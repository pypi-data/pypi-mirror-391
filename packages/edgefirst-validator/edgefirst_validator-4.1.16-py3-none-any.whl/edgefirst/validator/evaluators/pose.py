from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy as np

from edgefirst.validator.datasets.utils.transformations import (crop_image,
                                                                denormalize)
from edgefirst.validator.evaluators import Evaluator
from edgefirst.validator.visualize import PoseDrawer
from edgefirst.validator.datasets import PoseInstance
from edgefirst.validator.metrics import PoseStats, PoseMetrics


if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.runners import Runner


class PoseValidator(Evaluator):
    """
    Define the validation methods for EdgeFirst. Reproduces EdgeFirst
    metrics for head pose.

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
        super(PoseValidator, self).__init__(
            parameters=parameters, runner=runner, dataset=dataset)

        self.pose_stats = PoseStats()
        self.metrics = PoseMetrics(
            parameters=self.parameters.validation,
            pose_stats=self.pose_stats,
            model_name=self.model_name,
            dataset_name=self.dataset_name,
            save_path=self.save_path
        )
        self.drawer = PoseDrawer()

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

        gt_instance: PoseInstance
        for gt_instance in self.dataset.read_all_samples(
            silent=self.parameters.validation.silent
        ):

            gt_instance.boxes = denormalize(
                gt_instance.boxes, (gt_instance.height, gt_instance.width)
            )
            gt_instance.pose_angles = np.squeeze(gt_instance.pose_angles)

            dt_instance = None
            if len(gt_instance.boxes) > 0:
                gt_box = gt_instance.boxes[0]
                gt_instance.boxes = gt_box

                image = crop_image(gt_instance.image, gt_box)
                angles, labels = self.runner.run_single_instance(image)

                dt_instance = PoseInstance(gt_instance.image_path)
                dt_instance.height = gt_instance.height
                dt_instance.width = gt_instance.width
                dt_instance.pose_angles = angles
                dt_instance.labels = labels

            yield {
                'gt_instance': gt_instance,
                'dt_instance': dt_instance
            }

    def evaluate(self, instance: dict):
        """
        Run model evaluation using EdgeFirst validation methods
        for head pose.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model predictions instances
            with keys "gt_instance" and "dt_instance".
        """
        gt_instance: PoseInstance = instance.get("gt_instance")
        dt_instance: PoseInstance = instance.get("dt_instance")

        dt_angles = dt_instance.pose_angles
        # Currently inside a list of lists
        gt_angles = gt_instance.pose_angles
        self.pose_stats.store_angles(dt_angles, gt_angles)

    def visualize(
        self,
        gt_instance: PoseInstance,
        dt_instance: PoseInstance,
        epoch: int = 0
    ):
        """
        Draw pose axis results on the image and save
        the results in disk or publish into Tensorboard.

        Parameters
        ----------
        gt_instance: DetectionInstance
            This is the ground truth instance which contains
            pose axis for roll, pitch, yaw to draw.
        dt_instance: DetectionInstance
            This is the model detection instance which contains
            pose axis for roll, pitch, yaw to draw.
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        """
        image = self.drawer.draw_axes(
            gt_instance.image,
            dt_instance.pose_angles,
            gt_instance.pose_angles,
            gt_box=gt_instance.boxes
        )

        if self.parameters.validation.visualize:
            image.save(os.path.join(self.parameters.validation.visualize,
                                    os.path.basename(gt_instance.image_path)))
        elif self.tensorboard_writer:
            self.tensorboard_writer(
                np.asarray(image), gt_instance.image_path, step=epoch)
