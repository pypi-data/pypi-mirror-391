from typing import List


class Parameters:
    """
    Parent parameters to contain common parameters between
    the model, dataset, and validation.

    Parameters
    ----------
    labels_path: str
        The path to the labels.txt file containing unique string labels
        from the model or the dataset.
    labels: list
        A list of unique string labels which is part of the model artifacts
        for converting model output indices into strings.
    label_offset: int
        This is the offset to map the integer labels to string labels.
    box_format: str
        The output bounding box format of the model. Options could be one
        of the following: "pascalvoc" as (xmin, ymin, xmax, ymax),
        "coco" as (xmin, ymin, width, height), or "yolo" as (xc, yc, width, height).
    """

    def __init__(
        self,
        labels_path: str = None,
        labels: list = None,
        label_offset: int = 0,
        box_format: str = "pascalvoc",

    ):
        self.__labels_path = labels_path
        self.__labels = labels
        self.__label_offset = label_offset
        self.__box_format = box_format.lower()

    @property
    def labels_path(self) -> str:
        """
        Attribute to access the labels_path.
        This is the path to the labels.txt file. This contains unique string
        labels from either the dataset or the model.

        Returns
        -------
        str
            The path to the labels.txt file.
        """
        return self.__labels_path

    @labels_path.setter
    def labels_path(self, path: str):
        """
        Set the path to the labels.txt file.

        Parameters
        ----------
        path: str
            The path to the labels.txt file.
        """
        self.__labels_path = path

    @property
    def labels(self) -> List[str]:
        """
        Attribute to access the model labels.
        This is used for mapping the prediction integer indices to strings.

        Returns
        -------
        List[str]
            The list of unique string labels from the model.
        """
        return self.__labels

    @labels.setter
    def labels(self, this_labels: List[str]):
        """
        Sets the string labels for mapping the integer indices to
        string representations.

        Parameters
        ----------
        this_labels: List[str]
            The labels to set.
        """
        self.__labels = this_labels

    @property
    def label_offset(self) -> int:
        """
        Attribute to access the label offset for the predictions.
        This is used for mapping the prediction integer labels to strings.

        Returns
        -------
        int
            The label offset to map integer indices to string representations.
        """
        return self.__label_offset

    @label_offset.setter
    def label_offset(self, this_label_offset: int):
        """
        Sets the label offset for mapping the integer indices to
        string representations.

        Parameters
        ----------
        this_label_offset: int
            The label_offset to set.
        """
        self.__label_offset = this_label_offset

    @property
    def box_format(self) -> str:
        """
        Attribute to access the box format.
        The box format can either be: "xyxy", "xywh", "yxyx"

        Returns
        -------
        str
            The box format type.
        """
        return self.__box_format

    @box_format.setter
    def box_format(self, this_box_format: str):
        """
        Sets the box format type.

        Parameters
        ----------
        this_box_format: str
            The box format to set.
        """
        if this_box_format not in ['yolo', 'pascalvoc', 'coco']:
            raise ValueError(
                f"Unsupported box format provided: {this_box_format}")
        self.__box_format = this_box_format.lower()


