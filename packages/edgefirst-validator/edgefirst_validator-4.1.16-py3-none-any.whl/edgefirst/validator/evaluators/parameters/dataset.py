from __future__ import annotations

from typing import TYPE_CHECKING

from edgefirst.validator.evaluators.parameters import Parameters

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import CommonParameters


class DatasetParameters(Parameters):
    """
    Container for dataset parameters used for reading and fetching
    the validation dataset.

    Parameters
    ----------
    common_parameters: CommonParameters
        This represents the parameters that are common between
        model, dataset, and validation that should remain consistent across.
    dataset_path: str
        This is the path to the dataset directory or file (YAML or cache file).
    local_reader: bool
        Specify to use local validation methods for reading the dataset.
        Default to True. Otherwise, use deepview-datasets, when set to False.
    show_missing_annotations: bool
        Specify to print on the terminal the images without any ground truth
        annotations. Default to False.
    normalized: bool
        Specify whether the ground truth annotations are normalized to the
        image dimensions or not. Default to True.
    box_format: str
        The output bounding box format of the model. Options could be one
        of the following: "pascalvoc" as (xmin, ymin, xmax, ymax),
        "coco" as (xmin, ymin, width, height), or "yolo" as (xc, yc, width, height).
    labels: list
        A list of unique string labels which is part of the model artifacts
        for converting model output indices into strings.
    label_offset: int
        This is the offset to map the integer labels to string labels.
    **kwargs: dict
        Define extra arguments as part of the dataset parameters.
    """

    def __init__(
        self,
        common_parameters: CommonParameters,
        dataset_path: str = "Dataset",
        local_reader: bool = True,
        show_missing_annotations: bool = False,
        normalized: bool = True,
        box_format: str = "pascalvoc",
        labels_path: str = None,
        labels: list = None,
        label_offset: int = 0,
        **kwargs: dict
    ):
        super(DatasetParameters, self).__init__(
            labels_path=labels_path,
            labels=labels,
            label_offset=label_offset,
            box_format=box_format,
        )

        self.common = common_parameters
        self.__dataset_path = dataset_path
        self.__local_reader = local_reader
        self.__show_missing_annotations = show_missing_annotations
        self.__normalized = normalized

    @property
    def dataset_path(self) -> str:
        """
        Attribute to access the dataset_path.
        This is the path to the dataset directory or a dataset.yaml file.

        Returns
        -------
        str
            The path to the dataset.
        """
        return self.__dataset_path

    @dataset_path.setter
    def dataset_path(self, path: str):
        """
        Set the path to the dataset.

        Parameters
        ----------
        path: str
            The path to the dataset directory or dataset.yaml file.
        """
        self.__dataset_path = path

    @property
    def local_reader(self) -> bool:
        """
        Attribute to access local_reader.
        Specify whether reading the dataset relies on local validation
        methods. Otherwise, use deepview-datasets if set to False.

        Returns
        -------
        bool
            Condition for utilization of dataset local readers.
        """
        return self.__local_reader

    @local_reader.setter
    def local_reader(self, local: bool):
        """
        Specify condition for using local dataset readers

        Parameters
        ----------
        local: bool
            The condition to set.
        """
        self.__local_reader = local

    @property
    def show_missing_annotations(self) -> bool:
        """
        Attribute to access show_missing_annotations.
        Specify whether to print on the terminal the images without
        any ground truth annotations. By default set to False.

        Returns
        -------
        bool
            Condition for printing the images without any
            ground truth annotations. .
        """
        return self.__show_missing_annotations

    @show_missing_annotations.setter
    def show_missing_annotations(self, show: bool):
        """
        Specify condition for printing the images without
        any ground truth annotations.

        Parameters
        ----------
        show: bool
            The condition to set.
        """
        self.__show_missing_annotations = show

    @property
    def normalized(self) -> bool:
        """
        Attribute to access normalized.
        Specify whether the ground truth annotations are
        normalized to the image dimensions. Default to True.

        Returns
        -------
        bool
            Condition for printing the images without any
            ground truth annotations. .
        """
        return self.__normalized

    @normalized.setter
    def normalized(self, normalize: bool):
        """
        Specify condition of whether or not the ground truth
        annotations are normalized to the image dimensions.

        Parameters
        ----------
        normalize: bool
            The condition to set.
        """
        self.__normalized = normalize
