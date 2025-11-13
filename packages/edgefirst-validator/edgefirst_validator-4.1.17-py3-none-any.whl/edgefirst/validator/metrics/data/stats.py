from typing import List, Union

import numpy as np

from edgefirst.validator.metrics.data import (DetectionLabelData,
                                              SegmentationLabelData,
                                              PoseLabelData)


class YOLOStats:
    """
    Storing the pre-calculations of the Ultralytics metrics. The statistics
    are formatted in the same manner as Ultralytics which contains the
    correction matrix, the prediction class, the prediction confidence, and
    the ground truth class all of which are used to calculate the metrics.
    """

    def __init__(self):
        self.__stats = {
            "tp": [],
            "conf": [],
            "pred_cls": [],
            "target_cls": [],
            "target_img": [],
            "tp_m": []
        }
        self.__ious = np.array([
            0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95])

    @property
    def stats(self) -> dict:
        """
        Attribute to access the stats required for
        computing Ultralytics metrics.

        Returns
        -------
        dict
            This list contains the keys (['tp', 'conf', 'pred_cls',
            'target_cls', 'target_img', 'tp_m']) with the
            following items [tp (n, 10), conf (n, 1), pred_cls (n, 1),
            target_cls (n, 1), target_img (nc, ), tp_m (n, 10)].

            The tp/tp_m matrix contains True or False values for each IoU
            step of all n predictions. The conf contains the confidence
            scores of each prediction. The pred_cls contains the labels
            of each prediction. The target_cls contains the labels
            of each ground truth.
        """
        return self.__stats

    @stats.setter
    def stats(self, stat: dict):
        """
        Sets the stats to a new value.

        Parameters
        ----------
        stat: dict
            These are the stats to set.
        """
        self.__stats = stat

    @property
    def ious(self) -> np.ndarray:
        """
        Attribute to access the ious which contains the IoU steps for validation.
        By default set from 0.50 to 0.95 in 0.05 steps.

        Returns
        -------
        np.ndarray
            The list of IoUs to evaluate the model.
        """
        return self.__ious

    @ious.setter
    def ious(self, iou: np.ndarray):
        """
        Sets the IoU steps to a new value.

        Parameters
        ----------
        iou: np.ndarray
            These are the various IoU levels to evaluate the model.
        """
        self.__ious = iou

    def reset(self):
        """
        Resets the stats to an empty container.
        """
        self.stats = {
            "tp": [],
            "conf": [],
            "pred_cls": [],
            "target_cls": [],
            "target_img": [],
            "tp_m": []
        }


