from __future__ import annotations
from typing import TYPE_CHECKING, Union

import numpy as np

from edgefirst.validator.metrics.utils.math import (iou_2d, localize_distance)

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ValidationParameters


class Matcher:
    """
    The Matching Algorithm used in EdgeFirst Validation. This algorithm
    will run matching recursively to find the best matches based on IoU
    with a preference to a matching ground truth and detection labels.
    The Matching and Classification rules is documented in::
    https://au-zone.atlassian.net/wiki/spaces/DV/pages/2325938299/DeepView-Validator+Matching+and+Classification+Rules

    Parameters
    ----------
    parameters: ValidationParameters
        This contains the validation parameters set from the command line.
    """

    def __init__(self, parameters: ValidationParameters):
        self.parameters = parameters
        self.gt_boxes = list()
        self.gt_labels = list()
        self.dt_boxes = list()
        self.dt_labels = list()

        # This contains the IoUs of each detection to ground truth match.
        self.iou_list = list()
        # An IoU grid where rows are the ground truths
        # and the predictions are the columns.
        self.iou_grid = list()
        # The matches containing ground truth and detection indices:
        # [[gti, dti], [gti, dti], ..].
        self.index_matches = list()
        # The prediction indices that were not matched.
        self.index_unmatched_dt = list()
        # The ground truth indices that were not matched.
        self.index_unmatched_gt = list()

    def set_boxes(
        self,
        gt_boxes: list,
        gt_labels: list,
        dt_boxes: list,
        dt_labels: list
    ):
        """
        Sets the bounding boxes and labels for the ground truth and model
        predictions to match the bounding boxes described in the index_matches.
        Calling this method will also reset the previous matching results.

        Parameters
        ----------
        gt_boxes: list
            The ground truth bounding boxes in the format [xmin, ymin, xmax, ymax].
        gt_labels: list
            The ground truth labels for each bounding box. This can either
            contain strings or integers.
        dt_boxes: list
            The prediction bounding boxes in the format [xmin, ymin, xmax, ymax].
        dt_labels: list
            The prediction labels for each bounding box. This can either
            contain strings or integers.
        """
        # Setting boxes requires reset for a new matching process.
        self.reset()
        self.gt_boxes = gt_boxes
        self.gt_labels = gt_labels
        self.dt_boxes = dt_boxes
        self.dt_labels = dt_labels

        self.iou_list = np.zeros(len(self.dt_boxes))
        self.iou_grid = np.zeros((len(self.gt_boxes), len(self.dt_boxes)))

        # The prediction indices that were not matched.
        self.index_unmatched_dt = list(range(0, len(self.dt_boxes)))
        # The ground truth indices that were not matched.
        self.index_unmatched_gt = list(range(0, len(self.gt_boxes)))

    def match(
        self,
        gt_boxes: list,
        gt_labels: list,
        dt_boxes: list,
        dt_labels: list
    ):
        """
        The matching algorithm which matches the predictions to ground truth
        based on matching labels first and then by highest IoU or lowest
        centerpoint distance between boxes.

        This algorithm also incorporates recursive calls to
        perform rematching of ground truth that were unmatched due to
        duplicative matches, but the rematching is based on the next best IoU.

        Parameters
        ----------
        gt_boxes: list
            The ground truth bounding boxes in the format [xmin, ymin, xmax, ymax].
        gt_labels: list
            The ground truth labels for each bounding box. This can either
            contain strings or integers.
        dt_boxes: list
            The prediction bounding boxes in the format [xmin, ymin, xmax, ymax].
        dt_labels: list
            The prediction labels for each bounding box. This can either
            contain strings or integers.
        """
        self.set_boxes(
            gt_boxes=gt_boxes,
            gt_labels=gt_labels,
            dt_boxes=dt_boxes,
            dt_labels=dt_labels
        )

        if 0 in [len(self.gt_boxes), len(self.dt_boxes)]:
            return

        for gti, gt in enumerate(self.gt_boxes):
            # A list of prediction indices with
            # matching labels as the ground truth.
            dti_reflective, iou_reflective = list(), list()
            gt_label = self.gt_labels[gti]

            for dti, dt in enumerate(self.dt_boxes):
                self.iou_grid[gti][dti] = self.get_metric(gt, dt)

                dt_label = self.dt_labels[dti]
                if dt_label == gt_label:
                    dti_reflective.append(dti)
                    iou_reflective.append(self.iou_grid[gti][dti])

            # A potential match is the detection that produced the highest IoU.
            dti = np.argmax(self.iou_grid[gti])
            iou = max(self.iou_grid[gti])
            # If there is no intersection, it cannot be a match.
            if iou < 0:
                continue
            # Only match if the IoU between matching ground truth and detection
            # labels > 0.
            if len(dti_reflective) and max(
                    iou_reflective) >= self.parameters.iou_threshold:
                # The IoU of the detections with the same labels
                # as the ground truth. A potential match is the
                # detection with the same label as the ground truth.
                dti = dti_reflective[np.argmax(iou_reflective)]
                iou = max(iou_reflective)
            self.compare_matches(dti, gti, iou)

        # Find the unmatched predictions
        for match in self.index_matches:
            self.index_unmatched_dt.remove(match[0])
            self.index_unmatched_gt.remove(match[1])

    def compare_matches(self, dti: int, gti: int, iou: float):
        """
        Checks if duplicate matches exists. A duplicate match is when the
        same detection is being matched to more than one ground truth.
        The IoUs are compared and the better IoU is the true match and the
        ground truth of the other match is then rematch to the next best IoU,
        but it performs a recursive call to check if the next best IoU
        also generates a duplicate match.

        Parameters
        ----------
        dti: int
            The detection index being matched to the current ground truth.
        gti: int
            The current ground truth matched to the detection.
        iou: float
            The current best IoU that was computed for the current ground
            truth against all detections.
        """
        twice_matched = [(d, g) for d, g in self.index_matches if d == dti]
        assert len(twice_matched) < 2, "More than two duplicate matches occurred."

        if len(twice_matched) == 1:
            # Compare the IoUs between duplicate matches.
            dti, pre_gti = twice_matched[0]
            if iou > self.iou_list[dti]:
                self.index_matches.remove((dti, pre_gti))
                self.iou_list[dti] = iou
                self.index_matches.append((dti, gti))

                # Rematch pre_gti
                self.iou_grid[pre_gti][dti] = 0.
                dti = np.argmax(self.iou_grid[pre_gti])
                iou = max(self.iou_grid[pre_gti])
                if iou > 0:
                    self.compare_matches(dti, pre_gti, iou)
            else:
                # Rematch gti
                self.iou_grid[gti][dti] = 0.
                dti = np.argmax(self.iou_grid[gti])
                iou = max(self.iou_grid[gti])
                if iou > 0:
                    self.compare_matches(dti, gti, iou)
        else:
            if iou > 0:
                self.iou_list[dti] = iou
                self.index_matches.append((dti, gti))

    def get_metric(
        self,
        gt: Union[list, np.ndarray],
        dt: Union[list, np.ndarray],
    ) -> float:
        """
        Computes either the 3D or 2D IoU or centerpoint distances
        and stores the values in the IoU grid.

        When the iou_first flag is False, IoU is
        considered 0 if the classes don't match.

        Parameters
        ----------
        gt: Union[list, np.ndarray]
            This either contains ground truth bounding boxes
            if 2D validation or 3D box corners if 3D validation.
        dt: Union[list, np.ndarray]
            This either contains prediction bounding boxes
            if 2D validation or 3D box corners if 3D validation.

        Returns
        -------
        float
            The IoU or centerpoint distance between two boxes.

        Raises
        ------
        TypeError
            Raised if an invalid metric type is specified.
        """
        if self.parameters.metric == "iou":
            return iou_2d(dt.astype(float), gt.astype(float))
        elif self.parameters.metric == "centerpoint":
            return 1 - localize_distance(
                dt.astype(float),
                gt.astype(float),
                leniency_factor=self.parameters.matching_leniency
            )
        else:
            raise TypeError(
                "Unknown matching matching metric specified: {}".format(
                    self.parameters.metric
                ))

    def reset(self):
        """
        Resets the containers to allow for a new matching process.
        """
        self.iou_list = list()
        self.iou_grid = list()
        self.index_matches = list()
        self.index_unmatched_dt = list()
        self.index_unmatched_gt = list()
