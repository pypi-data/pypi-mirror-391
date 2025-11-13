from __future__ import annotations

import os
import ast
import zipfile
import datetime
import traceback
from typing import TYPE_CHECKING, Union

import yaml
from edgefirst_client import Client

from edgefirst.validator.datasets import instantiate_dataset
from edgefirst.validator.datasets.utils.fetch import (classify_dataset,
                                                      download_file)
from edgefirst.validator.datasets.utils.readers import (read_labels_file,
                                                        read_yaml_file)
from edgefirst.validator.publishers.utils.logger import (logger,
                                                         set_symbol_condition)
from edgefirst.validator.runners import (TFliteRunner, ONNXRunner, KerasRunner,
                                         TensorRTRunner, OfflineRunner,
                                         DeepViewRTRunner)
from edgefirst.validator.evaluators import (CombinedParameters, CommonParameters,
                                            ModelParameters, DatasetParameters,
                                            ValidationParameters)
from edgefirst.validator.evaluators import (YOLOValidator, EdgeFirstValidator,
                                            YOLOSegmentationValidator,
                                            SegmentationValidator,
                                            PoseValidator, MultitaskValidator,
                                            StudioProgress)
from edgefirst.validator.publishers import StudioPublisher
from edgefirst.validator.datasets import StudioCache

if TYPE_CHECKING:
    from edgefirst.validator.runners import Runner
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.evaluators import Evaluator


def build_parameters(args) -> CombinedParameters:
    """
    Store command line arguments inside the `Parameters` object.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    CombinedParameters
        This object is a container for both the model
        and validation parameters set from the command line.
    """
    # Time of validation
    today = datetime.datetime.now().strftime(
        '%Y-%m-%d--%H:%M:%S').replace(":", "_")
    tensorboard, visualize, json_out = None, None, None
    if args.visualize:
        visualize = os.path.join(
            args.visualize,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}")
    elif args.tensorboard:
        tensorboard = os.path.join(
            args.tensorboard,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}"
        )

    json_out = args.json_out
    if args.session_id is not None:
        if json_out is None:
            json_out = "apex_charts"

    if json_out:
        json_out = os.path.join(
            json_out,
            f"{os.path.basename(os.path.normpath(args.model))}_{today}"
        )

    model_metadata = get_model_metadata(args)
    # Validate with the model metadata parameters.
    # By default in the command line override is set to True to use
    # the command line parameters. Otherwise in EdgeFirst Studio, override
    # is set to False to use model meta parameters.
    if not args.override and model_metadata is not None:
        args.nms_score_threshold = model_metadata.get("validation", {})\
                                                 .get("score",
                                                      args.nms_score_threshold)
        args.nms_iou_threshold = model_metadata.get("validation", {})\
                                               .get("iou",
                                                    args.nms_iou_threshold)
        args.norm = model_metadata.get("validation", {})\
                                  .get("normalization", args.norm)
        args.preprocessing = model_metadata.get("validation", {})\
                                           .get("preprocessing",
                                                args.preprocessing)

    common_parameters = CommonParameters(
        norm=args.norm,
        preprocessing=args.preprocessing,
        method=args.method
    )

    model_parameters = ModelParameters(
        common_parameters=common_parameters,
        model_path=args.model,
        iou_threshold=args.nms_iou_threshold,
        score_threshold=args.nms_score_threshold,
        max_detections=args.max_detections,
        engine=args.engine,
        nms=args.nms,
        box_format=args.box_format,
        warmup=args.warmup,
        labels_path=args.model_labels,
        label_offset=args.label_offset,
    )
    model_parameters.metadata = model_metadata

    dataset_parameters = DatasetParameters(
        common_parameters=common_parameters,
        dataset_path=args.dataset,
        local_reader=args.suppress_local_reader,
        show_missing_annotations=args.show_missing_annotations,
        normalized=args.absolute_annotations,
        box_format=args.annotation_format,
        labels_path=args.dataset_labels,
        label_offset=args.gt_label_offset,
    )

    validation_parameters = ValidationParameters(
        validate_type=args.validate,
        method=args.method,
        iou_threshold=args.validation_iou,
        score_threshold=args.validation_score,
        metric=args.metric,
        matching_leniency=args.matching_leniency,
        clamp_boxes=args.clamp_boxes,
        ignore_boxes=args.ignore_boxes,
        display=args.display,
        visualize=visualize,
        tensorboard=tensorboard,
        json_out=json_out,
        include_background=args.include_background
    )

    parameters = CombinedParameters(
        model_parameters=model_parameters,
        dataset_parameters=dataset_parameters,
        validation_parameters=validation_parameters
    )
    return parameters


