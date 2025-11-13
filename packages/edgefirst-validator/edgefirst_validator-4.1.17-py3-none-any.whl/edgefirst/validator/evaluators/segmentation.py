from __future__ import annotations

import os
from copy import deepcopy
from typing import TYPE_CHECKING, List, Tuple

import numpy as np
from PIL import Image
import matplotlib.figure

from edgefirst.validator.metrics.utils.math import mask_iou
from edgefirst.validator.datasets.utils.fetch import get_shape
from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.visualize.utils.plots import (figure2numpy,
                                                       plot_pr_curve,
                                                       plot_mc_curve,
                                                       close_figures,
                                                       plot_classification_segmentation)
from edgefirst.validator.evaluators.utils.classify import classify_mask
from edgefirst.validator.datasets.utils.transformations import (resize,
                                                                labels2string,
                                                                format_segments,
                                                                create_mask_class,
                                                                create_mask_background)
from edgefirst.validator.evaluators import Evaluator, YOLOValidator
from edgefirst.validator.visualize import SegmentationDrawer, DetectionDrawer
from edgefirst.validator.metrics import (SegmentationStats, SegmentationMetrics,
                                         MultitaskMetrics, MultitaskPlots,
                                         YOLOStats, DetectionMetrics)
from edgefirst.validator.datasets import SegmentationInstance, MultitaskInstance

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.runners import Runner


