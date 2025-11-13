import numpy as np


class Instance:
    """
    Base Instance object for containing the ground truth dataset instance.

    Parameters
    ----------
    image_path: str
        The path to the image for Darknet datasets. Otherwise this is the
        image name for TFRecord datasets. This is required either to
        allow reading the image from file or saving the image results
        in disk with the same file name.
    """

    def __init__(self, image_path: str):
        self.__image_path = image_path
        # This is the NumPy array image.
        self.__image = None
        self.__height = 0
        self.__width = 0

        # Same property used in YOLOv5 and YOLOv7 for the shapes.
        self.__shapes = [
            [
                [0, 0],  # imgsz (model input shape) [height, width]
                # ratio_pad [[scale y, scale x], [pad w, pad h]]
                [(1.0, 1.0), (0.0, 0.0)]
            ],
            [1.0, 1.0]  # label ratio [x, y]
        ]
        self.__ratio = 1.0
        # The original image dimensions.
        self.__image_shape = None

    @property
    def image_path(self) -> str:
        """
        Attribute to access the image path/name.

        Returns
        -------
        str
            The image path/name.
        """
        return self.__image_path

    @image_path.setter
    def image_path(self, path: str):
        """
        Sets the image path/name.

        Parameters
        ----------
        path: str
            The image path/name.
        """
        self.__image_path = path

    @property
    def image(self) -> np.ndarray:
        """
        Attribute to access the image.

        Returns
        -------
        np.ndarray
            The image as a NumPy array.
        """
        return self.__image

    @image.setter
    def image(self, this_image: np.ndarray):
        """
        Sets the image array.

        Parameters
        ----------
        image: np.ndarray
            The image array.
        """
        self.__image = this_image

    @property
    def height(self) -> int:
        """
        Attribute to access the image height in pixels.

        Returns
        -------
        int
            The image height in pixels. 0 means uninitialized.
        """
        return self.__height

    @height.setter
    def height(self, image_height: int):
        """
        Sets the image height dimension to a new value.

        Parameters
        ----------
        image_height: int
            This is the new image height to set.
        """
        self.__height = image_height

    @property
    def width(self) -> int:
        """
        Attribute to access the image width in pixels.

        Returns
        -------
        int:
            The image width in pixels. 0 means uninitialized.
        """
        return self.__width

    @width.setter
    def width(self, image_width: int):
        """
        Sets the image width dimension to a new value.

        Parameters
        ----------
        image_width: int
            This is the new image width to set.
        """
        self.__width = image_width

    @property
    def shapes(self) -> list:
        """
        Attribute to access the inference shapes which includes
        the image shape after letterbox operation and aswell as padding
        and ratio which are variables that mirrors YOLOv5 and YOLOv7 implementation
        of the letterbox image processing. This attribute is used for bounding box
        rescaling for both the ground truth and detections.

        Returns
        -------
        list
            .. code-block:: python

                [
                    [image height, image width]],
                    [[ratio y, ratio x], [pad x, pad y]],
                    label_ratio
                ]
        """
        return self.__shapes

    @shapes.setter
    def shapes(self, shape: list):
        """
        Sets the shapes attribute to a new value.

        Parameters
        ----------
        shape: list
            .. code-block:: python

                [
                    [image height, image width]],
                    [[ratio y, ratio x], [pad x, pad y]],
                    label_ratio
                ]
        """
        self.__shapes = shape

    @property
    def ratio(self) -> float:
        """
        Attribute to access the ratio.
        This is the rescaling factor used for the bounding boxes to
        based on the letterbox and padding image transformations.

        Returns
        -------
        float
            Returns the ratio.
        """
        return self.__ratio

    @ratio.setter
    def ratio(self, this_ratio: float):
        """
        Sets the rescaling ratio.

        Parameters
        ----------
        this_ratio: float
            The rescaling ratio to set.
        """
        self.__ratio = this_ratio

    @property
    def image_shape(self) -> tuple:
        """
        Attribute to access the image shape.
        This is the original image dimensions prior
        to image preprocessing.

        Returns
        -------
        tuple
            This contains the image (height, width) dimensions.
        """
        return self.__image_shape

    @image_shape.setter
    def image_shape(self, shape: tuple):
        """
        Sets the image shape.

        Parameters
        ----------
        shape: tuple
            Sets the original image dimensions.
        """
        self.__image_shape = shape
