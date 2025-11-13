from typing import Union

import numpy as np

from edgefirst.validator.datasets.instance import Instance


class DetectionInstance(Instance):
    """
    Instance for storing ground truth and
    model bounding boxes, labels, and scores.

    Parameters
    ----------
    image_path: str
        The path to the image for Darknet datasets. Otherwise this is the
        image name for TFRecord datasets. This is required either to
        allow reading the image from file or saving the image results
        in disk with the same file name.
    """

    def __init__(self, image_path: str):
        super(DetectionInstance, self).__init__(image_path)

        # These are the 2D bounding boxes in either YOLO, COCO, or PascalVoc.
        self.__boxes = np.array([])
        # These contain either string or integer labels per bounding box.
        self.__labels = np.array([])
        # These contain the prediction scores per bounding box. Empty if gt.
        self.__scores = np.array([])
        # These contain either 2D (x, y) or 3D (x, y, z) bounding box centers.
        self.__centers = np.array([])

    @property
    def boxes(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the 2D bounding boxes for detection.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the 2D normalized bounding boxes.
        """
        return self.__boxes

    @boxes.setter
    def boxes(self, boxes_2d: Union[list, np.ndarray]):
        """
        Sets the 2D bounding boxes to a new value.

        Parameters
        ----------
        boxes_2d: Union[list, np.ndarray]
            These are the 2D bounding boxes to set.
        """
        self.__boxes = boxes_2d

    def append_boxes(self, box: Union[list, np.ndarray]):
        """
        Appends list or stacks NumPy array 2D bounding boxes.

        Parameters
        ----------
        box: Union[list, np.ndarray]
            This is the 2D normalized bounding box in either YOLO, COCO,
            or PascalVoc.
        """
        if isinstance(self.__boxes, np.ndarray):
            self.__boxes = np.vstack([self.__boxes, box])
        else:
            self.__boxes.append(box)

    @property
    def labels(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the labels per bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the labels per bounding box.
        """
        return self.__labels

    @labels.setter
    def labels(self, new_labels: Union[list, np.ndarray]):
        """
        Sets the labels to a new value.

        Parameters
        ----------
        new_labels: Union[list, np.ndarray]
            These are the labels to set.
        """
        self.__labels = new_labels

    def append_labels(self, label: Union[str, int, np.integer]):
        """
        Appends list or appends NumPy array label.

        Parameters
        ----------
        label: Union[str, int, np.integer]
            This is the label to append to the list.
        """
        if isinstance(self.__labels, np.ndarray):
            self.__labels = np.append(self.__labels, label)
        else:
            self.__labels.append(label)

    @property
    def scores(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the scores per bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the scores per bounding box.
        """
        return self.__scores

    @scores.setter
    def scores(self, new_scores: Union[list, np.ndarray]):
        """
        Sets the scores to a new value.

        Parameters
        ----------
        new_scores: Union[list, np.ndarray]
            These are the scores to set.
        """
        self.__scores = new_scores

    def append_scores(self, score: float):
        """
        Appends list or appends NumPy array scores.

        Parameters
        ----------
        score: float
            This is the score to append to the list.
        """
        if isinstance(self.__scores, np.ndarray):
            self.__scores = np.append(self.__scores, score)
        else:
            self.__scores.append(score)

    @property
    def centers(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the centers per 2D or 3D bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the centers per 2D (x, y) or 3D (x, y, z) bounding box.
        """
        return self.__centers

    @centers.setter
    def centers(self, new_centers: Union[list, np.ndarray]):
        """
        Sets the centers to a new value.

        Parameters
        ----------
        new_centers: Union[list, np.ndarray]
            These are the centers to set.
        """
        self.__centers = new_centers


class Detection3DInstance(DetectionInstance):
    """
    Instance for storing 3D validation properties in the
    ground truth or model predictions.
    """

    def __init__(self, image_path: str):
        super(Detection3DInstance, self).__init__(image_path)

        # These contain the 3D bounding box size (width, height, length).
        self.__sizes = list()
        # These contain the angles to rotate the 3D bounding box in the y-axis.
        self.__box_angles = list()
        # These contain the view calibration matrix for
        # 3D bounding box conversion to corners.
        self.__calibration = list()
        # These contain the 3D bounding box corners (3,8).
        self.__corners = list()

    @property
    def sizes(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the sizes per 3D bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the size per
            3D bounding box in [width, height, length].
        """
        return self.__sizes

    @sizes.setter
    def sizes(self, new_sizes: Union[list, np.ndarray]):
        """
        Sets the sizes to a new value.

        Parameters
        ----------
        new_sizes: Union[list, np.ndarray]
            These are the size to set.
        """
        self.__sizes = new_sizes

    @property
    def box_angles(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the angles per 3D bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the angles per 3D bounding box in radians to
            perform rotation around the y-axis. The y-axis would be
            pointing upwards, the x-axis is either left/right, and the
            z-axis is in/out of the page.
        """
        return self.__box_angles

    @box_angles.setter
    def box_angles(self, new_box_angles: Union[list, np.ndarray]):
        """
        Sets the box_angles to a new value.

        Parameters
        ----------
        new_box_angles: Union[list, np.ndarray]
            These are the box_angles to set.
        """
        self.__box_angles = new_box_angles

    @property
    def calibration(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the calibration per 3D bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the view matrix to transform
            the 3D bounding box centers into respective
            corners that can be drawn on the image.
        """
        return self.__calibration

    @calibration.setter
    def calibration(self, new_calibration: Union[list, np.ndarray]):
        """
        Sets the calibration to a new value.

        Parameters
        ----------
        new_calibration: Union[list, np.ndarray]
            This is the calibration to set.
        """
        self.__calibration = new_calibration

    @property
    def corners(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the corners per 3D bounding box.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the corners of the 3D bounding box with shape
            (3,8) representing the (x,y,z) 8 corners of a 3D box.

            The following points are:
                P1: top, left, front corner
                P2: top, right, front corner
                P3: top, right, back corner
                P4: top, left, back corner
                P5: bottom, left, front corner
                P6: bottom, right, front corner
                P7: bottom, right, back corner
                P8: bottom, left, back corner
        """
        return self.__corners

    @corners.setter
    def corners(self, new_corners: Union[list, np.ndarray]):
        """
        Sets the corners to a new value.

        Parameters
        ----------
        new_corners: Union[list, np.ndarray]
            This is the corners to set.
        """
        self.__corners = new_corners


class RadarDetectionInstance(DetectionInstance):
    """
    Instance for storing Radar validation properties for the
    ground truth and model predictions.

    Parameters
    ----------
    image_path: str
        The path to the image for Darknet datasets. Otherwise this is the
        image name for TFRecord datasets. This is required either to
        allow reading the image from file or saving the image results
        in disk with the same file name.
    """

    def __init__(self, image_path: str):
        super(RadarDetectionInstance, self).__init__(image_path)

        self.__cube = np.array([])

    @property
    def cube(self) -> np.ndarray:
        """
        Attribute to access the Radar cube.

        Returns
        -------
        np.ndarray
            This contains the Radar cube.
        """
        return self.__cube

    @cube.setter
    def cube(self, new_cube: np.ndarray):
        """
        Sets the Radar cube to a new value.

        Parameters
        ----------
        new_cube: np.ndarray
            This is the Radar cube to set.
        """
        self.__cube = new_cube
