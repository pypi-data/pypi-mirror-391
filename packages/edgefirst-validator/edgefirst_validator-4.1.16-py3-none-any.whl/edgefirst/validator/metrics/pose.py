from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from edgefirst.validator.metrics.utils.math import mean_absolute_error
from edgefirst.validator.metrics import Metrics, Plots

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ValidationParameters
    from edgefirst.validator.metrics import PoseStats


class PoseMetrics:
    """
    Runs the metric computations for pose. The resulting metrics
    will be populated in the `Metrics` object that is created once initialized.

    Computes the mean squared error between angles for
    detection and ground truth for pose angles.

    Parameters
    ----------
    parameters: ValidationParameters
        This contains validation parameters set from the command line.
    pose_stats: PoseStats
        This is a container for the prediction and the ground truth angles.
    model_name: str
        The base name of the model being validated.
    dataset_name: str
        The base name of the validation dataset.
    save_path: str
        The path to save the metrics on disk.
    """

    def __init__(
        self,
        parameters: ValidationParameters,
        pose_stats: PoseStats,
        model_name: str = "Model",
        dataset_name: str = "Dataset",
        save_path: str = None
    ):
        self.parameters = parameters
        self.plots = Plots()
        self.pose_stats = pose_stats
        self.metrics = Metrics(model=model_name, dataset=dataset_name)
        self.metrics.save_path = save_path

    def run_metrics(self):
        """
        Method process for gathering all metrics used
        for the pose validation.
        """
        self.metrics.angles_mae = self.compute_overall_metrics()

    def compute_overall_metrics(self) -> np.ndarray:
        """
        Calculates the pose metrics with mean squared error for each angle.

        Returns
        -------
        np.ndarray
            This contains the mean squared error for each angle.
        """
        pose_label_data_list = self.pose_stats.stats
        overall_metrics = np.zeros(len(pose_label_data_list))
        for i, pose_data in enumerate(pose_label_data_list):
            overall_metrics[i] = mean_absolute_error(pose_data.y_true,
                                                     pose_data.y_pred)
        return overall_metrics

    def reset(self):
        """
        Reset the metric containers.
        """
        self.plots.reset()
        self.pose_stats.reset()
        self.metrics.reset()