def build_dataset(
    args,
    parameters: DatasetParameters,
    client: Union[Client, None]
) -> Dataset:
    """
    Instantiate the Dataset Reader.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: DatasetParameters
        Contains the dataset parameters set from the command line.
    client: Client
        The EdgeFirst Client object.

    Returns
    -------
    Dataset
        This can be any dataset reader such as a DarkNetDataset,
        TFRecordDataset, etc. depending on the dataset format that
        was passed specified.
    """
    studio_cache = None
    if args.session_id is not None:
        # Avoid the default dataset path for studio validation.
        if args.dataset == "samples/coco128.yaml":
            args.dataset = "dataset"
            parameters.dataset_path = args.dataset

        if parameters.labels_path and os.path.exists(parameters.labels_path):
            parameters.labels = read_labels_file(parameters.labels_path)

        # Download the dataset if it doesn't exist.
        studio_cache = StudioCache(
            parameters=parameters,
            client=client,
            session_id=args.session_id
        )

        # Download the dataset if it doesn't exist.
        if not (os.path.exists(args.dataset) and os.listdir(args.dataset)):
            logger("The dataset does not exist. " +
                   f"Attempting to download the dataset to '{args.dataset}'",
                   code="INFO")
            studio_cache.download(args.dataset)

        # Use the cache if specified, otherwise cache the dataset.
        if args.cache is not None:
            parameters.common.cache = True
            # Cache the dataset if the cache doesn't exist.
            if not os.path.exists(args.cache):
                logger("The dataset cache does not exist. " +
                       f"Attempting to cache existing dataset to {args.cache}",
                       code="INFO")
                studio_cache.cache(args.dataset, args.cache)
            parameters.dataset_path = args.cache

    # Determine the dataset type.
    info_dataset = classify_dataset(
        source=parameters.dataset_path,
        labels_path=parameters.labels_path,
        local=parameters.local_reader
    )

    # Build the dataset class depending on the type.
    dataset = instantiate_dataset(
        info_dataset=info_dataset,
        parameters=parameters,
    )

    # Transfer the cache timings to the dataset object.
    if studio_cache is not None:
        if studio_cache.edgefirst_dataset is not None:
            dataset.load_timings = \
                studio_cache.edgefirst_dataset.load_timings
            dataset.read_timings = \
                studio_cache.edgefirst_dataset.read_timings
    return dataset


