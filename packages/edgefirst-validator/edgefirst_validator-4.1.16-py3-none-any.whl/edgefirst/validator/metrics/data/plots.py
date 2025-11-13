import numpy as np


class Plots:
    """
    Container used to store the data needed for
    plotting the validation charts.

    Parameters
    ----------
    labels: list
        A list of unique string labels to
        initialize the confusion matrix.
    """

    def __init__(self, labels: list = []):
        self.labels = labels
        self.reset()

    @property
    def class_histogram_data(self) -> dict:
        """
        Attribute to access the class histogram data.

        Returns
        -------
        dict
            This contains the data for the class histogram.
        """
        return self.__class_histogram_data

    @class_histogram_data.setter
    def class_histogram_data(self, data: dict):
        """
        Sets the data for the class histogram to a new value.

        Parameters
        ----------
        data: dict
            This is the class histogram data to set.
            This should be a dictionary with the following keys.

                .. code-block:: python

                    {
                        "precision": precision,
                        "recall": recall,
                        "accuracy": accuracy,
                        "tp": tp,
                        "fn": fn,
                        "fp": fp,
                        "gt": gt
                    }
        """
        self.__class_histogram_data = data

    def append_class_histogram_data(self, label: str, data: dict):
        """
        This adds another key to the class histogram data indicated as the
        class label and data contains the metrics of that label.

        Parameters
        ----------
        label: str
            This is the key of the dictionary that is the class label.
        data: dict
            This contains the metrics of the label. This should
            be a dictionary with the following keys.

                .. code-block:: python

                    {
                        "precision": precision,
                        "recall": recall,
                        "accuracy": accuracy,
                        "tp": tp,
                        "fn": fn,
                        "fp": fp,
                        "gt": gt
                    }
        """
        self.__class_histogram_data[label] = data

    @property
    def confusion_labels(self) -> list:
        """
        Attribute to access the confusion matrix unique labels.

        Returns
        -------
        list
            This contains the labels for the confusion matrix.
        """
        return self.__confusion_labels

    @confusion_labels.setter
    def confusion_labels(self, labels: list):
        """
        Sets the labels for the confusion matrix to a new value.

        Parameters
        ----------
        labels: list
            These are the confusion matrix labels to set.
        """
        self.__confusion_labels = labels

    @property
    def confusion_matrix(self) -> np.ndarray:
        """
        Attribute to access the confusion matrix.

        Returns
        -------
        np.ndarray
            This contains the confusion matrix.
        """
        return self.__confusion_matrix

    @confusion_matrix.setter
    def confusion_matrix(self, matrix: np.ndarray):
        """
        Sets the confusion matrix to a new value.

        Parameters
        ----------
        matrix: :py:class:`np.ndarray`
            This is the confusion matrix to set.
        """
        self.__confusion_matrix = matrix

    def initialize_confusion_matrix(self):
        """
        Initialize the confusion matrix array.
        """
        labels = self.labels
        # Insert the background class in the confusion matrix if it doesn't
        # exist.
        if not any(s.lower() == "background" for s in self.labels):
            labels = ["background"] + self.labels

        self.confusion_labels = labels
        # Rows = predictions, columns = ground truth
        self.confusion_matrix = np.zeros(
            (len(labels), len(labels)), dtype=np.int32)

    @property
    def px(self) -> np.ndarray:
        """
        Attribute to access px.

        Returns
        -------
        np.ndarray
            Precision vs Recall Curve 1000-point interpolated px values
            representing recall.
        """
        return self.__px

    @px.setter
    def px(self, this_px: np.ndarray):
        """
        Sets px to a new value.

        Parameters
        ----------
        px: np.ndarray
            The px values to set.
        """
        self.__px = this_px

    @property
    def py(self) -> np.ndarray:
        """
        Attribute to access py.

        Returns
        -------
        np.ndarray
            Precision vs Recall Curve 1000-point interpolated py values
            representing precision.
        """
        return self.__py

    @py.setter
    def py(self, this_py: np.ndarray):
        """
        Sets py to a new value.

        Parameters
        ----------
        py: np.ndarray
            The py values to set.
        """
        self.__py = this_py

    @property
    def precision(self) -> np.ndarray:
        """
        Attribute to access the array of precision values.

        Returns
        -------
        np.ndarray
            This contains the data for the precision recall curve.
        """
        return self.__precision

    @precision.setter
    def precision(self, data: np.ndarray):
        """
        Sets the data for the precision values.

        Parameters
        ----------
        data: :py:class:`np.ndarray`
            These are the precision values to set.

            This data should be formatted as the following:
            (nc x thresholds) so each row are for a unique class and
            each column is the precision value for each score threshold.
        """
        self.__precision = data

    @property
    def recall(self) -> np.ndarray:
        """
        Attribute to access the array of recall values.

        Returns
        -------
        np.ndarray
            This contains the data for the precision recall curve.
        """
        return self.__recall

    @recall.setter
    def recall(self, data: np.ndarray):
        """
        Sets the data for the recall values.

        Parameters
        ----------
        data: np.ndarray
            These are the recall values to set.

            This data should be formatted as the following:
            (nc x thresholds) so each row are for a unique class and
            each column is the recall value for each score threshold.
        """
        self.__recall = data

    @property
    def f1(self) -> np.ndarray:
        """
        Attribute to access the array of F1 values.

        Returns
        -------
        np.ndarray
            This contains the data for the precision-f1 curve.
        """
        return self.__f1

    @f1.setter
    def f1(self, data: np.ndarray):
        """
        Sets the data for the F1 values.

        Parameters
        ----------
        data: np.ndarray
            These are the F1 values to set.

            This data should be formatted as the following:
            (nc x thresholds) so each row are for a unique class and
            each column is the F1 value for each score threshold.
        """
        self.__f1 = data

    @property
    def average_precision(self) -> np.ndarray:
        """
        Attribute to access the array of average precision values.

        Returns
        -------
        np.ndarray
            This contains the data for the precision recall curve.
        """
        return self.__average_precision

    @average_precision.setter
    def average_precision(self, data: np.ndarray):
        """
        Sets the data for the average precision values.

        Parameters
        ----------
        data: np.ndarray
            These are the average precision values to set.

            This data should be formatted as the following:
            (nc x 10) so each row are for a unique class and
            each column is the precision at 10 different IoU threshold from
            0.50 to 0.95 in 0.05 intervals with a static score threshold
            set from the command line.
        """
        self.__average_precision = data

    @property
    def curve_labels(self) -> list:
        """
        Attribute to access the precision recall curve unique labels.

        Returns
        -------
        list
            This contains the labels for the precision recall curve.
        """
        return self.__curve_labels

    @curve_labels.setter
    def curve_labels(self, labels: list):
        """
        Sets the labels for the precision recall curve to a new value.

        Parameters
        ----------
        labels: list
            These are the precision recall curve labels to set.
        """
        self.__curve_labels = labels

    @property
    def tp_scores(self) -> list:
        """
        Attribute to access the confidence scores of true positive detections.

        Returns
        -------
        list
            A list containing the scores assigned to true positive detections.
        """
        return self.__tp_scores

    @tp_scores.setter
    def tp_scores(self, scores: list):
        """
        Sets the confidence scores for true positive detections.

        Parameters
        ----------
        scores: list
            A list of confidence scores to assign to true positive detections.
        """
        self.__tp_scores = scores

    @property
    def fp_scores(self) -> list:
        """
        Attribute to access the confidence scores of false positive detections.

        Returns
        -------
        list
            A list containing the scores assigned to false positive detections.
        """
        return self.__fp_scores

    @fp_scores.setter
    def fp_scores(self, scores: list):
        """
        Sets the confidence scores for false positive detections.

        Parameters
        ----------
        scores: list
            A list of confidence scores to assign to false positive detections.
        """
        self.__fp_scores = scores

    @property
    def tp_ious(self):
        """
        Attribute to access the IoU values for true positive detections.

        Returns
        -------
        list
            A list containing Intersection-over-Union (IoU) values for true positives.
        """
        return self.__tp_ious

    @tp_ious.setter
    def tp_ious(self, ious: list):
        """
        Sets the IoU values for true positive detections.

        Parameters
        ----------
        ious: list
            A list of IoU values to assign to true positive detections.
        """
        self.__tp_ious = ious

    def reset(self):
        """
        Resets the containers for the data use to plot.
        """
        self.__class_histogram_data = dict()

        """Confusion Matrix Data"""
        self.__confusion_labels = list()
        self.__confusion_matrix = list()

        """Precision Recall Curve"""
        self.__px = np.array([])
        self.__py = np.array([])
        self.__precision = list()
        self.__recall = list()
        self.__f1 = list()
        self.__average_precision = list()
        self.__curve_labels = list()

        """TP vs FP scores"""
        self.__tp_scores = list()
        self.__fp_scores = list()
        self.__tp_ious = list()


class MultitaskPlots:
    """
    A container for both detection and segmentation
    plots for Multitask validation.

    Parameters
    -----------
    detection_plots: Plots
        Detection plots container.
    segmentation_plots: Plots
        Segmentation plots container.
    """

    def __init__(self, detection_plots: Plots, segmentation_plots: Plots):
        self.detection_plots = detection_plots
        self.segmentation_plots = segmentation_plots