class DetectionStats(YOLOStats):
    """
    Storing the pre-calculations of the EdgeFirst metrics. The statistics
    contains DetectionLabelData containers for each label found during validation.
    A label container will store the number of ground truths, true positives,
    false positives, false negatives of the specific label. This will be used
    to calculate the metrics.
    """

    def __init__(self):
        super(DetectionStats, self).__init__()

        self.__tp = list()  # Model correct matrix (n, 10).
        self.__conf = list()  # Prediction confidence scores.
        self.__pred_cls = list()  # Prediction labels.
        self.__target_cls = list()  # Ground truths labels.

        # A list containing the strings or integers of unique labels.
        self.__labels = list()
        # A list containing the DetectionLabelData objects for each label.
        self.__stats = list()

    @property
    def labels(self) -> list:
        """
        Attribute to access the list of unique labels found.

        Returns
        -------
        list
            This contains unique labels found during validation.
        """
        return self.__labels

    @labels.setter
    def labels(self, new_labels: list):
        """
        Sets the list of unique labels found during validation.

        Parameters
        ----------
        new_labels: list
            This is the list of unique labels found during validation.
        """
        self.__labels = new_labels

    @property
    def stats(self) -> List[DetectionLabelData]:
        """
        Attribute to access the stats which contains DetectionLabelData
        objects needed to compute EdgeFirst metrics.

        Returns
        -------
        List[DetectionLabelData]
            This list contains DetectionLabelData objects where each
            object tracks the metrics of a specific label.
        """
        return self.__stats

    @stats.setter
    def stats(self, stat: List[DetectionLabelData]):
        """
        Sets the stats to a new value.

        Parameters
        ----------
        stat: List[DetectionLabelData]
            These are the stats to set.
        """
        self.__stats = stat

    def get_label_data(
        self,
        label: Union[str, int, np.integer]
    ) -> Union[DetectionLabelData, None]:
        """
        Grabs the DetectionLabelData object by the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            A unique string label or integer index to
            fetch the LabelData container.

        Returns
        -------
        Union[DetectionLabelData, None]
            The data container of the label specified if
            it exists. None if the label does not exist.
        """
        for label_data in self.stats:
            if label_data.label == label:
                return label_data
        return None

    def add_label_data(self, label: Union[str, int, np.integer]):
        """
        Adds a DetectionLabelData object for the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            The string label or the integer index
            to place as a data container.
        """
        self.stats.append(DetectionLabelData(label))

    def capture_class(self, labels: Union[list, np.ndarray]):
        """
        Records the unique labels encountered from the prediction and
        ground truth and creates a DetectionLabelData container
        for each unique label found. Ignores 'background' or empty string
        labels.

        Parameters
        ----------
        labels: Union[list, np.ndarray]
            This list contains labels for one image from either the
            ground truth or the predictions.
        """
        for label in labels:
            if isinstance(label, str):
                if label.lower() in ["background", " ", ""]:
                    continue
            if label not in self.labels:
                self.add_label_data(label)
                self.labels.append(label)

    @property
    def tp(self) -> list:
        """
        Attribute to access the correct matrix.

        Returns
        -------
        list
            This is a (n, 10) correct matrix similar to Ultralytics parameters
            which arranges all the classes in rows and 10 IoU thresholds in
            columns and contains boolean values of True or False depending
            on the class and the IoU threshold.
        """
        return self.__tp

    @tp.setter
    def tp(self, this_tp: list):
        """
        Sets the correct matrix to a new value.

        Parameters
        ----------
        this_tp: list
            The correct matrix to set.
        """
        self.__tp = this_tp

    @property
    def conf(self) -> list:
        """
        Attribute to access the model prediction confidence scores.

        Returns
        -------
        list
            An array of model prediction scores for each label
            in the row of the correct matrix.
        """
        return self.__conf

    @conf.setter
    def conf(self, this_conf: list):
        """
        Sets the confidence scores to a new value.

        Parameters
        ----------
        this_conf: list
            The model prediction scores of each row in the correct matrix.
        """
        self.__conf = this_conf

    @property
    def pred_cls(self) -> list:
        """
        Attribute to access the model class labels.

        Returns
        -------
        list
            An array of model labels for each row in the correct matrix.
        """
        return self.__pred_cls

    @pred_cls.setter
    def pred_cls(self, this_pred_cls: list):
        """
        Sets the model prediction labels to a new value.

        Parameters
        ----------
        this_pred_cls: list
            The model prediction labels of each row in the correct matrix.
        """
        self.__pred_cls = this_pred_cls

    @property
    def target_cls(self) -> list:
        """
        Attribute to access the ground truth class labels.

        Returns
        -------
        list
            An array of ground truth labels for each row in the correct matrix.
        """
        return self.__target_cls

    @target_cls.setter
    def target_cls(self, this_target_cls: list):
        """
        Set the ground truth labels to a new value.

        Parameters
        ----------
        this_target_cls: list
            The ground truth labels of each row in the correct matrix.
        """
        self.__target_cls = this_target_cls

    def reset(self):
        """
        Resets the container back to an empty list.
        """
        self.stats = list()
        self.labels = list()

        self.tp = list()
        self.conf = list()
        self.pred_cls = list()  # classes of detections
        self.target_cls = list()  # classes of ground truths


