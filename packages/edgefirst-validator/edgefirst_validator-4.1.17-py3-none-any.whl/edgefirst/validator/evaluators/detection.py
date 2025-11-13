from __future__ import annotations

import os
from typing import TYPE_CHECKING, List

import numpy as np
import matplotlib.figure

from edgefirst.validator.metrics.utils.math import batch_iou
from edgefirst.validator.visualize.utils.plots import (figure2numpy,
                                                       plot_pr_curve,
                                                       plot_mc_curve,
                                                       plot_score_histogram,
                                                       plot_confusion_matrix,
                                                       plot_classification_detection)
from edgefirst.validator.datasets.utils.transformations import (scale,
                                                                clamp_boxes,
                                                                ignore_boxes)
from edgefirst.validator.visualize import DetectionDrawer
from edgefirst.validator.datasets import DetectionInstance
from edgefirst.validator.visualize.utils.plots import ConfusionMatrix
from edgefirst.validator.runners import (OfflineRunner, DeepViewRTRunner)
from edgefirst.validator.evaluators import Evaluator, Matcher, DetectionClassifier
from edgefirst.validator.metrics import YOLOStats, DetectionStats, DetectionMetrics

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.runners import Runner


class YOLOValidator(Evaluator):
    """
    Reproduce the validation methods implemented in Ultralytics and other
    variations such as YOLOv7 for detection. Reproduces the metrics in
    Ultralytics to allow comparable metrics between EdgeFirst models
    and Ultralytics models.

    Parameters
    ----------
    parameters: CombinedParameters
        This is a container for the model, dataset, and validation parameters
        set from the command line.
    runner: Runner
        A type of model runner object responsible for running the model
        for inference provided with an input image to produce bounding boxes.
    dataset: Dataset
        A type of dataset object responsible for reading different types
        of datasets such as Darknet, TFRecords, or EdgeFirst Datasets.
    """

    def __init__(
        self,
        parameters: CombinedParameters,
        runner: Runner = None,
        dataset: Dataset = None,
    ):
        super(YOLOValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        self.detection_stats = YOLOStats()
        self.confusion_matrix = ConfusionMatrix(
            nc=len(self.parameters.dataset.labels),
            iou_thres=self.parameters.validation.iou_threshold,
            offset=int(not any(s.lower() == "background"
                               for s in self.parameters.dataset.labels))
        )
        self.metrics = DetectionMetrics(
            parameters=self.parameters.validation,
            detection_stats=self.detection_stats,
            model_name=self.model_name,
            dataset_name=self.dataset_name,
            save_path=self.save_path,
            labels=self.parameters.dataset.labels
        )
        self.metrics.plots.initialize_confusion_matrix()
        self.drawer = DetectionDrawer()
        self.matcher = None

    def instance_collector(self):
        """
        Collects the instances from the ground truth and runs
        model inference on a single image to collect the instance for
        the model predictions.

        Yields
        ------
        dict
            This yields one image instance from the ground truth
            and model predictions with keys "gt_instance" and "dt_instance".
        """

        gt_instance: DetectionInstance
        for gt_instance in self.dataset.read_all_samples(
            silent=self.parameters.validation.silent
        ):
            if isinstance(self.runner, (OfflineRunner, DeepViewRTRunner)):
                detections = self.runner.run_single_instance(
                    image=gt_instance.image_path,
                    image_shape=[gt_instance.height, gt_instance.width]
                )
            else:
                detections = self.runner.run_single_instance(
                    image=gt_instance.image,
                    shapes=gt_instance.shapes,
                    ratio=gt_instance.ratio,
                    image_shape=gt_instance.image_shape
                )
                # Visualize the image with transformations.
                gt_instance.image = self.runner.image

            # Storing the shapes of the image passed for inference.
            # This is used for box rescaling due to letterbox transformations.
            if self.parameters.dataset.common.cache:
                shapes = gt_instance.shapes
            else:
                shapes = self.runner.shapes

            gt_instance.shapes = shapes
            gt_instance.image_shape = (self.runner.image_shape if
                                       self.runner.image_shape is not None else
                                       (gt_instance.height, gt_instance.width))
            self.create_labelsn(gt_instance)

            if detections is None:
                yield {
                    "gt_instance": gt_instance,
                    "dt_instance": None
                }

            dt_instance = DetectionInstance(gt_instance.image_path)
            boxes, labels, scores = detections
            dt_instance.height = gt_instance.height
            dt_instance.width = gt_instance.width
            dt_instance.boxes = boxes
            dt_instance.labels = labels
            dt_instance.scores = scores
            dt_instance.shapes = shapes
            dt_instance.image_shape = gt_instance.image_shape

            self.create_predn(dt_instance)

            yield {
                "gt_instance": gt_instance,
                "dt_instance": dt_instance,
            }

    def create_predn(self, dt_instance: DetectionInstance):
        """
        Apply validation filters and prepare prediction bounding box
        coordinates for image visualization and evaluations.

        Parameters
        ----------
        dt_instance: DetectionInstance
            The model detections container of the bounding boxes, labels,
            and scores for a single image/sample.
        """
        if self.parameters.validation.ignore_boxes:
            boxes, labels, scores = ignore_boxes(
                ignore=self.parameters.validation.ignore_boxes,
                boxes=dt_instance.boxes,
                labels=dt_instance.labels,
                scores=dt_instance.scores,
                shape=(dt_instance.height, dt_instance.width)
            )
            dt_instance.boxes = boxes
            dt_instance.labels = labels
            dt_instance.scores = scores
        if self.parameters.validation.clamp_boxes:
            dt_instance.boxes = clamp_boxes(
                boxes=dt_instance.boxes,
                clamp=self.parameters.validation.clamp_boxes,
                shape=(dt_instance.height, dt_instance.width)
            )

        # Prediction bounding boxes are already centered around objects
        # in images with letterbox, padding, or resize transformations.
        # This operation will only denormalize the bounding box coordinates.
        if len(dt_instance.boxes) and dt_instance.shapes is not None:
            input_shape = dt_instance.shapes[0][0]
            dt_instance.boxes *= np.array([input_shape[1],
                                           input_shape[0],
                                           input_shape[1],
                                           input_shape[0]])

        # If the model and dataset labels are not equal, it is required
        # to map the indices properly to match the ground truth and the
        # detections.
        if self.parameters.model.labels != self.parameters.dataset.labels:
            try:
                dt_instance.labels = np.array([
                    self.parameters.dataset.labels.index(
                        self.parameters.model.labels[int(cls)])
                    if self.parameters.model.labels[int(cls)]
                    in self.parameters.dataset.labels else cls for cls in
                    dt_instance.labels])
            except IndexError:
                raise IndexError("Model index out of range. " +
                                 "Try specifying the path to the model's " +
                                 "labels via `--model-labels <path to labels.txt>`.")

    def create_labelsn(self, gt_instance: DetectionInstance):
        """
        Apply validation filters and prepare ground truth bounding box
        coordinates for image visualization with letterbox,
        padding, and resize transformations, and evaluations.

        Parameters
        ----------
        gt_instance: DetectionInstance
            The ground truth container for the bounding boxes, labels
            for a single image instance.
        """

        if self.parameters.validation.ignore_boxes:
            boxes, labels, scores = ignore_boxes(
                ignore=self.parameters.validation.ignore_boxes,
                boxes=gt_instance.boxes,
                labels=gt_instance.labels,
                scores=gt_instance.scores,
                shape=(gt_instance.height, gt_instance.width)
            )
            gt_instance.boxes = boxes
            gt_instance.labels = labels
            gt_instance.scores = scores
        if self.parameters.validation.clamp_boxes:
            gt_instance.boxes = clamp_boxes(
                boxes=gt_instance.boxes,
                clamp=self.parameters.validation.clamp_boxes,
                shape=(gt_instance.height, gt_instance.width)
            )

        if len(gt_instance.boxes) and gt_instance.shapes is not None:
            shapes, label_ratio = gt_instance.shapes
            input_shape = shapes[0]

            # Scale ground truth coordinates to center around objects
            # in an image with letterbox transformation.
            if self.parameters.model.common.preprocessing == "letterbox":
                ratio = shapes[1][0]
                pad = shapes[1][1]

                gt_instance.boxes = scale(
                    boxes=gt_instance.boxes,
                    w=label_ratio[1] * ratio[1] * gt_instance.width,
                    h=label_ratio[0] * ratio[0] * gt_instance.height,
                    padw=pad[0],
                    padh=pad[1],
                )
            # Scale ground truth coordinates to center around objects
            # in an image with padding transformation.
            elif (self.parameters.model.common.preprocessing == "pad"
                  and gt_instance.shapes is not None):

                gt_instance.boxes = scale(
                    boxes=gt_instance.boxes,
                    w=label_ratio[1] * gt_instance.width,
                    h=label_ratio[0] * gt_instance.height,
                )
            # Scale ground truth coordinates to center around objects
            # in an image with resize transformation.
            else:
                # Denormalize boxes
                gt_instance.boxes *= np.array([input_shape[1],
                                               input_shape[0],
                                               input_shape[1],
                                               input_shape[0]])

    def match_predictions(
        self,
        pred_classes: np.ndarray,
        true_classes: np.ndarray,
        iou: np.ndarray
    ) -> np.ndarray:
        """
        Match predictions to ground truth using IoU.
        Function implementation was taken from Ultralytics::
        https://github.com/ultralytics/ultralytics/blob/main/ultralytics/engine/validator.py#L251

        Parameters
        ----------
        pred_classes: np.ndarray
            Predicted class indices of shape (N,).
        true_classes: np.ndarray
            Target class indices of shape (M,).
        iou: np.ndarray
            An NxM tensor containing the pairwise IoU
            values for predictions and ground truth.

        Returns
        -------
        np.ndarray
            Correct tensor of shape (N, 10) for 10 IoU thresholds.
        """
        correct = np.zeros(
            (pred_classes.shape[0], self.detection_stats.ious.shape[0]),
            dtype=bool
        )

        correct_class = (true_classes[:, None] == pred_classes).astype(
            np.float32)  # shape (N, M)
        iou = iou * correct_class

        for i, threshold in enumerate(self.detection_stats.ious):
            # IoU > threshold and classes match
            matches = np.nonzero(iou >= threshold)
            matches = np.array(matches).T
            if matches.shape[0]:
                if matches.shape[0] > 1:
                    matches = matches[iou[matches[:, 0],
                                          matches[:, 1]].argsort()[::-1]]
                    matches = matches[np.unique(
                        matches[:, 1], return_index=True)[1]]
                    matches = matches[np.unique(
                        matches[:, 0], return_index=True)[1]]
                correct[matches[:, 1].astype(int), i] = True
        return correct

    def process_batch_v5(
        self,
        dt_instance: DetectionInstance,
        gt_instance: DetectionInstance
    ) -> np.ndarray:
        """
        Return the correct prediction matrix. Function implementation was taken
        from YOLOv5: https://github.com/ultralytics/yolov5/blob/master/val.py#L94.

        Parameters
        -----------
        dt_instance: DetectionInstance
            A prediction instance container of the boxes, labels, and scores.
        gt_instance: DetectionInstance
            A ground truth instance container of the boxes and the labels.

        Returns
        -------
        np.ndarray
            (array[n, 10]) where n denotes the classes for 10 IoU levels. This
            is a true positive array.
        """
        iou = batch_iou(gt_instance.boxes, dt_instance.boxes)
        return self.match_predictions(
            pred_classes=dt_instance.labels,
            true_classes=gt_instance.labels if len(
                gt_instance.boxes) else np.array([]),
            iou=iou
        )

    def process_batch_v7(
        self,
        dt_instance: DetectionInstance,
        gt_instance: DetectionInstance
    ) -> np.ndarray:
        """
        Return the correct prediction matrix. Function implementation was taken
        from YOLOv7: https://github.com/WongKinYiu/yolov7/blob/main/test.py#L179

        Parameters
        -----------
        dt_instance: DetectionInstance
            A prediction instance container of the boxes, labels, and scores.
        gt_instance: DetectionInstance
            A ground truth instance container of the boxes and the labels.

        Returns
        -------
        np.ndarray
            (array[N, 10]) where n denotes the classes for 10 IoU levels. This
            is a true positive array..
        """
        correct = np.zeros(
            (dt_instance.boxes.shape[0],
             self.detection_stats.ious.shape[0])).astype(bool)
        gt_labels = gt_instance.labels if len(
            gt_instance.boxes) else np.array([])
        detected = []  # target indices
        # Generate a similar format to YOLOv5 for visualization purposes.
        matches = []
        for cls in np.unique(gt_labels):
            ti = np.flatnonzero(cls == gt_labels)  # target indices
            # prediction indices
            pi = np.flatnonzero(cls == dt_instance.labels)

            # Search for detections
            if pi.shape[0]:
                ious = batch_iou(dt_instance.boxes[pi], gt_instance.boxes[ti])
                i = ious.argmax(1)
                ious = ious.max(axis=1)
                detected_set = set()
                for j in np.flatnonzero(ious > self.detection_stats.ious[0]):
                    d = ti[i[j]]  # detected target
                    # The ious[j] is always a tensor of 1 value.
                    matches.append([ti[i[j]], pi[j], ious[j]])
                    if d.item() not in detected_set:
                        detected_set.add(d.item())
                        detected.append(d)
                        # iou_thres is 1xn
                        correct[pi[j]] = ious[j] > self.detection_stats.ious
                        # all targets already located in image
                        if len(detected) == len(gt_instance.boxes):
                            break
        return correct

    def evaluate(self, instance: dict):
        """
        Run model evaluation using Ultralytics or YOLOv7 validation methods.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model prediction instances
            with keys "gt_instance", "dt_instance".
        """
        gt_instance: DetectionInstance = instance.get("gt_instance")
        dt_instance: DetectionInstance = instance.get("dt_instance")

        niou = len(self.detection_stats.ious)
        nl = len(gt_instance.labels)  # The number of ground truths.
        nd = len(dt_instance.labels)  # The number of predictions.
        tcls = gt_instance.labels.tolist() if nl else []  # target class.

        self.metrics.metrics.add_ground_truths(nl)
        self.metrics.metrics.add_predictions(nd)

        if nl:
            if nd == 0:
                if self.parameters.validation.plots:
                    self.confusion_matrix.process_batch(dt_instance=None,
                                                        gt_instance=gt_instance)
                self.detection_stats.stats["tp"].append(
                    np.zeros((0, niou), dtype=bool))
                self.detection_stats.stats["conf"].append(np.array([]))
                self.detection_stats.stats["pred_cls"].append(np.array([]))
                self.detection_stats.stats["target_cls"].append(tcls)
                return

            # Ultralytics method.
            if self.parameters.validation.method == "ultralytics":
                correct = self.process_batch_v5(dt_instance=dt_instance,
                                                gt_instance=gt_instance)
            # YOLOv7 method.
            elif self.parameters.validation.method == "yolov7":
                correct = self.process_batch_v7(dt_instance=dt_instance,
                                                gt_instance=gt_instance)

            if self.parameters.validation.plots:
                self.confusion_matrix.process_batch(dt_instance, gt_instance)
        else:
            correct = np.zeros((dt_instance.boxes.shape[0], niou)).astype(bool)

        if nd:
            self.detection_stats.stats["tp"].append(correct)
            self.detection_stats.stats["conf"].append(dt_instance.scores)
            self.detection_stats.stats["pred_cls"].append(dt_instance.labels)
            self.detection_stats.stats["target_cls"].append(tcls)
        else:
            self.detection_stats.stats["tp"].append(
                np.zeros((0, niou), dtype=bool))
            self.detection_stats.stats["conf"].append(np.array([]))
            self.detection_stats.stats["pred_cls"].append(np.array([]))
            self.detection_stats.stats["target_cls"].append(tcls)

    def visualize(
        self,
        gt_instance: DetectionInstance,
        dt_instance: DetectionInstance,
        epoch: int = 0
    ):
        """
        Draw bounding box results on the image and save the results in disk
        or publish into Tensorboard.

        Parameters
        ----------
        gt_instance: DetectionInstance
            This is the ground truth instance which contains bounding
            boxes and labels to draw.
        dt_instance: DetectionInstance
            This is the model detection instance which contains the
            bounding boxes, labels, and confidence scores to draw.
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        """
        image = self.drawer.draw_2d_bounding_boxes(
            gt_instance=gt_instance,
            dt_instance=dt_instance,
            matcher=self.matcher,
            validation_iou=self.parameters.validation.iou_threshold,
            validation_score=self.parameters.validation.score_threshold,
            method=self.parameters.validation.method,
            labels=self.parameters.dataset.labels
        )
        if self.parameters.validation.visualize:
            image.save(os.path.join(self.parameters.validation.visualize,
                                    os.path.basename(gt_instance.image_path)))
        elif self.tensorboard_writer:
            self.tensorboard_writer(
                np.asarray(image), gt_instance.image_path, step=epoch)

    def get_plots(self) -> List[matplotlib.figure.Figure]:
        """
        Reproduces the validation charts from Ultralytics.
        These plots are Matplotlib figures.

        Returns
        -------
        List[matplotlib.figure.Figure]
            This contains matplotlib figures of the plots.
        """
        fig_confusion_matrix = self.confusion_matrix.plot(
            names=self.metrics.plots.confusion_labels
        )
        fig_prec_rec_curve = plot_pr_curve(
            precision=self.metrics.plots.py,
            recall=self.metrics.plots.px,
            ap=self.metrics.plots.average_precision,
            names=self.parameters.dataset.labels,
            model=self.metrics.metrics.model,
            iou_threshold=self.parameters.validation.iou_threshold
        )
        fig_f1_curve = plot_mc_curve(
            px=self.metrics.plots.px,
            py=self.metrics.plots.f1,
            names=self.parameters.dataset.labels,
            model=self.metrics.metrics.model,
            ylabel='F1'
        )
        fig_prec_curve = plot_mc_curve(
            px=self.metrics.plots.px,
            py=self.metrics.plots.precision,
            names=self.parameters.dataset.labels,
            model=self.metrics.metrics.model,
            ylabel='Precision'
        )
        fig_rec_curve = plot_mc_curve(
            px=self.metrics.plots.px,
            py=self.metrics.plots.recall,
            names=self.parameters.dataset.labels,
            model=self.metrics.metrics.model,
            ylabel='Recall'
        )
        return [fig_confusion_matrix,
                fig_prec_rec_curve,
                fig_f1_curve,
                fig_prec_curve,
                fig_rec_curve]

    def save_plots(self, plots: List[matplotlib.figure.Figure]):
        """
        Saves the validation plots as image files in disk.

        Parameters
        ----------
        plots: List[matplotlib.figure.Figure]
            This is the list of matplotlib figures to save.
        """
        plots[0].savefig(
            f"{self.parameters.validation.visualize}/confusion_matrix.png",
            bbox_inches="tight")

        plots[1].savefig(
            f"{self.parameters.validation.visualize}/prec_rec_curve.png",
            bbox_inches="tight")
        plots[2].savefig(
            f"{self.parameters.validation.visualize}/F1_curve.png",
            bbox_inches="tight"
        )
        plots[3].savefig(
            f"{self.parameters.validation.visualize}/P_curve.png",
            bbox_inches="tight"
        )
        plots[4].savefig(
            f"{self.parameters.validation.visualize}/R_curve.png",
            bbox_inches="tight"
        )

    def publish_plots(
            self, plots: List[matplotlib.figure.Figure], epoch: int = 0):
        """
        Publishes the validation plots into Tensorboard.

        Parameters
        ----------
        plots: List[matplotlib.figure.Figure]
            This is the list of matplotlib figures to save.
        epoch: int
            The training epoch number used for ModelPack training usage.
        """
        nimage_confusion_matrix = figure2numpy(plots[0])
        nimage_precision_recall = figure2numpy(plots[1])
        nimage_f1 = figure2numpy(plots[2])
        nimage_prec = figure2numpy(plots[3])
        nimage_rec = figure2numpy(plots[4])

        self.tensorboard_writer(
            nimage_confusion_matrix,
            f"{self.metrics.metrics.model}_confusion_matrix.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_precision_recall,
            f"{self.metrics.metrics.model}_precision_recall.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_f1,
            f"{self.metrics.metrics.model}_F1_curve.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_prec,
            f"{self.metrics.metrics.model}_P_curve.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_rec,
            f"{self.metrics.metrics.model}_R_curve.png",
            step=epoch
        )


class EdgeFirstValidator(YOLOValidator):
    """
    Define the validation methods for EdgeFirst. Reproduces EdgeFirst matching
    and metrics for object detection.

    Parameters
    ----------
    parameters: CombinedParameters
        This is a container for the model, dataset, and validation parameters
        set from the command line.
    runner: Runner
        A type of model runner object responsible for running the model
        for inference provided with an input image to produce bounding boxes.
    dataset: Dataset
        A type of dataset object responsible for reading different types
        of datasets such as Darknet, TFRecords, or EdgeFirst Datasets.
    """

    def __init__(
        self,
        parameters: CombinedParameters,
        runner: Runner = None,
        dataset: Dataset = None,
    ):
        super(EdgeFirstValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        self.detection_stats = DetectionStats()
        self.matcher = Matcher(parameters=parameters.validation)
        self.metrics = DetectionMetrics(
            parameters=self.parameters.validation,
            detection_stats=self.detection_stats,
            model_name=self.model_name,
            dataset_name=self.dataset_name,
            save_path=self.save_path,
            labels=self.parameters.dataset.labels
        )
        self.classifier = DetectionClassifier(
            parameters=self.parameters.validation,
            detection_stats=self.detection_stats,
            matcher=self.matcher,
            plots=self.metrics.plots
        )
        self.metrics.plots.initialize_confusion_matrix()

    def evaluate(self, instance: dict):
        """
        Run model evaluation using EdgeFirst validation methods.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model predictions instances
            with keys "gt_instance" and "dt_instance".
        """
        gt_instance: DetectionInstance = instance.get("gt_instance")
        dt_instance: DetectionInstance = instance.get("dt_instance")

        self.detection_stats.capture_class(dt_instance.labels)
        self.detection_stats.capture_class(gt_instance.labels)

        self.metrics.metrics.add_ground_truths(len(gt_instance.labels))
        self.metrics.metrics.add_predictions(len(dt_instance.labels))

        self.matcher.match(
            gt_boxes=gt_instance.boxes,
            gt_labels=gt_instance.labels,
            dt_boxes=dt_instance.boxes,
            dt_labels=dt_instance.labels,
        )
        self.classifier.classify(
            gt_instance=gt_instance,
            dt_instance=dt_instance
        )

    def get_plots(self) -> List[matplotlib.figure.Figure]:
        """
        Generate EdgeFirst validation plots.

        Returns
        -------
        List[matplotlib.figure.Figure]
            This contains matplotlib figures of the plots.
        """
        fig_confusion_matrix = plot_confusion_matrix(
            confusion_data=self.metrics.plots.confusion_matrix,
            labels=self.metrics.plots.confusion_labels,
            model=self.metrics.metrics.model
        )
        fig_prec_rec_curve = plot_pr_curve(
            precision=self.metrics.plots.py,
            recall=self.metrics.plots.px,
            ap=self.metrics.plots.average_precision,
            names=self.parameters.dataset.labels,
            model=self.metrics.metrics.model,
            iou_threshold=self.parameters.validation.iou_threshold
        )
        fig_class_metrics = plot_classification_detection(
            class_histogram_data=self.metrics.plots.class_histogram_data,
            model=self.metrics.metrics.model,
        )
        fig_score_metrics = plot_score_histogram(
            tp_scores=np.concatenate(self.metrics.plots.tp_scores, axis=0),
            fp_scores=np.concatenate(self.metrics.plots.fp_scores, axis=0),
            model=self.metrics.metrics.model
        )
        return [fig_confusion_matrix, fig_prec_rec_curve,
                fig_class_metrics, fig_score_metrics]

    def save_plots(self, plots: List[matplotlib.figure.Figure]):
        """
        Saves the validation plots as image files in disk.

        Parameters
        ----------
        plots: List[matplotlib.figure.Figure]
            This is the list of matplotlib figures to save.
        """
        plots[0].savefig(
            f"{self.parameters.validation.visualize}/confusion_matrix.png",
            bbox_inches="tight")

        plots[1].savefig(
            f"{self.parameters.validation.visualize}/prec_rec_curve.png",
            bbox_inches="tight")

        plots[2].savefig(
            f"{self.parameters.validation.visualize}/class_scores.png",
            bbox_inches="tight")

        plots[3].savefig(
            f"{self.parameters.validation.visualize}/histogram_scores.png",
            bbox_inches="tight")

    def publish_plots(
            self, plots: List[matplotlib.figure.Figure], epoch: int = 0):
        """
        Publishes the validation plots into Tensorboard.

        Parameters
        ----------
        plots: List[matplotlib.figure.Figure]
            This is the list of matplotlib figures to save.
        epoch: int
            The training epoch number used for ModelPack training usage.
        """
        nimage_confusion_matrix = figure2numpy(plots[0])
        nimage_precision_recall = figure2numpy(plots[1])
        nimage_class = figure2numpy(plots[2])
        nimage_score = figure2numpy(plots[3])

        self.tensorboard_writer(
            nimage_confusion_matrix,
            f"{self.metrics.metrics.model}_confusion_matrix.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_precision_recall,
            f"{self.metrics.metrics.model}_precision_recall.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_class,
            f"{self.metrics.metrics.model}_scores.png",
            step=epoch
        )
        self.tensorboard_writer(
            nimage_score,
            f"{self.metrics.metrics.model}_histogram_scores.png",
            step=epoch
        )
