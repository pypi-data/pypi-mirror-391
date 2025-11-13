import os

from edgefirst.validator.datasets.instance import (Instance, DetectionInstance,
                                                   RadarDetectionInstance,
                                                   SegmentationInstance,
                                                   Detection3DInstance,
                                                   MultitaskInstance,
                                                   FusionInstance,
                                                   PoseInstance)
from edgefirst.validator.datasets.core import Dataset, BaseDataset
from edgefirst.validator.datasets.tfrecord import TFRecordDataset
from edgefirst.validator.datasets.darknet import DarkNetDataset
from edgefirst.validator.datasets.arrow import ArrowDataset
from edgefirst.validator.datasets.database import (Database, EdgeFirstDatabase,
                                                   DarknetDatabase, LMDBDatabase)
from edgefirst.validator.datasets.cache import StudioCache

from edgefirst.validator.datasets.utils.fetch import download_and_extract
from edgefirst.validator.publishers.utils.logger import logger


def instantiate_dataset(
    info_dataset: dict,
    parameters,
) -> Dataset:
    """
    This function instantiates either darknet or tfrecord
    format dataset objects.

    Parameters
    ----------
    info_dataset: dict
        If the dataset is Darknet, this contains information such as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "type": "darknet",
                    "validation":
                    {
                        "images: 'path to the images',
                        "annotations": 'path to the annotations'
                    },
                }

        *Note: the classes are optional and the path to the images
        and annotations can be the same.*

        If the dataset is tfrecord, this contains information such as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "validation": {
                        "path": path to the *.tfrecord files.
                    }
                }
    parameters: DatasetParameters
        A container for the dataset parameters set from the command line.

    Returns
    -------
    Dataset
        This object is returned depending on the type of the dataset provided.

    Raises
    ------
    InvalidDatasetSourceException
        Raised if the path to the images or annotations is None.
    DatasetNotFoundException
        Raised if the provided path to the images or
        annotations does not exist.
    ValueError
        Raised if the provided path to the images or
        annotations is not a string.
    EmptyDatasetException
        Raised if the provided path to the images or
        text files does not contain any image files or
        text files respectively.
    """
    if isinstance(info_dataset, dict):
        if "download" in info_dataset.keys():
            url = info_dataset.get("download")
            download_path = os.path.join(os.getcwd(),
                                         f"samples/{os.path.basename(url)}")
            if not os.path.exists(download_path):
                download_and_extract(url=url, download_path=download_path)

        try:
            ds_format = info_dataset.get('type')
            if ds_format is None:
                ds_format = info_dataset.get("dataset").get("format")
        except AttributeError:
            logger("Dataset was not properly read. Ensure the dataset " +
                   "structure follows images/validate and labels/validate.",
                   code="ERROR")
        if ds_format in [None, "tfrecord"]:
            return TFRecordDataset(
                source=parameters.dataset_path,
                parameters=parameters,
                info_dataset=info_dataset,
            )
        elif ds_format == "darknet":
            return DarkNetDataset(
                source=parameters.dataset_path,
                parameters=parameters,
                info_dataset=info_dataset,
            )
        elif ds_format == "arrow":
            return ArrowDataset(
                source=parameters.dataset_path,
                parameters=parameters,
                info_dataset=info_dataset,
            )
        elif ds_format == "lmdb":
            return LMDBDatabase(
                source=parameters.dataset_path,
                parameters=parameters
            )
        elif ds_format == "edgefirst":
            return EdgeFirstDatabase(
                source=parameters.dataset_path,
                parameters=parameters,
            )
    else:
        return BaseDataset(
            source=parameters.dataset_path,
            iterator=info_dataset
        )