class SegmentationStats:
    """
    Acts as a container of SegmentationLabelData objects for each label
    and provides methods to capture the total number of true predictions
    and false predictions pixels.
    """

    def __init__(self):

        # A list containing the strings or integers of unique labels.
        self.__labels = list()
        # A list containing the SegmentationLabelData objects for each label.
        self.__stats = list()

    @property
    def labels(self) -> list:
        """
        Attribute to access the list of unique labels found.

        Returns
        -------
        list
            This contains unique labels found during validation.
        """
        return self.__labels

    @labels.setter
    def labels(self, new_labels: list):
        """
        Sets the list of unique labels found during validation.

        Parameters
        ----------
        new_labels: list
            This is the list of unique labels found during validation.
        """
        self.__labels = new_labels

    @property
    def stats(self) -> List[SegmentationLabelData]:
        """
        Attribute to access the stats which contains SegmentationLabelData
        objects needed to compute EdgeFirst metrics.

        Returns
        -------
        List[SegmentationLabelData]
            This list contains SegmentationLabelData objects where each
            object tracks the metrics of a specific label.
        """
        return self.__stats

    @stats.setter
    def stats(self, stat: List[SegmentationLabelData]):
        """
        Sets the stats to a new value.

        Parameters
        ----------
        stat: List[SegmentationLabelData]
            These are the stats to set.
        """
        self.__stats = stat

    def get_label_data(
        self,
        label: Union[str, int, np.integer]
    ) -> Union[SegmentationLabelData, None]:
        """
        Grabs the SegmentationLabelData object by the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            A unique string label or integer index to
            fetch the LabelData container.

        Returns
        -------
        Union[SegmentationLabelData, None]
            The data container of the label specified if
            it exists. None if the label does not exist.
        """
        for label_data in self.stats:
            if label_data.label == label:
                return label_data
        return None

    def add_label_data(self, label: Union[str, int, np.integer]):
        """
        Adds a SegmentationLabelData object for the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            The string label or the integer index
            to place as a data container.
        """
        self.stats.append(SegmentationLabelData(label))

    def capture_class(
        self,
        class_labels: Union[list, np.ndarray],
        labels: List[str] = None
    ):
        """
        Records the unique labels encountered in the prediction and
        ground truth and creates a container (SegmentationLabelData)
        for the label found in the model predictions and ground truth.

        Parameters
        ----------
        class_labels: list of int.
            All unique indices for the classes found from the ground
            truth and the model prediction masks.
        labels: list
            This list contains unique string labels for the classes found.
            This is optional to convert the integer labels into string
            labels.
        """
        for label in class_labels:
            if labels is not None:
                label: str = labels[label]
                if label.lower() in [" ", ""]:
                    continue
            if label not in self.labels:
                self.add_label_data(label)
                self.labels.append(label)

    def reset(self):
        """
        Resets the containers to an empty list
        and resets the labels captured to an empty list.
        """
        self.stats, self.labels = list(), list()