def build_runner(parameters: ModelParameters) -> Runner:
    """
    Instantiate the model runners.

    Parameters
    ----------
    parameters: ModelParameters
        Contains the model parameters set from the command line.

    Returns
    -------
    Runner
        This can be any model runner depending on the model passed
        such as ONNX, TFLite, Keras, RTM, etc.

    Raises
    ------
    NotImplementedError
        Certain runner implementations are not yet implemented.
    """
    if (not os.path.exists(parameters.model_path) and
            parameters.model_path == "yolov5s.onnx"):
        download_file(
            url="https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.onnx",
            download_path=os.path.join(os.getcwd(), "yolov5s.onnx")
        )

    # KERAS
    if os.path.splitext(parameters.model_path)[1].lower() in [".h5", ".keras"]:
        runner = KerasRunner(parameters.model_path, parameters=parameters)
    # TFLITE
    elif os.path.splitext(parameters.model_path)[1].lower() == ".tflite":
        runner = TFliteRunner(parameters.model_path, parameters=parameters)
    # ONNX
    elif os.path.splitext(parameters.model_path)[1].lower() == ".onnx":
        runner = ONNXRunner(parameters.model_path, parameters=parameters)
    # TENSORRT
    elif os.path.splitext(parameters.model_path)[1].lower() in [".engine", ".trt"]:
        runner = TensorRTRunner(parameters.model_path, parameters=parameters)
    # HAILO
    elif os.path.splitext(parameters.model_path)[1].lower() == ".hef":
        raise NotImplementedError(
            "Running Hailo models is not implemented.")
    # DEEPVIEWRT EVALUATION
    elif os.path.splitext(parameters.model_path)[1].lower() == ".rtm":
        runner = DeepViewRTRunner(
            model=parameters.model_path,
            parameters=parameters
        )
    # OFFLINE (TEXT FILES) or SAVED MODEL Directory
    elif os.path.splitext(parameters.model_path)[1].lower() == "":
        runner = find_keras_pb_model(parameters)

        if runner is None:
            logger("Model extension does not exist, running offline validation.",
                   code='INFO')

            runner = OfflineRunner(
                annotation_source=parameters.model_path,
                parameters=parameters
            )
    else:
        raise NotImplementedError(
            "Running the model '{}' is currently not supported".format(
                parameters.model_path)
        )
    return runner


def build_evaluator(
        args, parameters: CombinedParameters, client: Client) -> Evaluator:
    """
    Intantiate the evaluator object depending on the task.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: CombinedParameters
        This object is a container for both model, dataset, and validation
        parameters set from the command line.
    client: Client
        The EdgeFirst Client object.

    Returns
    -------
    Evaluator
        This can be any evaluator object depending on the task such
        as segmentation, detection, multitask, or pose.

    Raises
    ------
    ValueError
        Dataset labels were not found.
    NotImplementedError
        Certain validation types are not yet implemented.
    """
    runner = build_runner(parameters.model)
    dataset = build_dataset(args, parameters=parameters.dataset, client=client)

    if parameters.dataset.labels is None or len(
            parameters.dataset.labels) == 0:
        raise ValueError(
            "The unique set of string labels from the dataset was not found.")

    # DeepViewRT models might already contain the labels from the context.
    if parameters.model.labels is None or len(parameters.model.labels) == 0:
        parameters.model.labels = get_model_labels(args, parameters.dataset)

    """
    Instantiate evaluators
    """
    if parameters.validation.validate_type == "vision":
        # Multitask Validation
        if parameters.model.common.with_boxes and parameters.model.common.with_masks:
            if parameters.validation.method in ["ultralytics", "yolov7"]:
                # Ultralytics segmentation models are always multitask models.
                evaluator = YOLOSegmentationValidator(
                    parameters=parameters,
                    runner=runner,
                    dataset=dataset
                )
            else:
                evaluator = MultitaskValidator(
                    parameters=parameters,
                    runner=runner,
                    dataset=dataset
                )
        # Segmentation Validation
        elif parameters.model.common.with_masks:
            # Semantic Segmentation models from ModelPack are validated using EdgeFirst
            parameters.model.common.method = "edgefirst"
            parameters.validation.method = "edgefirst"
            evaluator = SegmentationValidator(
                parameters=parameters,
                runner=runner,
                dataset=dataset
            )
        # Detection Validation
        elif parameters.model.common.with_boxes:
            if parameters.validation.method in ["ultralytics", "yolov7"]:
                evaluator = YOLOValidator(
                    parameters=parameters,
                    runner=runner,
                    dataset=dataset
                )
            else:
                evaluator = EdgeFirstValidator(
                    parameters=parameters,
                    runner=runner,
                    dataset=dataset
                )
        else:
            raise RuntimeError(
                "Both values for `with_boxes` and `with_masks` were set to False.")

    # Pose Validation
    elif parameters.validation.validate_type == "pose":
        evaluator = PoseValidator(
            parameters=parameters,
            runner=runner,
            dataset=dataset
        )

    else:
        raise NotImplementedError(
            "The validation process for {} is currently not supported".format(
                parameters.validation.validate_type
            ))
    return evaluator