class YOLOSegmentationValidator(YOLOValidator):
    """
    Reproduce the validation methods implemented in Ultralytics for
    segmentation.

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
        dataset: Dataset = None
    ):
        super(YOLOSegmentationValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        self.segmentation_stats = YOLOStats()
        # Segmentation in Ultralytics uses base detection metrics.
        self.segmentation_metrics = DetectionMetrics(
            parameters=self.parameters.validation,
            detection_stats=self.segmentation_stats,
            model_name=self.model_name,
            dataset_name=self.dataset_name,
            save_path=self.save_path,
            labels=self.parameters.dataset.labels
        )

        self.detection_drawer = DetectionDrawer()
        self.segmentation_drawer = SegmentationDrawer()

        # Store both detection and segmentation metric results.
        self.multi_metrics = MultitaskMetrics(
            detection_metrics=self.metrics.metrics,
            segmentation_metrics=self.segmentation_metrics.metrics
        )
        self.multi_plots = MultitaskPlots(
            detection_plots=self.metrics.plots,
            segmentation_plots=self.segmentation_metrics.plots
        )
        self.mask_overlap = True

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

        gt_instance: MultitaskInstance
        for gt_instance in self.dataset.read_all_samples(
            silent=self.parameters.validation.silent
        ):
            detections = self.runner.run_single_instance(
                image=gt_instance.image,
                shapes=gt_instance.shapes,
                ratio=gt_instance.ratio,
                image_shape=gt_instance.image_shape
            )
            # Storing the shapes of the image passed for inference.
            # This is used for box rescaling due to letterbox transformations.
            if self.parameters.dataset.common.cache:
                shapes = gt_instance.shapes
            else:
                shapes = self.runner.shapes

            # Visualize the image with transformations.
            gt_instance.image = self.runner.image
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

            dt_instance = MultitaskInstance(gt_instance.image_path)
            boxes, labels, scores, mask = detections
            dt_instance.height = gt_instance.height
            dt_instance.width = gt_instance.width
            dt_instance.boxes = boxes
            dt_instance.labels = labels
            dt_instance.scores = scores
            dt_instance.shapes = shapes
            dt_instance.mask = mask
            dt_instance.image_shape = gt_instance.image_shape

            self.create_predn(dt_instance)

            yield {
                "gt_instance": gt_instance,
                "dt_instance": dt_instance,
            }

    def create_labelsn(self, gt_instance: MultitaskInstance) -> dict:
        """
        Apply validation filters and prepare ground truth bounding box
        coordinates for image visualization with letterbox,
        padding, and resize transformations, and evaluations.

        Transform ground truth mask to center around objects in images
        with letterbox, padding, or resize transformations.

        Parameters
        ----------
        gt_instance: MultitaskInstance
            The model detections container of the bounding boxes,
            labels, and masks for a single image/sample.
        """
        super().create_labelsn(gt_instance)

        if gt_instance.shapes is not None:
            shapes, label_ratio = gt_instance.shapes
            imgsz = shapes[0]
            ratio_pad = shapes[1]

            # Scale ground truth mask to center around objects
            # in an image with padding transformation.
            if self.parameters.model.common.preprocessing == "pad":
                ratio_pad[0] = label_ratio
                ratio_pad[1] = [0.0, 0.0]
            # Scale ground truth mask to center around objects
            # in an image with letterbox transformation.
            else:
                ratio_pad[0][0] *= label_ratio[0]
                ratio_pad[0][1] *= label_ratio[1]

        else:
            imgsz = get_shape(self.parameters.model.common.shape)
            ratio_pad = [[1.0, 1.0], [0.0, 0.0]]

        if (self.parameters.model.common.semantic and
                "background" not in self.parameters.dataset.labels):
            offset = 1
        else:
            offset = 0

        # For ModelPack do not run this step that converts the mask
        # as instance segmentation. ModelPack is semantic segmentation.
        if not self.parameters.dataset.common.cache:
            masks, sorted_idx = format_segments(
                segments=gt_instance.polygons,
                shape=imgsz,
                ratio_pad=ratio_pad,
                colors=gt_instance.labels + offset,
                mask_overlap=self.mask_overlap,
                semantic=self.parameters.model.common.semantic
            )
            if sorted_idx is not None and len(sorted_idx) > 0:
                if len(gt_instance.labels):
                    gt_instance.labels = gt_instance.labels[sorted_idx]
                if len(gt_instance.boxes):
                    gt_instance.boxes = gt_instance.boxes[sorted_idx]
            gt_instance.mask = masks

        # These steps are redundant in YOLO...
        # Box padding is added instead of substracted for detection.
        # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/augment.py#L1740
        # boxes[..., 1:] += np.array([ratio_pad[1][0], ratio_pad[1][1],
        #                             ratio_pad[1][0], ratio_pad[1][1]])
        # Boxes are converted back to YOLO format.
        # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/augment.py#L2157
        # boxes[..., 1:] = xyxy2yolo(boxes[..., 1:])
        # # Boxes are normalized.
        # # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/augment.py#L2185
        # boxes[..., 1:] /= np.array([imgsz[0], imgsz[1], imgsz[0], imgsz[1]])
        # -----------------Operations above are reverted here------------------
        # Boxes are denormalized and reconverted back to xyxy format and scaled back to native space.
        # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/models/yolo/detect/val.py#L149

    def process_seg_batch_v5(
        self,
        dt_instance: MultitaskInstance,
        gt_instance: MultitaskInstance,
    ) -> np.ndarray:
        """
        Processes predicted and ground truth masks to compute IoU matches.

        Parameters
        ----------
        dt_instance : MultitaskInstance
            A prediction instance container with predicted
            bounding boxes and masks.
        gt_instance : MultitaskInstance
            A ground truth instance contaienr with ground truth
            bounding boxes and masks.

        Returns
        -------
        np.ndarray
            Boolean array indicating correct matches per IoU threshold.
        """
        niou = len(self.segmentation_stats.ious)
        gt_cls = gt_instance.labels
        pred_cls = dt_instance.labels

        gt_masks = gt_instance.mask
        pred_masks = dt_instance.mask

        if len(gt_cls) == 0 or len(pred_cls) == 0:
            correct = np.zeros((len(pred_cls), niou), dtype=bool)
        else:
            if self.mask_overlap and not self.parameters.model.common.semantic:
                nl = len(gt_cls)
                index = np.arange(nl).reshape(nl, 1, 1) + 1
                # shape(1,640,640) -> (n,640,640)
                gt_masks = np.repeat(gt_masks, nl, axis=0)
                gt_masks = np.where(gt_masks == index, 1.0, 0.0)

            if gt_masks.shape[1:] != pred_masks.shape[1:]:
                ih, iw = pred_masks.shape[1:]
                # masks: (N, H, W), new_shape: (new_H, new_W)
                n, _, _ = gt_masks.shape
                resized = np.zeros((n, ih, iw), dtype=gt_masks.dtype)

                for i in range(n):
                    mask_resized = resize(gt_masks[i],
                                          size=(ih, iw),
                                          resample=Image.Resampling.BILINEAR)
                    resized[i] = np.array(mask_resized)
                gt_masks = resized
                gt_masks = (gt_masks > 0.50).astype(np.uint8)

            iou = mask_iou(
                gt_masks.reshape(gt_masks.shape[0], -1).astype(np.float32),
                pred_masks.reshape(pred_masks.shape[0], -1).astype(np.float32)
            )
            correct = self.match_predictions(pred_classes=pred_cls,
                                             true_classes=gt_cls,
                                             iou=iou)
        return correct

    def process_seg_batch_v7(
        self,
        dt_instance: MultitaskInstance,
        gt_instance: MultitaskInstance
    ) -> np.ndarray:
        """
        Placeholder for YOLOv7 segmentation evaluation support.

        Parameters
        ----------
        dt_instance : MultitaskInstance
            A prediction instance container with predicted
            bounding boxes and masks.
        gt_instance : MultitaskInstance
            A ground truth instance contaienr with ground truth
            bounding boxes and masks.

        Returns
        -------
        np.ndarray
            Boolean array indicating correct matches per IoU threshold.
        """
        logger("Validation with YOLOv7 is not yet supported for segmentation. " +
               "Defaulting to use Ultralytics.", code="WARNING")
        return self.process_seg_batch_v5(
            dt_instance=dt_instance,
            gt_instance=gt_instance
        )

    def evaluate(self, instance: dict):
        """
        Evaluates a segmentation prediction instance and updates metrics.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model prediction instances
            with keys "gt_instance", "dt_instance".
        """
        super().evaluate(instance=instance)

        gt_instance: MultitaskInstance = instance.get("gt_instance")
        dt_instance: MultitaskInstance = instance.get("dt_instance")

        if self.parameters.validation.method == "ultralytics":
            correct = self.process_seg_batch_v5(dt_instance=dt_instance,
                                                gt_instance=gt_instance)
        elif self.parameters.validation.method == "yolov7":
            correct = self.process_seg_batch_v7(dt_instance=dt_instance,
                                                gt_instance=gt_instance)
        else:
            correct = np.zeros((0, len(self.segmentation_stats.ious)),
                               dtype=bool)

        self.segmentation_stats.stats["tp"].append(correct)
        self.segmentation_stats.stats["conf"].append(dt_instance.scores)
        self.segmentation_stats.stats["pred_cls"].append(dt_instance.labels)
        self.segmentation_stats.stats["target_cls"].append(gt_instance.labels)

    def process_dt_mask_visualization(
        self,
        mask: np.ndarray,
        labels: np.ndarray,
        input_shape: tuple,
    ) -> np.ndarray:
        """
        Transform the prediction masks
        into a single 2D array for visualization.

        Parameters
        ----------
        mask: np.ndarray
            The mask to process. This has a typical shape of (n, 160, 160)
            containing the mask for each object.
        labels: np.ndarray
            The string labels of each mask/object in the image.
        input_shape: tuple
            The model input shape (height, width).

        Returns
        -------
        np.ndarray
            The resized 2D mask with the same dimensions as
            the image and contains the labels for each pixel
            representing the object.
        """
        if "background" not in self.parameters.dataset.labels:
            offset = 1
        else:
            offset = 0

        if not self.parameters.model.common.semantic:
            masks = np.zeros(mask.shape[1:], dtype=mask.dtype)
            for cls, m in zip(labels, mask):
                # Offset because detection labels start at 0.
                masks[m > 0] = self.parameters.dataset.labels.index(cls) + offset
        else:
            masks = mask.squeeze()
            
        return resize(masks, input_shape, resample=Image.Resampling.NEAREST)

    def process_gt_mask_visualization(
        self,
        mask: np.ndarray,
        labels: np.ndarray,
        input_shape: tuple,
    ) -> np.ndarray:
        """
        Transform the mask into a 2D array for visualization.

        Parameters
        ----------
        mask: np.ndarray
            The mask to process. This has a typical shape of (1, 160, 160)
            containing the mask for each object.
        labels: np.ndarray
            The string labels of each mask/object in the image.
        input_shape: tuple
            The model input shape (height, width).

        Returns
        --------
        np.ndarray
            The resized 2D mask with the same dimensions as
            the image and contains the labels for each pixel
            representing the object.
        """
        if "background" not in self.parameters.dataset.labels:
            offset = 1
        else:
            offset = 0

        if not self.parameters.model.common.semantic:
            masks = np.zeros(mask.shape[1:], dtype=mask.dtype)
            unique = np.unique(mask)
            unique = unique[unique != 0]
            if self.mask_overlap:
                for i, cls in zip(unique, labels):
                    masks[mask[0] == i] = self.parameters.dataset.labels.index(
                        cls) + offset
            else:
                for m, cls in zip(mask, labels):
                    masks[m > 0] = self.parameters.dataset.labels.index(cls) + offset
        else:
            masks = mask.squeeze()
        return resize(masks, input_shape, resample=Image.Resampling.NEAREST)

    def visualize(
        self,
        gt_instance: MultitaskInstance,
        dt_instance: MultitaskInstance,
        epoch: int = 0
    ):
        """
        Visualizes predicted and ground truth bounding
        boxes and masks on an image.

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
        # Separate results for the ground truth and detection.
        dt_instance.image = gt_instance.image.copy()

        # Draw the ground truth boxes on the image.
        image = self.detection_drawer.draw_2d_gt_boxes(
            image=gt_instance.image,
            gt_instance=gt_instance,
            method="ultralytics",
            labels=self.parameters.dataset.labels,
        )
        gt_instance.image = np.asarray(image)

        # Transform ground truth masks into a 2D mask array with all the
        # labels.
        gt_instance.mask = self.process_gt_mask_visualization(
            mask=gt_instance.mask,
            labels=gt_instance.labels,
            input_shape=get_shape(self.parameters.model.common.shape),
        )

        # Filter to visualize only confident scores.
        filt = dt_instance.scores >= 0.25
        dt_instance.boxes = dt_instance.boxes[filt]
        dt_instance.labels = dt_instance.labels[filt]
        dt_instance.scores = dt_instance.scores[filt]

        if (len(dt_instance.mask.shape) >= len(filt) and
                not self.parameters.model.common.semantic):
            dt_instance.mask = dt_instance.mask[filt]

        # Draw the prediction boxes on the image.
        image = self.detection_drawer.draw_2d_dt_boxes(
            image=dt_instance.image,
            dt_instance=dt_instance,
            method="ultralytics",
            labels=self.parameters.dataset.labels,
        )
        dt_instance.image = np.asarray(image)

        # Transform prediction masks into a 2D mask array with all the labels.
        dt_instance.mask = self.process_dt_mask_visualization(
            mask=dt_instance.mask,
            labels=dt_instance.labels,
            input_shape=get_shape(self.parameters.model.common.shape),
        )

        # Draw the masks prediction and ground truth boxes on the image.
        image = self.segmentation_drawer.mask2maskimage(
            gt_instance=gt_instance,
            dt_instance=dt_instance
        )

        if self.parameters.validation.visualize:
            image.save(os.path.join(self.parameters.validation.visualize,
                                    os.path.basename(gt_instance.image_path)))
        elif self.tensorboard_writer:
            self.tensorboard_writer(
                np.asarray(image), gt_instance.image_path, step=epoch)

    def end(
        self,
        epoch: int = 0,
        reset: bool = True
    ) -> Tuple[MultitaskMetrics, MultitaskPlots]:
        """
        Computes the final metrics from Ultralytics for detection and
        segmentation and generates the validation plots to save the
        results in disk or publishes to Tensorboard.

        Parameters
        ----------
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        reset: bool
            This is an optional parameter that controls the reset state.
            By default, it will reset at the end of validation to erase
            the data in the containers.

        Returns
        -------
        Tuple[MultitaskMetrics, MultitaskPlots]
            This returns the detection and segmentation metrics and
            validation plots.
        """
        metrics, plots = super().end(epoch=epoch, reset=reset, publish=False)

        self.multi_metrics.detection_metrics = metrics
        self.multi_plots.detection_plots = plots
        self.multi_metrics.timings = metrics.timings

        self.segmentation_metrics.run_metrics()
        self.multi_metrics.segmentation_metrics = deepcopy(
            self.segmentation_metrics.metrics)
        self.multi_plots.segmentation_plots = deepcopy(
            self.segmentation_metrics.plots)

        # Plot Operations
        if self.parameters.validation.plots:
            self.segmentation_metrics.plots.curve_labels = labels2string(
                self.segmentation_metrics.plots.curve_labels,
                self.parameters.dataset.labels
            )
            self.segmentation_metrics.plots.confusion_matrix =\
                self.confusion_matrix.matrix

            if self.parameters.validation.visualize or self.tensorboard_writer:
                plots = self.get_seg_plots()

                if self.parameters.validation.visualize:
                    self.save_plots(plots)
                elif self.tensorboard_writer:
                    self.publish_plots(plots, epoch)
                close_figures(plots)

        if self.tensorboard_writer:
            self.tensorboard_writer.publish_metrics(
                metrics=self.multi_metrics,
                parameters=self.parameters,
                step=epoch,
            )
        else:
            table = self.console_writer(metrics=self.multi_metrics,
                                        parameters=self.parameters)

            if self.parameters.validation.visualize:
                self.console_writer.save_metrics(table)

        if reset:
            self.segmentation_metrics.reset()
        return self.multi_metrics, self.multi_plots

    def get_seg_plots(self) -> List[matplotlib.figure.Figure]:
        """
        Reproduces the validation charts from Ultralytics.
        These plots are Matplotlib figures.

        Returns
        -------
        List[matplotlib.figure.Figure]
            This contains matplotlib figures of the plots.
        """
        fig_confusion_matrix = self.confusion_matrix.plot(
            names=self.segmentation_metrics.plots.confusion_labels
        )
        fig_prec_rec_curve = plot_pr_curve(
            precision=self.segmentation_metrics.plots.py,
            recall=self.segmentation_metrics.plots.px,
            ap=self.segmentation_metrics.plots.average_precision,
            names=self.parameters.dataset.labels,
            model=self.segmentation_metrics.metrics.model,
            iou_threshold=self.parameters.validation.iou_threshold
        )
        fig_f1_curve = plot_mc_curve(
            px=self.segmentation_metrics.plots.px,
            py=self.segmentation_metrics.plots.f1,
            names=self.parameters.dataset.labels,
            model=self.segmentation_metrics.metrics.model,
            ylabel='F1'
        )
        fig_prec_curve = plot_mc_curve(
            px=self.segmentation_metrics.plots.px,
            py=self.segmentation_metrics.plots.precision,
            names=self.parameters.dataset.labels,
            model=self.segmentation_metrics.metrics.model,
            ylabel='Precision'
        )
        fig_rec_curve = plot_mc_curve(
            px=self.segmentation_metrics.plots.px,
            py=self.segmentation_metrics.plots.recall,
            names=self.parameters.dataset.labels,
            model=self.segmentation_metrics.metrics.model,
            ylabel='Recall'
        )
        return [fig_confusion_matrix,
                fig_prec_rec_curve,
                fig_f1_curve,
                fig_prec_curve,
                fig_rec_curve]


