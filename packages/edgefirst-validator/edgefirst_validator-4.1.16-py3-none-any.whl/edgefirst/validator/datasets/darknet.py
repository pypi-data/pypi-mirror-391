"""
Implementations for reading DarkNet datasets.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, List, Tuple, Union
from time import monotonic_ns as clock_now

from edgefirst.validator.datasets import Dataset
from edgefirst.validator.datasets import (RadarDetectionInstance,
                                          SegmentationInstance,
                                          Detection3DInstance,
                                          DetectionInstance,
                                          MultitaskInstance,
                                          PoseInstance)
from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.datasets.utils.fetch import (get_image_files,
                                                      get_numpy_files,
                                                      classify_dataset,
                                                      get_annotation_files,
                                                      validate_dataset_source)
from edgefirst.validator.datasets.utils.readers import (read_image,
                                                        read_npy_file,
                                                        read_detection_text_file,
                                                        read_segmentation_text_file,
                                                        read_pose_json_file,
                                                        read_3d_detection_json_file,
                                                        read_segmentation_json_file)
from edgefirst.validator.datasets.utils.transformations import create_mask_image

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters
    from edgefirst.validator.datasets import Instance


class DarkNetDataset(Dataset):
    """
    Reads Darknet format datasets.
    Dataset format should be the same as coco128 at
    `https://www.kaggle.com/datasets/ultralytics/coco128`.
    Optionally, the images and text annotations can be in the same directory.

    Parameters
    ----------
    source: str
        The path to the source dataset.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.
    info_dataset: dict
        Contains information such as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "validation":
                    {
                        "images: 'path to the images',
                        "annotations": 'path to the annotations'
                    }
                }

        *Note: the classes are optional and the path to the images
        and annotations can be the same.*

    Raises
    ------
    ValueError
        Raised if the provided path to the images or
        annotations is not a string.
    EmptyDatasetException
        Raised if the provided path to the images or
        text files does not contain any image files or
        text files respectively.
    """

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters,
        info_dataset: dict = None,
    ):
        super(DarkNetDataset, self).__init__(
            source=source,
            parameters=parameters
        )

        if info_dataset is None:
            info_dataset = classify_dataset(source)

        try:
            images_path = info_dataset.get(
                "dataset").get('validation').get('images')
            annotations_path = info_dataset.get(
                "dataset").get('validation').get('annotations')
        except AttributeError:
            images_path = info_dataset.get('validation').get('images')
            annotations_path = info_dataset.get(
                'validation').get('annotations')

        self.image_source = validate_dataset_source(images_path)
        self.annotation_source = validate_dataset_source(annotations_path)

        labels = info_dataset.get('classes', None)
        if labels is not None:
            self.parameters.labels = [str(label) for label in labels]

        self.images = get_image_files(self.image_source)
        self.annotations = get_annotation_files(self.annotation_source)
        self.numpy_files = get_numpy_files(
            self.annotation_source, check_empty=False)

        # This is used to map the image name to the annotation file.
        self.annotation_extension = os.path.splitext(self.annotations[0])[1]

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.

        Returns
        -------
        int
            The number of samples in the dataset.
        """
        return len(self.images)

    def build_dataset(self) -> List[tuple]:
        """
        Builds the instances to allow iteration in the dataset.

        Returns
        -------
        List[tuple]
            One instance contains the
            (path to the image, path to the annotation).
        """
        missing_annotations = 0
        instances = list()
        for image_path in self.images:
            if len(self.numpy_files) > 0:
                radar_path = os.path.join(
                    os.path.dirname(image_path),
                    os.path.splitext(os.path.basename(image_path))[0] +
                    ".cube.npy")
                annotation_path = os.path.join(
                    os.path.dirname(image_path),
                    os.path.splitext(os.path.basename(image_path))[0] +
                    self.annotation_extension)
            else:
                radar_path = None
                annotation_path = os.path.join(
                    self.annotation_source,
                    os.path.splitext(os.path.basename(image_path))[0] +
                    self.annotation_extension)

            if os.path.exists(annotation_path):
                instances.append((image_path, annotation_path, radar_path))
            else:
                instances.append((image_path, None, None))
                if self.parameters.show_missing_annotations:
                    logger(
                        "Could not find the annotation " +
                        "for this image: {}. ".format(
                            os.path.basename(image_path)) +
                        "Looking for {}".format(
                            os.path.splitext(
                                os.path.basename(image_path))[0] +
                            self.annotation_extension),
                        code="WARNING")
                missing_annotations += 1

        if not self.parameters.show_missing_annotations and missing_annotations > 0:
            logger(
                "There were {} images without annotations. ".format(
                    missing_annotations) + "To see the names of the images, " +
                "enable --show_missing_annotations in the command line.",
                code="WARNING")
        return instances

    def read_sample(self, sample: Tuple[str, str, str]) -> Instance:
        """
        Reads one sample from the dataset.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        Instance
            The ground truth instance objects contains the annotations
            representing the ground truth of the image.
        """

        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            return self.build_multitask_instance(sample)
        elif self.parameters.common.with_boxes:
            return self.build_detection_instance(sample)
        elif self.parameters.common.with_masks:
            return self.build_segmentation_instance(sample)
        else:
            raise ValueError(
                "Either 'with_boxes' or 'with_masks' needs to be set to True.")

    def build_detection_instance(
        self,
        sample: Tuple[str, str, str]
    ) -> Union[DetectionInstance, RadarDetectionInstance]:
        """
        Builds a 2D detection instance container.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        Instance
            The ground truth instance objects contains the 2D bounding boxes
            and the labels representing the ground truth of the image.
        """
        image_path, annotation_path, radar_path = sample

        start = clock_now()
        image = read_image(image_path)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = image.shape

        if len(self.numpy_files) > 0:
            instance = RadarDetectionInstance(image_path)
            instance.cube = read_npy_file(annotation_path=radar_path)
        else:
            instance = DetectionInstance(image_path)

        instance.height = height
        instance.width = width
        instance.image = image

        annotations = read_detection_text_file(
            annotation_path=annotation_path,
            label_offset=self.parameters.label_offset,
            shape=(height, width),
            normalizer=self.normalizer,
            transformer=self.transformer
        )
        instance.boxes = annotations.get("boxes", [])
        instance.labels = annotations.get("labels", [])
        return instance

    def build_3d_detection_instance(
            self, sample: Tuple[str, str, str]) -> Detection3DInstance:
        """
        Builds a 3D detection instance container.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        Detection3DInstance
            The ground truth instance objects contains the 3D bounding boxes
            and the labels representing the ground truth of the image.
        """
        image_path, annotation_path, _ = sample

        start = clock_now()
        image = read_image(image_path)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = image.shape

        instance = Detection3DInstance(image_path)
        instance.height = height
        instance.width = width
        instance.image = image

        annotations = read_3d_detection_json_file(
            annotation_path=annotation_path,
            label_offset=self.parameters.label_offset
        )
        instance.boxes = annotations.get("boxes", [])
        instance.centers = annotations.get("centers", [])
        instance.sizes = annotations.get("sizes", [])
        instance.box_angles = annotations.get("angles", [])
        instance.calibration = annotations.get("view", [])
        instance.labels = annotations.get("labels", [])
        return instance

    def build_segmentation_instance(
            self, sample: Tuple[str, str, str]) -> SegmentationInstance:
        """
        Builds a segmentation instance container.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        SegmentationInstance
            The ground truth instance objects contains the polygon, mask,
            and the labels representing the ground truth of the image.
        """
        image_path, annotation_path, _ = sample

        start = clock_now()
        image = read_image(image_path)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = image.shape

        instance = SegmentationInstance(image_path)
        instance.height = height
        instance.width = width
        instance.image = image

        annotations = read_segmentation_json_file(
            annotation_path=annotation_path,
            shape=(height, width),
            label_offset=self.parameters.label_offset,
            denormalizer=self.denormalizer
        )
        instance.polygons = annotations.get("segments")
        labels = annotations.get("labels")
        instance.mask = create_mask_image(polygons=instance.polygons,
                                          labels=labels,
                                          shape=(height, width))
        return instance

    def build_pose_instance(
            self, sample: Tuple[str, str, str]) -> PoseInstance:
        """
        Builds a pose instance container.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        PoseInstance
            The ground truth instance objects contains the pose angles
            and the labels representing the ground truth of the image.
        """
        image_path, annotation_path, _ = sample

        start = clock_now()
        image = read_image(image_path)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = image.shape

        instance = PoseInstance(image_path)
        instance.height = height
        instance.width = width
        instance.image = image

        annotations = read_pose_json_file(
            annotation_path=annotation_path,
            label_offset=self.parameters.label_offset,
            shape=(height, width),
            normalizer=self.normalizer,
            transformer=self.transformer
        )
        instance.boxes = annotations.get("boxes")
        instance.pose_angles = annotations.get("angles")
        instance.labels = annotations.get("labels")
        return instance

    def build_multitask_instance(
            self, sample: Tuple[str, str, str]) -> MultitaskInstance:
        """
        Builds a multitask instance container.

        Parameters
        ----------
        sample: Tuple[str, str, str]
            This contains the (image path, annotation path, radar_path).

        Returns
        -------
        MultitaskInstance
            The ground truth instance objects contains the bounding boxes
            and the segmentation mask representing the ground truth of
            the image
        """

        image_path, annotation_path, _ = sample

        start = clock_now()
        image = read_image(image_path)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        height, width, _ = image.shape

        instance = MultitaskInstance(image_path)

        instance.height = height
        instance.width = width
        instance.image = image

        annotations = read_segmentation_text_file(
            annotation_path=annotation_path,
            label_offset=self.parameters.label_offset,
            shape=(height, width),
            normalizer=self.normalizer,
            transformer=self.transformer
        )
        instance.boxes = annotations.get("boxes")
        instance.labels = annotations.get("labels")
        instance.polygons = annotations.get("segments")

        # Segment to mask creation is done inside the evaluator.
        # Offset because the detection labels start at 0.
        # instance.mask = create_mask_image(polygons=instance.polygons,
        #                                   labels=instance.labels+1,
        #                                   shape=(height, width))
        return instance