def find_keras_pb_model(
        parameters: ModelParameters) -> Union[KerasRunner, None]:
    """
    Instantiate Keras runners based on pb model extension.

    Parameters
    ----------
    parameters: Parameters
        These are the model parameters loaded by the command line.

    Returns
    -------
    Union[KerasRunner, None]
        If 'keras_metadata.pb' or 'saved_model.pb' files exists, then
        the KerasRunner is instantiated. This is the runner object for
        deploying Keras models for inference. Otherwise, None is returned.
    """
    runner = None
    for root, _, files in os.walk(parameters.model_path):
        for file in files:
            if (os.path.basename(file) == "keras_metadata.pb" or
                    os.path.basename(file) == "saved_model.pb"):
                runner = KerasRunner(
                    model=root,
                    parameters=parameters
                )
                break
    return runner


def get_model_labels(args, parameters: DatasetParameters) -> list:
    """
    Fetch the labels associated to the model.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    parameters: DatasetParameters
        The dataset parameters set from the command line.

    Returns
    -------
    list
        The list of model labels.
    """
    model_labels = parameters.labels

    arg_labels, embedded_labels = [], []
    if args.model_labels and os.path.exists(args.model_labels):
        arg_labels = read_labels_file(args.model_labels)
        model_labels = arg_labels

    if args.model.endswith('.tflite'):
        if zipfile.is_zipfile(args.model):
            with zipfile.ZipFile(args.model, 'r') as zip_ref:
                # Find the first .txt file inside the ZIP.
                txt_files = [name for name in zip_ref.namelist()
                             if name.lower().endswith('.txt')]
                if txt_files:
                    # Pick the first .txt file (or handle multiple if needed).
                    with zip_ref.open(txt_files[0]) as file:
                        content = file.read().decode('utf-8').strip()
                        try:
                            model_metadata = ast.literal_eval(content)
                            names = model_metadata.get("names", {})
                            embedded_labels = [name for name in names.values()]
                        except (ValueError, SyntaxError):
                            embedded_labels = [line
                                               for line in content.splitlines()
                                               if line not in ["\n", "", "\t"]]
                        model_labels = embedded_labels

    if len(arg_labels) and len(embedded_labels):
        if arg_labels != embedded_labels:
            logger("The contents of the specified --model-labels does not match " +
                   "the labels embedded in the model. Defaulting to the " +
                   "labels embedded in the model", code="WARNING")

    if not (len(arg_labels) or len(embedded_labels)):
        logger("Model labels was not specified. " +
               "Defaulting to use the dataset labels for the model.",
               code="WARNING")
    return model_labels


def get_model_metadata(args) -> Union[dict, None]:
    """
    Returns the model metadata for decoding the outputs.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    Union[dict, None]
        The model metadata if it exists. Otherwise None is returned.
    """
    if args.config is not None:
        return read_yaml_file(args.config)
    if zipfile.is_zipfile(args.model):
        with zipfile.ZipFile(args.model) as zip_ref:
            if "edgefirst.yaml" in zip_ref.namelist():
                file = "edgefirst.yaml"
            elif "config.yaml" in zip_ref.namelist():
                file = "config.yaml"
            else:
                return None
            with zip_ref.open(file) as f:
                yaml_text = f.read().decode("utf-8")
                metadata = yaml.safe_load(yaml_text)
                return metadata
    return None


