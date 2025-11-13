from typing import Union

import numpy as np

from edgefirst.validator.datasets.instance import DetectionInstance


class PoseInstance(DetectionInstance):
    """
    Instance container for storing head pose ground truth or
    model prediction properties.

    Parameters
    ----------
    image_path: str
        The path to the image for Darknet datasets. Otherwise this is the
        image name for TFRecord datasets. This is required either to
        allow reading the image from file or saving the image results
        in disk with the same file name.
    """

    def __init__(self, image_path: str):
        super(PoseInstance, self).__init__(image_path)

        # These contain the pose angles
        self.__pose_angles = list()

    @property
    def pose_angles(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the pose angles.

        Returns
        -------
        Union[list, np.ndarray]
            This contains the angles for pose in radians which is the
            [yaw, pitch, roll].
        """
        return self.__pose_angles

    @pose_angles.setter
    def pose_angles(self, new_pose_angles: Union[list, np.ndarray]):
        """
        Sets the pose_angles to a new value.

        Parameters
        ----------
        new_pose_angles: Union[list, np.ndarray]
            These are the pose_angles to set.
        """
        self.__pose_angles = new_pose_angles
