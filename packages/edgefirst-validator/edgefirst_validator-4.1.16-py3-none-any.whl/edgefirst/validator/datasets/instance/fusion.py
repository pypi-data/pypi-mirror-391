from edgefirst.validator.datasets.instance import Instance


class FusionInstance(Instance):
    """
    Instance container for storing Fusion validation of ground truth and
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
        super(FusionInstance, self).__init__(image_path)

        raise NotImplementedError(
            "This type of Instance container is not yet implemented.")
