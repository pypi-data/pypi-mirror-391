"""
Implementations for downloading and caching the dataset.
"""

from __future__ import annotations

import os
import json
import glob
from typing import TYPE_CHECKING

import tqdm
import lmdb
import numpy as np

from edgefirst_client import Client, FileType, AnnotationType

from edgefirst.validator.datasets import EdgeFirstDatabase
from edgefirst.validator.publishers.utils.logger import logger

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters


class StudioCache:
    def __init__(
        self,
        parameters: DatasetParameters,
        client: Client,
        session_id: str = None,
        val_group: str = "val"
    ):
        """
        Communicate with EdgeFirst Studio for
        fetching and caching the dataset and post the progress.

        Parameters
        ----------
        parameters: DatasetParameters
            This contains dataset parameters set from the command line.
        client: Client
            EdgeFirst Client object.
        session_id: str
            This is the validation session ID in EdgeFirst Studio for
            posting validation metrics.
        val_group: str
            The dataset validation group set in EdgeFirst Studio.
        """

        self.parameters = parameters
        self.client = client
        self.edgefirst_dataset = None

        self.val_session = self.client.validation_session(session_id)
        self.val_task_id = self.val_session.task.id
        train_session_id = self.val_session.training_session_id
        self.train_session = self.client.training_session(train_session_id)

        self.val_group = val_group

    def download(self, dataset: str):
        """
        Download the dataset from EdgeFirst Studio into the device.

        Parameters
        ----------
        dataset: str
            The path to directory to save the dataset.

        Returns
        -------
        pl.DataFrame
            This is the polars dataframe of the annotations.
        """
        annotation_types = [AnnotationType.Box2d, AnnotationType.Mask]
        os.makedirs(dataset, exist_ok=True)

        dataset_id = self.val_session.dataset_id
        annotation_id = self.val_session.annotation_set_id

        # Download Images
        with tqdm.tqdm(
            total=0,
            desc=f"Downloading Images from Dataset ID: ds-{dataset_id.value:x}"
        ) as bar:
            def progress(current, total):
                if total != bar.total:
                    bar.reset(total)
                bar.update(current - bar.n)
                self.client.update_stage(
                    self.val_session.task.id,
                    stage="fetch_img",
                    status="Running",
                    message="Downloading Images",
                    percentage=int(100 * current / total)
                )

            self.client.download_dataset(
                dataset_id=dataset_id,
                groups=[self.val_group],
                types=[FileType.Image],
                output=os.path.join(dataset, "images"),
                progress=progress,
            )

        total_images = len(glob.glob(os.path.join(dataset, "images", "*"),
                                     recursive=True))
        logger(f"Downloaded a total of {total_images} images.", code="INFO")

       # Download Annotations
        with tqdm.tqdm(
            total=0,
            desc=f"Downloading Annotations from Annotation ID: as-{annotation_id.value:x}"
        ) as bar:
            def progress(current, total):
                if total != bar.total:
                    bar.reset(total)
                bar.update(current - bar.n)
                self.client.update_stage(
                    self.val_session.task.id,
                    stage="fetch_as",
                    status="Running",
                    message="Downloading Annotations",
                    percentage=int(100 * current / total)
                )

            dataframe = self.client.annotations_dataframe(
                annotation_set_id=annotation_id,
                groups=[self.val_group],
                annotation_types=annotation_types,
                progress=progress
            )
            dataframe.write_ipc(os.path.join(dataset, "dataset.arrow"))

        logger(f"Downloaded a total of {dataframe.shape[0]} annotations.",
               code="INFO")

        return dataframe

    def cache(self, dataset: str, cache: str = "cache/val.db"):
        """
        Cache the dataset provided into an LMDB file.

        Parameters
        ----------
        dataset: str
            The path to the dataset directory.
        cache: str
            The path to the cache file to save the cache.
        """
        group_name = os.path.basename(cache)
        logger(f"Caching dataset to {group_name}", code="INFO")

        os.makedirs(os.path.dirname(cache), exist_ok=True)

        self.edgefirst_dataset = EdgeFirstDatabase(
            source=dataset,
            parameters=self.parameters,
        )
        ds_iterator = tqdm.tqdm(self.edgefirst_dataset)

        # Remove existing cache file.
        if os.path.exists(cache):
            os.remove(cache)

        dbenv = lmdb.open(
            cache,
            map_size=1024 ** 4,
            max_dbs=10,
            subdir=False,
            lock=False
        )

        names_db = dbenv.open_db(b'names')
        camera_db = dbenv.open_db(b'camera')
        labels_db = dbenv.open_db(b'labels')

        boxes_db = None
        if self.parameters.common.with_boxes:
            boxes_db = dbenv.open_db(b'box2d')

        masks_db = None
        if self.parameters.common.with_masks:
            masks_db = dbenv.open_db(b'masks')

        with dbenv.begin(write=True) as txn:
            txn.put(
                b'labels',
                json.dumps(self.parameters.labels).encode(),
                db=labels_db
            )

        for i, instance in enumerate(ds_iterator):
            with dbenv.begin(write=True) as txn:
                boxes = None
                masks = None

                if self.parameters.common.with_boxes and self.parameters.common.with_masks:
                    name, image_data, boxes, (masks, masks_shape) = instance
                elif self.parameters.common.with_boxes:
                    name, image_data, boxes = instance
                elif self.parameters.common.with_masks:
                    name, image_data, (masks, masks_shape) = instance

                image, shapes, ratio, image_shape = image_data

                if boxes is not None:
                    txn.put(name.encode(), boxes.tobytes(), db=boxes_db)

                if masks is not None:
                    masks = masks.astype(np.uint8).tobytes()
                    txn.put(name.encode(), masks, db=masks_db)

                txn.put(name.encode(), None, db=names_db)

                if image is not None:
                    txn.put(name.encode(), image.tobytes(), db=camera_db)

                if shapes is not None:
                    txn.put(f'{name}/shapes'.encode(),
                            json.dumps(shapes).encode(),
                            db=camera_db)

                if ratio is not None:
                    txn.put(f'{name}/ratio'.encode(),
                            np.array([ratio], dtype=np.float32).tobytes(),
                            db=camera_db)

                # These are the original image dimensions.
                if image_shape is not None:
                    txn.put(f'{name}/shape'.encode(),
                            np.array(image_shape, dtype=np.int32).tobytes(),
                            db=camera_db)

                # These are the shape of the mask.
                if masks_shape is not None:
                    txn.put(f'{name}/mask_shape'.encode(),
                            np.array(masks_shape, dtype=np.int32).tobytes(),
                            db=masks_db)

            self.client.update_stage(
                self.val_session.task.id,
                stage="cache",
                status="Running",
                message=f"Caching: {group_name}",
                percentage=int(100 * i / len(ds_iterator))
            )

        # Close the database.
        dbenv.close()

        self.client.update_stage(
            self.val_session.task.id,
            stage="cache",
            status="Running",
            message=f"Caching: {group_name}",
            percentage=100
        )