class CommonParameters:
    """
    Parameters that are common between all three parameter types
    where each of these parameters should remain consistent across
    the model, dataset, and validation.

    Parameters
    ----------
    with_boxes: bool
        The condition of whether or not the dataset and the model both provide
        bounding box detections.
    with_masks: bool
        The condition of whether or not the dataset and the model both provide
        segmentation mask detections.
    norm: str
        The type of image normalization to match the model input requirements.
        Options could be one of the following: "raw", "unsigned", "signed",
        "imagenet", or "whitening".
    preprocessing: str
        The type of image preprocessing to apply to the image prior to model
        inference. Options could be one of the following: "letterbox", "pad",
        "resize".
    method: str
        Reproducing validation results reported by Ultralytics by default. Specify
        validation method seen in other sources such as YOLOv7. Options could
        be "ultralytics" for the official validator from Ultralytics which
        supports YOLOv5, YOLOv8, and YOLOv11. However, there are variations
        such as "yolov7" for YOLOv7 and "edgefirst" for internal Au-Zone implementations.
    cache: bool
        Specify to cache the dataset which preprocesses images with resizing,
        letterbox, or padding transformations and other specifications such as
        to YUYV or RGBA and stores these transformed assets inside an LMDB cache.
        Defaults to False, but if this is True, the preprocessing steps
        in the Runner will be skipped as it is already done in the dataset.
    shape: tuple
        Specify the input shape of the model.
    dtype: str
        The input data type of the model.
    """

    def __init__(
        self,
        with_boxes: bool = True,
        with_masks: bool = True,
        norm: str = "raw",
        preprocessing: str = "letterbox",
        method: str = "ultralytics",
        cache: bool = False,
        shape: tuple = None,
        dtype: str = "float32",
    ):

        self.__with_boxes = with_boxes
        self.__with_masks = with_masks
        self.__norm = norm.lower()
        self.__preprocessing = preprocessing.lower()
        self.__method = method.lower()
        self.__cache = cache
        self.__shape = shape
        self.__dtype = dtype
        self.__semantic = False

    @property
    def with_boxes(self) -> bool:
        """
        Attribute to access with_boxes.
        Specify whether the model or the dataset provides
        bounding box annotations.

        Returns
        -------
        bool
            Condition for object detection (bounding box) validation.
        """
        return self.__with_boxes

    @with_boxes.setter
    def with_boxes(self, boxes: bool):
        """
        Specify condition for object detection (bounding box) validation.

        Parameters
        ----------
        boxes: bool
            The condition to set.
        """
        self.__with_boxes = boxes

    @property
    def with_masks(self) -> bool:
        """
        Attribute to access with_masks.
        Specify whether the model or the dataset provides
        segmentation annotations.

        Returns
        -------
        bool
            Condition for segmentation validation.
        """
        return self.__with_masks

    @with_masks.setter
    def with_masks(self, masks: bool):
        """
        Specify condition for segmentation validation.

        Parameters
        ----------
        masks: bool
            The condition to set.
        """
        self.__with_masks = masks

    @property
    def norm(self) -> str:
        """
        Attribute to access the image normalization type.
        Typically quantized models use "raw" and floating point models
        use "unsigned" or "signed".

        Returns
        -------
        str
            The image normalization type.
        """
        return self.__norm

    @norm.setter
    def norm(self, this_norm: str):
        """
        Sets the image normalization type.

        Parameters
        ----------
        this_norm: str
            The image normalization to set.
        """
        self.__norm = this_norm.lower() if this_norm is not None else this_norm

    @property
    def preprocessing(self) -> str:
        """
        Attribute to access the type of image preprocessing to perform.
        Options can be "letterbox", "pad", or "resize".

        Returns
        -------
        str
            The type of image preprocessing to perform.
        """
        return self.__preprocessing

    @preprocessing.setter
    def preprocessing(self, preprocess: str):
        """
        Sets the type of image preprocessing to perform.

        Parameters
        ----------
        preprocess: str
            The type of image preprocessing to set. Options include
            "letterbox", "pad", or "resize".
        """
        self.__preprocessing = preprocess.lower() if preprocess is not None else preprocess

    @property
    def method(self) -> str:
        """
        Attribute to access validation methods.
        Specifies the validation method to
        reproduce in EdgeFirst Validator. By default the "ultralytics" methods
        seen in YOLOv5, YOLOv8, and YOLOv11 are used. However, other variations
        such as "yolov7" from YOLOv7 and "edgefirst" for internal Au-Zone
        implementations are also possible.

        Returns
        -------
        bool
            The type of method for validation.
        """
        return self.__method

    @method.setter
    def method(self, methods: str):
        """
        Sets the validation method.

        Parameters
        ----------
        methods: str
            The validation method to reproduce.
            Options include "ultralytics", "yolov7", or "edgefirst".
        """
        self.__method = methods.lower() if methods is not None else methods

    @property
    def cache(self) -> bool:
        """
        Attribute to access the cache condition.
        This specifies whether or not to cache the dataset. Caching
        the dataset includes preprocessing the images and annotations
        to run only once during the validation sessions to speed up the process.

        Returns
        -------
        bool
            Condition to cache the dataset.
        """
        return self.__cache

    @cache.setter
    def cache(self, to_cache: bool):
        """
        Sets the caching condition.

        Parameters
        ----------
        to_cache: bool
            The condition for cache to set.
        """
        self.__cache = to_cache

    @property
    def shape(self) -> tuple:
        """
        Attribute to access the model's input shape.

        Returns
        --------
        tuple
            The input shape of the model.
        """
        return self.__shape

    @shape.setter
    def shape(self, size: tuple):
        """
        Sets the input shape of the model.

        Parameters
        ----------
        size: tuple
            The model input shape to set.
        """
        self.__shape = size

    @property
    def dtype(self) -> str:
        """
        Attribute to access the model dtype.
        By default this is set to "float32". However, possible
        variations include "float16", "int8", "uint8", etc.

        Returns
        -------
        str
            The model datatype
        """
        return self.__dtype

    @dtype.setter
    def dtype(self, this_dtype: str):
        """
        Sets the model data type.

        Parameters
        ----------
        this_dtype: str
            The model data type to set.
        """
        self.__dtype = this_dtype

    @property
    def semantic(self) -> bool:
        """
        Attribute to access the semantic condition.

        Returns
        -------
        bool
            Specify to True if the model is a semantic segmentation
            model as seen in ModelPack. Otherwise False for instance
            segmentation as seen in Ultralytics.
        """
        return self.__semantic

    @semantic.setter
    def semantic(self, condition: bool):
        """
        Sets the specification if the model being validated
        is semantic segmentation (True) or instance segmentation (False).

        Parameters
        ----------
        condition: bool
            Specify the semantic condition.
        """
        self.__semantic = condition
