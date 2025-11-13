from __future__ import annotations

import os
from typing import TYPE_CHECKING, Union

from edgefirst.validator.publishers.utils.table import (detection_table,
                                                        segmentation_table,
                                                        pose_table,
                                                        multitask_table)

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.metrics import Metrics, MultitaskMetrics


class ConsolePublisher:
    """
    Prints the metrics on the terminal.

    Parameters
    ----------
    save_path: str
        The path to save the metrics as a text file.
    """

    def __init__(self, save_path: str):
        self.save_path = save_path

    def __call__(
        self,
        metrics: Union[Metrics, MultitaskMetrics],
        parameters: CombinedParameters,
    ) -> str:
        """
        When this is called, it prints the metrics on the console.

        Parameters
        ----------
        metrics: Union[Metrics, MultitaskMetrics]
            This is the metrics computed during validation.
        parameters: CombinedParameters
            This contains the model, validation, and dataset parameters
            set from the command line.

        Returns
        -------
        str
            The formatted validation table showing the metrics, parameters,
            and model timings.
        """
        if parameters.model.common.with_boxes and parameters.model.common.with_masks:
            table = multitask_table(metrics, parameters)
        elif parameters.model.common.with_boxes:
            table = detection_table(metrics, parameters)
        elif parameters.model.common.with_masks:
            table = segmentation_table(metrics, parameters)
        else:
            table = pose_table(metrics, parameters)

        if not parameters.validation.silent:
            print(table)
        return table

    def save_metrics(
        self,
        table: str
    ):
        """
        Saves the validation metrics as a text file in disk.

        Parameters
        ----------
        table: str
            The validation metrics formatted as a table.
        """
        with open(os.path.join(self.save_path, 'metrics.txt'), 'w') as fp:
            fp.write(table + '\n')
            fp.close()