class PoseStats:
    """
    This is a container for PoseLabelData objects which
    contains angles for either roll, pitch, yaw.

    Raises
    ------
    ValueError
        Raised if the detected angle name was never stored as a
        container. Also if the lengths of ground truth and
        prediction angles are not matching.
    """

    def __init__(self):

        # A list containing the strings or integers of unique labels.
        self.__labels = list()
        # A list containing the SegmentationLabelData objects for each label.
        self.__stats = list()

    @property
    def labels(self) -> list:
        """
        Attribute to access the list of unique angle names gathered.

        Returns
        -------
        list
            This contains unique angle names gathered during validation.
        """
        return self.__labels

    @labels.setter
    def labels(self, new_labels: list):
        """
        Sets the list of unique angle names gathered during validation.

        Parameters
        ----------
        new_labels: list
            This is the list of unique angle names found during validation.
        """
        self.__labels = new_labels

    @property
    def stats(self) -> List[PoseLabelData]:
        """
        Attribute to access the stats which contains PoseLabelData
        objects needed to compute EdgeFirst metrics.

        Returns
        -------
        List[PoseLabelData]
            This list contains PoseLabelData objects where each
            object tracks the metrics of a specific label.
        """
        return self.__stats

    @stats.setter
    def stats(self, stat: List[PoseLabelData]):
        """
        Sets the list of PoseLabelData objects.

        Parameters
        ----------
        stat: List[PoseLabelData]
            These are the stats to set.
        """
        self.__stats = stat

    def get_label_data(
        self,
        label: Union[str, int, np.integer]
    ) -> Union[PoseLabelData, None]:
        """
        Grabs the PoseLabelData object by the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            A unique string label or integer index to
            fetch the LabelData container.

        Returns
        -------
        Union[PoseLabelData, None]
            The data container of the label specified if
            it exists. None if the label does not exist.
        """
        for label_data in self.stats:
            if label_data.label == label:
                return label_data
        return None

    def add_label_data(self, label: Union[str, int, np.integer]):
        """
        Adds a PoseLabelData object for the label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            The string label or the integer index
            to place as a data container.
        """
        self.stats.append(PoseLabelData(label))

    def reset(self):
        """
        Resets the containers to an empty list
        and resets the labels captured to an empty list.
        """
        self.stats, self.labels = list(), list()

    def capture_angle_names(self, name: Union[str, int, np.integer]):
        """
        Creates a PoseLabelData object based on the
        provided angle name if it does not exist yet.

        Parameters
        ----------
        name: Union[str, int, np.integer]
            The name of the angle.
        """
        if name not in self.labels:
            self.add_label_data(name)
            self.labels.append(name)

    def store_angle(
        self,
        name: Union[str, int, np.integer],
        gt_angle: float,
        dt_angle: float
    ):
        """
        Stores the angle in the object with the specified name.

        Parameters
        ----------
        name: str or int
            The name of the angle.
        gt_angle: float
            The ground truth angle.
        dt_angle: float
            The prediction angle.

        Raises
        ------
        ValueError
            Raised if the detected angle name was never stored as a container.
        """
        pose_data = self.get_label_data(name)
        if pose_data is None:
            raise ValueError(
                f"No PoseDataLabel container is associated with this angle: {name}")
        pose_data.add_y_pred(dt_angle)
        pose_data.add_y_true(gt_angle)

    def store_angles(
        self,
        dt_angles: Union[list, np.ndarray],
        gt_angles: Union[list, np.ndarray]
    ):
        """
        Evaluates the lengths of the provided angles.
        If it is three it assumes the angles are roll, pitch, and yaw.
        If it is four, it assumes the angles are quaternion.
        Also provides flexibility for other angle lengths, but names
        them as angle_1, angle_2, etc..

        Parameters
        ----------
        dt_angles: Union[list, np.ndarray]
            An array that contains the detection angles.
        gt_angles: Union[list, np.ndarray]
            An array that contains the ground truth angles.

        Raises
        ------
        ValueError
            The lengths of ground truth and prediction angles are not matching.
        """
        if len(gt_angles) != len(dt_angles):
            raise ValueError("The lengths of the provided angles for " +
                             "prediction and ground truth are not the same.")

        # Euler angles.
        if len(gt_angles) == 3:
            for name, dt_angle, gt_angle in zip(
                    ["roll", "pitch", "yaw"], dt_angles, gt_angles):
                self.capture_angle_names(name)
                self.store_angle(name, gt_angle, dt_angle)

        # No angles were captured for both prediction and ground truth.
        elif len(gt_angles) == 0:
            for name in ["roll", "pitch", "yaw"]:
                self.capture_angle_names(name)
                self.store_angle(name, np.nan, np.nan)

        # Quaternion angles.
        elif len(gt_angles) == 4:
            for name, dt_angle, gt_angle in zip(
                    ["real", "i", "j", "k"], dt_angles, gt_angles):
                self.capture_angle_names(name)
                self.store_angle(name, gt_angle, dt_angle)
        else:
            for i, (dt_angle, gt_angle) in enumerate(
                    zip(dt_angles, gt_angles)):
                self.capture_angle_names("angle_{}".format(i))
                self.store_angle("angle_{}".format(i), gt_angle, dt_angle)
