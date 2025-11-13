from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from edgefirst.validator.evaluators.callbacks import PlotsCallback, CallbacksList

if TYPE_CHECKING:
    from edgefirst.validator.publishers import StudioPublisher
    from edgefirst.validator.evaluators import Evaluator


class StudioProgress:
    """
    Deploy standard validation from the existing evaluator objects
    but also provide communication to EdgeFirst Studio to report
    the progress and the final metrics and evaluation of the model
    performance.

    Parameters
    ----------
    evaluator: Evaluator
        This object handles running validation by iterating through
        the dataset samples and run model inference to calculate the
        validation metrics at the end of the process.
    studio_publisher: StudioPublisher
        Handles the state updates to the validation session in EdgeFirst Studio.
    """

    def __init__(
        self,
        evaluator: Evaluator,
        studio_publisher: StudioPublisher
    ):
        self.evaluator = evaluator
        plots_callback = PlotsCallback(studio_publisher=studio_publisher,
                                       parameters=self.evaluator.parameters)
        self.callbacks = CallbacksList([plots_callback])

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
        save_image = bool(self.evaluator.parameters.validation.visualize or
                          self.evaluator.parameters.validation.tensorboard)

        logs = {
            "total": len(self.evaluator.dataset)
        }

        i = 0
        try:
            self.callbacks.on_test_begin(logs=logs)
            for instance in self.evaluator.instance_collector():
                i += 1
                self.callbacks.on_test_batch_begin(step=i, logs=logs)
                if self.evaluator.parameters.validation.display >= 0:
                    if (self.evaluator.counter <
                            self.evaluator.parameters.validation.display):
                        save_image = True
                        self.evaluator.counter += 1
                    else:
                        save_image = False

                self.evaluator.single_evaluation(
                    instance, epoch=epoch, save_image=save_image)
                self.callbacks.on_test_batch_end(step=i, logs=logs)
            metrics, plots = self.end(epoch=epoch, reset=reset)

            if (self.evaluator.parameters.model.common.with_boxes and
                    self.evaluator.parameters.model.common.with_masks):
                logs["multitask"] = metrics
                logs["plots"] = plots
                logs["timings"] = metrics.timings

            elif self.evaluator.parameters.model.common.with_boxes:
                logs["detection"] = metrics
                logs["plots"] = plots
                logs["timings"] = metrics.timings

            elif self.evaluator.parameters.model.common.with_masks:
                logs["segmentation"] = metrics
                logs["plots"] = plots
                logs["timings"] = metrics.timings

            self.callbacks.on_test_end(logs=logs)

        except Exception as e:
            self.callbacks.on_test_error(step=i, error=e, logs=logs)
            error = traceback.format_exc()
            print(error)
            raise e

    def end(self, epoch: int = 0, reset: bool = True):
        """
        Calculate final metrics and publish the results into
        EdgeFirst Studio.

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
        Tuple[Metrics, Metrics]
            This returns the detection and segmentation metrics for
            multitask. Otherwise, for single tasks, only one or
            the other is returned.
        """
        return self.evaluator.end(epoch=epoch, reset=reset)
