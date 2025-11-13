from __future__ import annotations

import os
from copy import deepcopy
from typing import TYPE_CHECKING, Tuple, List

import numpy as np
import matplotlib.figure

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.visualize.utils.plots import close_figures
from edgefirst.validator.datasets.utils.transformations import labels2string
from edgefirst.validator.publishers import ConsolePublisher, TensorBoardPublisher

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.datasets import Dataset
    from edgefirst.validator.metrics import Metrics
    from edgefirst.validator.runners import Runner
    from edgefirst.validator.metrics import Plots


class Evaluator:
    """
    Abstract class that provides a template for the
    Evaluators (detection or segmentation).

    Parameters
    ----------
    parameters: CombinedParameters
        This is a container for the model, dataset, and validation parameters
    runner: Runner
        This object provides methods to run inference on the model provided.
    dataset: Dataset
        A type of dataset object responsible for reading different types
        of datasets such as Darknet, TFRecords, or EdgeFirst Datasets.
    """

    def __init__(
        self,
        parameters: CombinedParameters,
        runner: Runner,
        dataset: Dataset,
    ):
        self.parameters = parameters
        self.runner = runner
        self.dataset = dataset

        self.console_writer = ConsolePublisher(
            self.parameters.validation.visualize)
        self.tensorboard_writer = None
        if self.parameters.validation.tensorboard:
            self.tensorboard_writer = TensorBoardPublisher(
                self.parameters.validation.tensorboard)

        self.model_name = os.path.basename(os.path.normpath(
            self.parameters.model.model_path))
        if os.path.isfile(self.parameters.dataset.dataset_path):
            self.dataset_name = os.path.basename(os.path.normpath(
                os.path.dirname(self.parameters.dataset.dataset_path)))
        else:
            self.dataset_name = os.path.basename(os.path.normpath(
                self.parameters.dataset.dataset_path))

        if self.parameters.validation.tensorboard:
            self.save_path = self.parameters.validation.tensorboard
        elif self.tensorboard_writer:
            self.save_path = self.tensorboard_writer.logdir
        elif self.parameters.validation.visualize:
            self.save_path = self.parameters.validation.visualize
        else:
            self.save_path = None

        self.metrics = None
        self.confusion_matrix = None

        # This counter is used to determine the number of images saved.
        self.counter = 0

    def instance_collector(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method")

    def evaluate(self, instance: dict):
        """Abstract Method"""
        pass

    def single_evaluation(self, instance: dict, epoch: int, save_image: bool):
        """
        Run model evaluation on a single image/sample.

        Parameters
        ----------
        instance: dict
            This contains the ground truth and model prediction instances
            with keys "gt_instance", "dt_instance".
        epoch: int
            This is the training epoch number. This
            parameter is internal for ModelPack usage.
            Standalone validation does not use this parameter.
        save_image: bool
            If set to True, this will save the image
            with drawn bounding box results.
        """
        self.evaluate(instance=instance)

        if save_image:
            gt_instance = instance.get("gt_instance", None)
            dt_instance = instance.get("dt_instance", None)

            # Convert labels from integers to string for detection.
            gt_instance.labels = np.array(labels2string(
                gt_instance.labels, self.parameters.dataset.labels))
            dt_instance.labels = np.array(labels2string(
                dt_instance.labels, self.parameters.dataset.labels))
            self.visualize(gt_instance, dt_instance, epoch=epoch)

    def group_evaluation(self, epoch: int = 0, reset: bool = True):
        """
        Runs model validation on all samples in the dataset.

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
        """
        save_image = bool(self.parameters.validation.visualize or
                          self.parameters.validation.tensorboard)

        for instance in self.instance_collector():
            if self.parameters.validation.display >= 0:
                if self.counter < self.parameters.validation.display:
                    save_image = True
                    self.counter += 1
                else:
                    save_image = False

            if instance.get("dt_instance", None) is None:
                logger(
                    "VisionPack Trial Expired. Please use a licensed version" +
                    " for complete validation. Contact support@au-zone.com" +
                    " for more information.", code="WARNING")
                break

            self.single_evaluation(
                instance=instance, epoch=epoch, save_image=save_image)
        return self.end(epoch=epoch, reset=reset)

    def visualize(self):
        """Absract Method"""
        raise NotImplementedError("This is an abstract method")

    def end(
        self,
        epoch: int = 0,
        reset: bool = True,
        publish: bool = True
    ) -> Tuple[Metrics, Plots]:
        """
        Computes the final metrics and generates the validation plots
        to save the results in disk or publishes to Tensorboard.

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
        publish: bool
            Specify to publish and print the metrics. Default to True.

        Returns
        -------
        Tuple[Metrics, Plots]
            Metrics
                This is a container for the detection metrics.
            Plots
                This is a container for the validation data for plotting.
        """
        if self.runner:
            # Collect preprocessing timings.
            if self.dataset:
                dataset_load_time = self.dataset.load_timings
                runner_load_time = self.runner.load_timings
                self.runner.read_timings = self.dataset.read_timings
                if len(dataset_load_time) and len(runner_load_time):
                    input_time = np.array(
                        dataset_load_time) + np.array(runner_load_time)
                    self.runner.load_timings = input_time
                elif len(dataset_load_time):
                    self.runner.load_timings = dataset_load_time
            self.metrics.metrics.timings = self.runner.timings()
        self.metrics.run_metrics()

        # Plot Operations
        if self.parameters.validation.plots:
            if self.parameters.model.common.with_boxes:
                self.metrics.plots.curve_labels = labels2string(
                    self.metrics.plots.curve_labels, self.parameters.dataset.labels)
                if self.parameters.validation.method in [
                        "ultralytics", "yolov7"]:
                    self.metrics.plots.confusion_matrix = self.confusion_matrix.matrix

            if self.parameters.validation.visualize or self.tensorboard_writer:
                plots = self.get_plots()

                if self.parameters.validation.visualize:
                    self.save_plots(plots)
                elif self.tensorboard_writer:
                    self.publish_plots(plots, epoch)
                close_figures(plots)

        if publish:
            # Metric Operations
            if self.tensorboard_writer:
                self.tensorboard_writer.publish_metrics(
                    metrics=self.metrics.metrics,
                    parameters=self.parameters,
                    step=epoch,
                )
            else:
                table = self.console_writer(metrics=self.metrics.metrics,
                                            parameters=self.parameters)
                if self.parameters.validation.visualize:
                    self.console_writer.save_metrics(table)

        # Prevent the reset from taking effect.
        metrics = deepcopy(self.metrics.metrics)
        plots = deepcopy(self.metrics.plots)
        if reset:
            self.metrics.reset()
        return metrics, plots

    def get_plots(self) -> List[matplotlib.figure.Figure]:
        """Absract Method"""
        pass

    def save_plots(self, plots: List[matplotlib.figure.Figure]):
        """Absract Method"""
        pass

    def publish_plots(
            self, plots: List[matplotlib.figure.Figure], epoch: int = 0):
        """Absract Method"""
        pass
