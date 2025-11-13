import os

from edgefirst.validator.datasets.utils.transformations import clamp
from edgefirst.validator.publishers.utils.logger import set_silent_condition


class ValidationParameters:
    """
    Container for validation parameters used for
    specifying additional settings for validation.

    Parameters
    ----------
    validate_type: str
        The validation task depending on the type of model. Options
        could be one of the following: "vision" or "fusion".
    method: str
        Reproducing validation results reported by Ultralytics by default. Specify
        validation method seen in other sources such as YOLOv7. Options could
        be "ultralytics" for the official validator from Ultralytics which
        supports YOLOv5, YOLOv8, and YOLOv11. However, there are variations
        such as "yolov7" for YOLOv7 and "edgefirst" for internal Au-Zone implementations.
    iou_threshold: float
        This is the threshold for the validation IoU which distinguish
        matched detections as either true positives or localization
        false positives. Localization false positives have an IoU below this
        threshold. Default is set to 0.50.
    score_threshold: float
        This is the threshold for validation score which provides
        extra score filtering of the predictions.
    metric: str
        The type of metric to use in the matching algorithm. Options could
        be one of the following: "iou" or "centerpoint". Using either the
        intersection over union with highest overlap as being the best matches
        or centerpoint distance with the closest distance being the best matches.
        Default is set to "iou".
    matching_leniency: int
        Distance metric to be considered a valid match when using the "centerpoint"
        metric. Default is 2 where the distance is no more than twice the
        size of the bounding box.
    clamp_boxes: int
        Clamp bounding boxes for the minimum size as this value set. By default
        this setting is not specified.
    ignore_boxes: int
        Ignore bounding boxes with sizes less than this value set. By default
        this setting is not specified.
    display: int
        Specify the limit of the number of visualization results to display.
        By default it is set to -1 which means all samples in the dataset.
    plots: bool
        Specify whether to save the validation plots. This is only effective
        when setting the visualization or the tensorboard parameters to a path.
        By default it is set to True which means to save the plots.
    silent: bool
        Specify whether to suppress validation updates on the terminal. This is
        useful when using the validator as an API to prevent any output messages.
    visualize: str
        Specify the path to store the validation results in disk.
    tensorboard: str
        Specify the path to output the tensorboard file for visualization
        using tensorboar.d
    json_out: str
        Specify the path to output the JSON files storing the validation results.
    include_background: bool
        For segmentation validation, specifying to True includes the background
        class in the metrics which will ultimately increase the metric outcomes
        since most of the pixels in the image are from the background class.
    **kwargs: dict
        Define extra arguments as part of the validation parameters.
    """

    def __init__(
        self,
        validate_type: str = "vision",
        method: str = "ultralytics",
        iou_threshold: float = 0.50,
        score_threshold: float = 0.00,
        metric: str = "iou",
        matching_leniency: int = 2,
        clamp_boxes: int = None,
        ignore_boxes: int = None,
        display: int = -1,
        plots: bool = True,
        silent: bool = False,
        visualize: str = None,
        tensorboard: str = None,
        json_out: str = None,
        include_background: bool = False,
        **kwargs: dict
    ):
        self.__validate_type = validate_type.lower()
        self.__method = method.lower()
        self.__iou_threshold = iou_threshold
        self.__score_threshold = score_threshold
        self.__metric = metric.lower()
        self.__matching_leniency = matching_leniency
        self.__clamp_boxes = clamp_boxes
        self.__ignore_boxes = ignore_boxes
        self.__display = display
        self.__plots = plots
        self.__silent = silent
        self.__visualize = visualize
        self.__tensorboard = tensorboard
        self.__json_out = json_out
        self.__include_background = include_background

        if visualize:
            if not os.path.exists(visualize):
                os.makedirs(visualize, exist_ok=True)

        if tensorboard:
            if not os.path.exists(tensorboard):
                os.makedirs(tensorboard, exist_ok=True)

        if json_out:
            if not os.path.exists(json_out):
                os.makedirs(json_out, exist_ok=True)

    @property
    def validate_type(self) -> str:
        """
        Attribute to access the validate type.
        Specifies the type of validation tasks. Options could be one of the
        following: "vision" or "fusion".

        Returns
        -------
        str
            The validation type.
        """
        return self.__validate_type

    @validate_type.setter
    def validate_type(self, validate: str):
        """
        Sets the validation type.

        Parameters
        ----------
        validate: str
            The type of validation to set.
        """
        self.__validate_type = validate.lower() if validate is not None else validate

    @property
    def method(self) -> str:
        """
        Attribute to access validation methods.
        Specifies the validation method to
        reproduce in EdgeFirst Validator. By default the "ultralytics" methods
        seen in YOLOv5, YOLOv8, and YOLOv11 are used. However, other variations
        such as "yolov7" from YOLOv7 and "edgefirst" for internal Au-Zone
        implementations are also possible.
        """
        return self.__method

    @method.setter
    def method(self, methods: str):
        """
        Sets the validation method.

        Parameters
        ----------
        methods: str
            The validation method to reproduce.
            Options include "ultralytics", "yolov7", or "edgefirst".
        """
        self.__method = methods.lower() if methods is not None else methods

    @property
    def iou_threshold(self) -> float:
        """
        Attribute to access the validation IoU threshold.
        This metric is used to classify matched detections as either
        true positives or false positives. Detections with IoUs below this
        threshold will be classified as localization false positives.

        Returns
        -------
        float:
             The validation IoU threshold.
        """
        return self.__iou_threshold

    @iou_threshold.setter
    def iou_threshold(self, iou: float):
        """
        Sets the validation IoU threshold.

        Parameters
        ----------
        iou: float
            The validation IoU threshold to set.
        """
        self.__iou_threshold = clamp(iou)

    @property
    def score_threshold(self) -> float:
        """
        Attribute to access the validation score threshold.
        This metric is used as an extra filter of the score threshold
        by keeping predictions with scores greater than or equal to this
        set threshold.

        Returns
        -------
        float:
             The validation score threshold.
        """
        return self.__score_threshold

    @score_threshold.setter
    def score_threshold(self, score: float):
        """
        Sets the validation score threshold.

        Parameters
        ----------
        iou: float
            The validation score threshold to set.
        """
        self.__score_threshold = clamp(score)

    @property
    def metric(self) -> str:
        """
        Attribute to access the metric type.
        This parameter is used to define which metric ("iou", "centerpoint")
        to use to match the predictions to ground truth.

        Returns
        -------
        str
            The metric type.
        """
        return self.__metric

    @metric.setter
    def metric(self, this_metric: str):
        """
        Sets the metric type.

        Parameters
        ----------
        this_metric: str
            The metric to set.
        """
        self.__metric = this_metric.lower() if this_metric is not None else this_metric

    @property
    def matching_leniency(self) -> int:
        """
        Attribute to access the leniency factor
        for center distance calculations.

        Returns
        -------
        int
            The leniency factor. This is a criteria to consider
            center distances if the number of times the diagonal
            (center to corner) of the smallest bounding box fits within the
            box to box center distance does not exceed the leniency factor.

        """
        return self.__matching_leniency

    @matching_leniency.setter
    def matching_leniency(self, leniency_factor: int):
        """
        Sets the leniency factor. This is a criteria to consider
        center distances if the number of times the diagonal
        (center to corner) of the smallest bounding box fits within the
        box to box center distance does not exceed the leniency factor.

        Parameters
        ----------
        leniency_factor: int
            The leniency_factor to set.
        """
        self.__matching_leniency = leniency_factor

    @property
    def clamp_boxes(self) -> int:
        """
        Attribute to access clamp boxes.
        This is used to specify the lowest limit for the
        box dimensions in pixels. Any box dimensions (height or width)
        lower than this setting will be resized to this setting.

        Returns
        -------
        int
            The pixel dimension to clamp.
        """
        return self.__clamp_boxes

    @clamp_boxes.setter
    def clamp_boxes(self, this_clamp_boxes: int):
        """
        Sets the clamp boxes.

        Parameters
        ----------
        this_clamp_boxes: int
            The clamp_boxes to set.
        """
        self.__clamp_boxes = this_clamp_boxes

    @property
    def ignore_boxes(self) -> int:
        """
        Attribute to access ignore boxes.
        Any box dimension (width or height) lower than this limit
        will be ignored from validation.

        Returns
        -------
        int
            The pixel dimension to ignore.
        """
        return self.__ignore_boxes

    @ignore_boxes.setter
    def ignore_boxes(self, this_ignore_boxes: int):
        """
        Sets the ignore boxes.

        Parameters
        ----------
        this_ignore_boxes: int
            The ignore_boxes to set.
        """
        self.__ignore_boxes = this_ignore_boxes

    @property
    def display(self) -> int:
        """
        Attribute to access display.
        Set the number of images to display showing results for validation.

        Returns
        -------
        int
            The number of images to display.
        """
        return self.__display

    @display.setter
    def display(self, this_display: int):
        """
        Sets the number of images to display.

        Parameters
        ----------
        this_display: int
            The display to set.
        """
        self.__display = this_display

    @property
    def plots(self) -> bool:
        """
        Attribute to access plots.
        Specify whether to draw validation plots or not.
        Validation plots include: Confusion Matrix, PR-curve, and
        classification histogram.

        Returns
        -------
        bool
            Condition to include plots.
        """
        return self.__plots

    @plots.setter
    def plots(self, this_plots: bool):
        """
        Specify to include validation plots.

        Parameters
        ----------
        this_plots: bool
            The plots to set.
        """
        self.__plots = this_plots

    @property
    def silent(self) -> bool:
        """
        Attribute to access the display flag.
        This is a flag to determine whether messages
        are printed to console. Does not print when silent is True.

        Returns
        -------
        bool
            Condition to disable validation logging.
        """
        return self.__silent

    @silent.setter
    def silent(self, silent: bool):
        """
        Sets a flag to determine whether messages are printed to console.
        Does not print when silent is True.

        Parameters
        ----------
        silent: bool
            This is the condition to disable validation logging.
        """
        self.__silent = silent
        set_silent_condition(silent)

    @property
    def visualize(self) -> str:
        """
        Attribute to access the visualize.
        This is the path to store the validation results which
        includes images.

        Returns
        -------
        str
            The path to save validation results.
        """
        return self.__visualize

    @visualize.setter
    def visualize(self, this_visualize: str):
        """
        Sets the path to save the validation results in disk.

        Parameters
        ----------
        this_visualize: str
            The visualize to set.
        """
        if not os.path.exists(this_visualize):
            os.makedirs(this_visualize)
        self.__visualize = this_visualize

    @property
    def tensorboard(self) -> str:
        """
        Attribute to access the tensorboard.
        This is the path to store the validation results which includes
        tfevent files to be loaded using tensorboard.

        Returns
        -------
        str
            The path to save validation results.
        """
        return self.__tensorboard

    @tensorboard.setter
    def tensorboard(self, this_tensorboard: str):
        """
        Sets the path to save the validation results in a tfevents file.

        Parameters
        ----------
        this_tensorboard: str
            The tensorboard to set.
        """
        if not os.path.exists(this_tensorboard):
            os.makedirs(this_tensorboard)
        self.__tensorboard = this_tensorboard

    @property
    def json_out(self) -> str:
        """
        Attribute to access the json_out.
        This is the path to save the JSON files containing
        validation metrics and raw data to draw the plots.

        Returns
        -------
        str
            The path to save JSON files.
        """
        return self.__json_out

    @json_out.setter
    def json_out(self, this_json_out: str):
        """
        Sets the path to save the JSON files in disk.

        Parameters
        ----------
        this_json_out: str
            The path to the JSON files to set.

        Raises
        ------
        ValueError
            Raised if the parameter --json_out recieved an
            extension that is not a JSON file.
        """
        if not os.path.exists(this_json_out):
            os.makedirs(this_json_out, exist_ok=True)
        self.__json_out = this_json_out

    @property
    def include_background(self) -> bool:
        """
        Attribute to access include_background.
        Specify whether to include background as
        part of segmentation validation.

        Returns
        -------
        bool
            Condition to include background for segmentation validation.
        """
        return self.__include_background

    @include_background.setter
    def include_background(self, this_include_background: bool):
        """
        Specify to include background class for segmentation validation.

        Parameters
        ----------
        this_include_background: bool
            The include_background to set.
        """
        self.__include_background = this_include_background