class SegmentationValidator(Evaluator):

    """
    Define the validation methods for EdgeFirst. Reproduces EdgeFirst
    metrics for segmentation::

        1. Grab the ground truth and the model prediction instances per image.
        2. Create masks for both ground truth and model prediction.
        3. Classify the mask pixels as either true predictions or false predictions.
        4. Overlay the ground truth and predictions masks on the image.
        5. Calculate the metrics.

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
        super(SegmentationValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        self.segmentation_stats = SegmentationStats()
        self.metrics = SegmentationMetrics(
            parameters=self.parameters.validation,
            segmentation_stats=self.segmentation_stats,
            model_name=self.model_name,
            dataset_name=self.dataset_name,
            save_path=self.save_path
        )
        self.drawer = SegmentationDrawer()
        self.mask_overlap = True

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

        Raises
        ------
        ValueError
            Raised if the model labels and the
            dataset labels are not matching.
        """

        gt_instance: SegmentationInstance
        for gt_instance in self.dataset.read_all_samples(
            silent=self.parameters.validation.silent
        ):
            mask = self.runner.run_single_instance(
                image=gt_instance.image,
                shapes=gt_instance.shapes,
                ratio=gt_instance.ratio,
                image_shape=gt_instance.image_shape
            )
            # Storing the shapes of the image passed for inference.
            # This is used for box rescaling due to letterbox transformations.
            if self.parameters.dataset.common.cache:
                shapes = gt_instance.shapes
            else:
                shapes = self.runner.shapes

            # Visualize the image with transformations.
            gt_instance.image = self.runner.image
            gt_instance.shapes = shapes
            gt_instance.image_shape = (self.runner.image_shape if
                                       self.runner.image_shape is not None else
                                       (gt_instance.height, gt_instance.width))

            if mask is None:
                yield {
                    'gt_instance': gt_instance,
                    'dt_instance': None
                }

            dt_instance = SegmentationInstance(gt_instance.image_path)
            dt_instance.height = gt_instance.height
            dt_instance.width = gt_instance.width
            dt_instance.shapes = shapes
            dt_instance.image_shape = gt_instance.image_shape
            dt_instance.mask = self.calibrate_mask(mask)
            self.create_labelsn(gt_instance)

            if dt_instance.mask.shape != gt_instance.mask.shape:
                dt_instance.mask = resize(
                    dt_instance.mask, gt_instance.mask.shape,
                    resample=Image.Resampling.NEAREST)

            yield {
                'gt_instance': gt_instance,
                'dt_instance': dt_instance
            }

    def create_labelsn(self, gt_instance: SegmentationInstance) -> dict:
        """
        Transform ground truth mask to center around objects in images
        with letterbox, padding, or resize transformations.

        Parameters
        ----------
        gt_instance: SegmentationInstance
            The model detections container of the bounding boxes,
            labels, and masks for a single image/sample.
        """
        if gt_instance.shapes is not None:
            shapes, label_ratio = gt_instance.shapes
            imgsz = shapes[0]
            ratio_pad = shapes[1]

            # Scale ground truth mask to center around objects
            # in an image with padding transformation.
            if self.parameters.model.common.preprocessing == "pad":
                ratio_pad[0] = label_ratio
                ratio_pad[1] = [0.0, 0.0]
            # Scale ground truth mask to center around objects
            # in an image with letterbox transformation.
            else:
                ratio_pad[0][0] *= label_ratio[0]
                ratio_pad[0][1] *= label_ratio[1]

        else:
            imgsz = get_shape(self.parameters.model.common.shape)
            ratio_pad = [[1.0, 1.0], [0.0, 0.0]]

        if "background" not in self.parameters.dataset.labels:
            offset = 1
        else:
            offset = 0

        # For ModelPack do not run this step that converts the mask
        # as instance segmentation. ModelPack is semantic segmentation.
        if not self.parameters.dataset.common.cache:
            masks, _ = format_segments(
                segments=gt_instance.polygons,
                shape=imgsz,
                ratio_pad=ratio_pad,
                # Offset due to background.
                colors=gt_instance.labels + offset,
                mask_overlap=self.mask_overlap,
                semantic=True
            )
            gt_instance.mask = np.squeeze(masks)

    def calibrate_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Map the labels of the mask to the label order of the ground
        truth labels. This ensures the prediction mask and the ground
        truth mask are comparable.

        Parameters
        ----------
        mask: np.ndarray
            The prediction mask output from the model.

        Returns
        -------
        np.ndarray
            The calibrated prediction mask.
        """
        mask = np.squeeze(mask)
        # For segmentation, the background class should exist to properly
        # map mask indices.
        if "background" not in self.parameters.model.labels:
            model_labels = ["background"] + self.parameters.model.labels
        else:
            model_labels = self.parameters.model.labels

        if "background" not in self.parameters.dataset.labels:
            dataset_labels = ["background"] + self.parameters.dataset.labels
        else:
            dataset_labels = self.parameters.dataset.labels

        # If the label orders does not match between prediction and dataset,
        # map the prediction indices to the dataset indices.
        if model_labels != dataset_labels:
            # -1 means unmapped/missing
            index_map = np.full(len(model_labels), -1, dtype=int)
            for model_idx, label in enumerate(model_labels):
                if label in dataset_labels:
                    index_map[model_idx] = dataset_labels.index(label)
                else:
                    raise ValueError(
                        f"Label '{label}' not found in dataset labels.")

            mask = index_map[mask]
        return mask

    def evaluate(self, instance: dict):
        """
        Run model evaluation using EdgeFirst validation methods
        for segmentation.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model predictions instances
            with keys "gt_instance" and "dt_instance".
        """
        gt_instance: SegmentationInstance = instance.get("gt_instance")
        dt_instance: SegmentationInstance = instance.get("dt_instance")

        class_labels = np.unique(np.append(np.unique(gt_instance.mask),
                                           np.unique(dt_instance.mask)))
        gt_mask = gt_instance.mask
        dt_mask = dt_instance.mask

        predictions = dt_mask.flatten()
        ground_truths = gt_mask.flatten()

        if not self.parameters.validation.include_background:
            class_labels = class_labels[class_labels != 0]
            predictions = predictions[predictions != 0]
            ground_truths = ground_truths[ground_truths != 0]
            true_predictions, false_predictions, union_gt_dt = classify_mask(
                gt_mask, dt_mask)
        else:
            true_predictions, false_predictions, union_gt_dt = classify_mask(
                gt_mask, dt_mask, False)

        self.segmentation_stats.capture_class(class_labels,
                                              self.parameters.dataset.labels)
        self.metrics.metrics.add_ground_truths(len(ground_truths))
        self.metrics.metrics.add_predictions(len(predictions))
        self.metrics.metrics.add_true_predictions(true_predictions)
        self.metrics.metrics.add_false_predictions(false_predictions)
        self.metrics.metrics.add_union(union_gt_dt)

        for cl in class_labels:
            gt_class_mask = create_mask_class(gt_mask, cl)
            dt_class_mask = create_mask_class(dt_mask, cl)

            # Evaluate background class
            if cl == 0:
                gt_class_mask = create_mask_background(gt_mask)
                dt_class_mask = create_mask_background(dt_mask)

            class_ground_truths = np.sum(gt_mask == cl)
            class_predictions = np.sum(dt_mask == cl)

            # Under classify_mask always exclude background because we are
            # only concerned with this class.
            class_true_predictions, class_false_predictions, union_gt_dt = \
                classify_mask(gt_class_mask, dt_class_mask)

            datalabel = self.segmentation_stats.get_label_data(
                self.parameters.dataset.labels[cl]
            )
            datalabel.add_true_predictions(class_true_predictions)
            datalabel.add_false_predictions(class_false_predictions)
            datalabel.add_ground_truths(class_ground_truths)
            datalabel.add_predictions(class_predictions)
            datalabel.add_union(union_gt_dt)

    def visualize(
        self,
        gt_instance: SegmentationInstance,
        dt_instance: SegmentationInstance,
        epoch: int = 0
    ):
        """
        Draw segmentation mask results on the image and save
        the results in disk or publish into Tensorboard.

        Parameters
        ----------
        gt_instance: DetectionInstance
            This is the ground truth instance which contains masks
            and labels to draw.
        dt_instance: DetectionInstance
            This is the model detection instance which contains the
            masks and labels to draw.
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        """
        image = self.drawer.mask2maskimage(gt_instance, dt_instance)

        if self.parameters.validation.visualize:
            image.save(os.path.join(self.parameters.validation.visualize,
                                    os.path.basename(gt_instance.image_path)))
        elif self.tensorboard_writer:
            self.tensorboard_writer(
                np.asarray(image), gt_instance.image_path, step=epoch)

    def get_plots(self) -> List[matplotlib.figure.Figure]:
        """
        Generatte EdgeFirst validation plots.

        Returns
        -------
        List[matplotlib.figure.Figure]
            This contains matplotlib figures of the plots.
        """
        fig_class_metrics = plot_classification_segmentation(
            class_histogram_data=self.metrics.plots.class_histogram_data,
            model=self.metrics.metrics.model
        )
        return [fig_class_metrics]

    def save_plots(self, plots: List[matplotlib.figure.Figure]):
        """
        Saves the validation plots as image files in disk.

        Parameters
        ----------
        plots: List[matplotlib.figure.Figure]
            This is the list of matplotlib figures to save.
        """
        plots[0].savefig(
            f'{self.parameters.validation.visualize}/class_scores.png',
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
        nimage_class = figure2numpy(plots[0])
        self.tensorboard_writer(
            nimage_class,
            f"{self.metrics.metrics.model}_scores.png",
            step=epoch
        )