def download_model_artifacts(args, client: Client):
    """
    Download model artifacts in EdgeFirst Studio.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    client: Client
        The EdgeFirst Studio client object to
        communicate with EdgeFirst Studio.
    """
    session = client.validation_session(session_id=args.session_id)

    train_session_id = session.training_session_id
    model = session.params["model"]

    logger(f"Downloading model artifacts from train session ID " +
           f"'t-{train_session_id.value:x}'.", code="INFO")

    # Do not auto-download the model, in case offline validation is specified.
    if not os.path.exists(args.model):
        model = str(model)
        if "String" in model:
            model = model.removeprefix("String(").removesuffix(")")
            
        try:
            client.download_artifact(
                training_session_id=train_session_id,
                modelname=model,
                filename=model
            )
        except RuntimeError as e:
            if "Status(404" in str(e):
                raise FileNotFoundError(f"The artifact '{model}' does not exist.")
            raise e
        args.model = os.path.join(os.path.dirname(args.model), model)

    if args.model_labels is None:
        args.model_labels = "labels.txt"

    if args.config is None:
        args.config = "edgefirst.yaml"

    try:
        client.download_artifact(
            training_session_id=train_session_id,
            modelname=args.model_labels,
            filename=args.model_labels
        )
    except RuntimeError as e:
        if "Status(404" in str(e):
            raise FileNotFoundError("The artifact 'labels.txt' does not exist.")
        raise e

    try:
        client.download_artifact(
            training_session_id=train_session_id,
            modelname=args.config,
            filename=args.config
        )
    except RuntimeError as e:
        if "Status(404" in str(e):
            raise FileNotFoundError("The artifact 'edgefirst.yaml' does not exist.")
        raise e


def update_parameters(args, client: Client):
    """
    Updates the parameters specified by EdgeFirst Studio.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.
    client: Client
        The EdgeFirst Client object.
    """
    session = client.validation_session(args.session_id)

    args.method = session.params.get("method", args.method)
    args.override = "override" in session.params.keys()
    args.nms_score_threshold = session.params.get("nms_score_threshold",
                                                  args.nms_score_threshold)
    args.nms_iou_threshold = session.params.get("nms_iou_threshold",
                                                args.nms_iou_threshold)


def initialize_studio_client(args) -> Union[Client, None]:
    """
    Initialize the EdgeFirst Client if the validation session ID is set.
    Downloads the model artifacts if it doesn't exist.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments.

    Returns
    -------
    Union[Client, None]
        The EdgeFirst client object is a bridge of communication between
        EdgeFirst Studio and the applications. Otherwise None is
        returned if the validation session ID is not specified.
    """
    client = None
    if args.session_id is not None:
        if args.session_id.isdigit():
            args.session_id = int(args.session_id)
        logger(f"Detected EdgeFirst Studio validation ID: '{args.session_id}'.",
               code="INFO")

        try:
            client = Client(
                token=args.token,
                username=args.username,
                password=args.password,
                server=args.server
            )
        except RuntimeError as e:
            if "MaxRetries" in str(e):
                raise ValueError(
                    f"Got an invalid server: {args.server}. " +
                    "Check that the right server is set.")
            raise e
    return client


def validate(args):
    """
    Instantiates the runners and readers to deploy the model for validation.

    Parameters
    ----------
    args: argsparse.NameSpace
        The command line arguments set.
    """
    set_symbol_condition(args.exclude_symbols)

    client = initialize_studio_client(args)
    studio_publisher = None

    if client is not None:
        studio_publisher = StudioPublisher(
            json_path=args.json_out,
            session_id=args.session_id,
            client=client
        )

    try:
        if studio_publisher is not None:
            stages = [
                ("fetch_img", "Downloading Images"),
                ("fetch_as", "Downloading Annotations"),
                ("validate", "Running Validation"),
            ]
            session = client.validation_session(session_id=args.session_id)
            client.set_stages(session.task.id, stages)

            download_model_artifacts(args, client=client)
            # Update parameters set from the validation session in studio.
            update_parameters(args=args, client=client)

            parameters = build_parameters(args)
            studio_publisher.json_path = parameters.validation.json_out
        else:
            parameters = build_parameters(args)
        evaluator = build_evaluator(args, parameters=parameters, client=client)
    except Exception as e:
        if studio_publisher is not None:
            studio_publisher.update_stage(
                stage="validate",
                status="error",
                message=str(e),
                percentage=0
            )
        error = traceback.format_exc()
        print(error)
        raise e

    if args.session_id is not None:
        studio_progress = StudioProgress(
            evaluator=evaluator,
            studio_publisher=studio_publisher
        )
        studio_progress.group_evaluation()
    else:
        evaluator.group_evaluation()
