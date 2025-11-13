"""
Implementations for reading TFRecord datasets.
"""

from __future__ import annotations

import os
import glob
from typing import TYPE_CHECKING
from time import monotonic_ns as clock_now

import numpy as np

from edgefirst.validator.datasets.utils.fetch import (classify_dataset,
                                                      validate_dataset_source)
from edgefirst.validator.datasets import Dataset
from edgefirst.validator.datasets import DetectionInstance

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters


class TFRecordDataset(Dataset):
    """
    Reads TFRecord Datasets.

    Parameters
    ----------
    source: str
        The path to the source dataset.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.
    info_dataset: dict
        Formatted as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "validation": {
                        "path": path to the *.tfrecord files.
                    }
                }

    Raises
    ------
    ImportError
        Raised if TensorFlow library is not installed.
    FileNotFoundError
        Raised if the provided path to the tfrecord files
        does not contain any tfrecord files.
    """

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters,
        info_dataset: dict = None,
    ):
        super(TFRecordDataset, self).__init__(
            source=source,
            parameters=parameters
        )

        if info_dataset is None:
            info_dataset = classify_dataset(source)

        self.source = validate_dataset_source(
            info_dataset.get('validation').get('path'))

        labels = info_dataset.get('classes', None)
        if labels is not None:
            self.labels = [str(label) for label in labels]

        self.tfrecords = glob.glob(os.path.join(self.source, '*.tfrecord'))
        if len(self.tfrecords) == 0:
            raise FileNotFoundError(
                f"There are no TFRecord files in {self.source}")

    def py_read_data(self, example):
        """
        Parses a serialized TFRecord example into image and annotation data.

        Parameters
        ----------
        example : tf.Tensor
            Serialized TFRecord example.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray, int, int, tf.Tensor]
            np.ndarray
                Decoded image array.
            np.ndarray
                Normalized and transformed bounding boxes (N, 4).
            np.ndarray
                Object class labels.
            int
                Image height.
            int
                Image width.
            tf.Tensor or None
                Optional image name field.

        Raises
        ------
        ImportError
            Raised if TensorFlow is not installed.
        """
        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf  # type: ignore
        except ImportError:
            raise ImportError("TensorFlow library is needed to " +
                              "read tfrecord datasets.")
        feature_description = {
            "image": tf.io.FixedLenFeature([], tf.string),
            "image_name": tf.io.FixedLenFeature([], tf.string),
            "width": tf.io.FixedLenFeature([], tf.int64),
            "height": tf.io.FixedLenFeature([], tf.int64),
            "objects": tf.io.VarLenFeature(tf.int64),
            "bboxes": tf.io.VarLenFeature(tf.float32),
        }
        sample = tf.io.parse_single_example(
            example,
            feature_description)

        start = clock_now()
        img = tf.io.decode_jpeg(sample['image']).numpy()
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = img.shape

        labels = tf.sparse.to_dense(sample['objects']).numpy().astype(np.int32)
        boxes = np.array([], dtype=np.float32)

        if len(labels):
            boxes = tf.sparse.to_dense(
                sample['bboxes']).numpy().reshape(-1, 4).astype(np.float32)
            boxes = self.normalizer(
                boxes, (height, width)) if self.normalizer else boxes
            boxes = self.transformer(boxes) if self.transformer else boxes
            boxes[boxes < 0] = 0.0
        return img, boxes, labels, height, width, sample.get('image_name')

    def read_data(self, path):
        """
        Wraps `py_read_data` in a TensorFlow `tf.py_function`.

        Parameters
        ----------
        path : tf.Tensor
            Input TFRecord file path or serialized record.

        Returns
        -------
        tuple
            Tuple of image, boxes, labels, height, width, and image name.

        Raises
        ------
        ImportError
            Raised if TensorFlow is not installed.
        """
        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf  # type: ignore
        except ImportError:
            raise ImportError("TensorFlow library is needed to " +
                              "read tfrecord datasets.")
        return tf.py_function(
            self.py_read_data,
            [path],
            Tout=[tf.uint8, tf.float32, tf.int32,
                  tf.int32, tf.int32, tf.string])

    def build_dataset(self) -> list:
        """
        Builds a batched and prefetched TFRecord dataset pipeline.

        Returns
        -------
        list
            A list of parsed records from the TFRecord dataset.

        Raises
        ------
        ImportError
            Raised if TensorFlow is not installed.
        """
        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf  # type: ignore
        except ImportError:
            raise ImportError("TensorFlow library is needed to " +
                              "read tfrecord datasets.")
        iteration = tf.data.TFRecordDataset(
            self.tfrecords,
            num_parallel_reads=tf.data.AUTOTUNE
        ).map(
            self.read_data,
            num_parallel_calls=tf.data.AUTOTUNE
        ).batch(
            batch_size=1
        ).prefetch(tf.data.AUTOTUNE)

        records = [record for record in iteration]
        return records

    def read_sample(self, this_instance) -> DetectionInstance:
        """
        Converts one TFRecord batch into a `DetectionInstance`.

        Parameters
        ----------
        this_instance : tuple
            A single parsed TFRecord batch.

        Returns
        -------
        DetectionInstance
            Instance containing image, boxes, labels, height, and width.

        Raises
        ------
        NotImplementedError
            Raised if `with_boxes` is not enabled in parameters.
        """
        img, boxes, labels, height, width, file_path = this_instance

        if self.parameters.common.with_boxes:
            instance = DetectionInstance(file_path.numpy()[0].decode())
            labels = labels.numpy()[0] + self.parameters.label_offset
            instance.height = height.numpy()[0]
            instance.width = width.numpy()[0],
            instance.image = img.numpy()[0]
            instance.boxes = boxes.numpy()[0]
            instance.labels = labels
            return instance
        else:
            raise NotImplementedError(
                "Only 'with_boxes' is currently supported for TFRecord datasets.")
