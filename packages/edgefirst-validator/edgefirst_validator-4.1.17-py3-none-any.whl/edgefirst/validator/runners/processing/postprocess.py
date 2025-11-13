from typing import Union, Tuple

import numpy as np

from edgefirst.validator.datasets.utils.transformations import (xyxy2yolo,
                                                                xyxy2xywh,
                                                                process_mask)
from edgefirst.validator.runners.processing.nms import (multiclass_nms,
                                                        v5_nms, v8_nms, nms,
                                                        tensorflow_combined_nms)


def process_yolox(
    output: np.ndarray,
    input_shape: tuple,
    ratio: float,
    image_shape: tuple,
    iou_thr: float = 0.45,
    score_thr: float = 0.1,
    max_detections: int = 300,
    nms_type: str = "numpy",
    p6: bool = False,
    box_format: str = "pascalvoc"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    This performs postprocessing of YOLOx detection models.
    Source:: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/utils/demo_utils.py#L139

    Parameters
    ----------
    output: np.ndarray
        This is the output of the model to postprocess into
        bounding boxes, classes, scores after NMS.
    input_shape: tuple
        Specifying the model input shape.
    ratio: float
        This is the ratio value from the letterbox or padding
        transformation to adjust the bounding boxes.
    image_shape: tuple
        This is the original shape of the image to normalize coordinates.
    iou_thr: float
        The IoU threshold below which boxes will be filtered out during NMS.
        Valid values are between 0.0 and 1.0.
    score_thr: float
        The confidence threshold below which boxes will be filtered out.
        Valid values are between 0.0 and 1.0.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.
    p6: bool
        If True, enables support for YOLOX-P6 with stride 64 detection head.
    box_format: str
        The bounding box format to output. By default "pascvalvoc" is used
        which is [xmin, ymin, xmax, ymax]. However, other options include
        "yolo" for [xc, yc, width, height], or "coco" for
        [xmin, ymin, width, height].

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            The prediction bounding boxes.. [[box1], [box2], ...].
        np.ndarray
            The prediction labels.. [cl1, cl2, ...].
        np.ndarray
            The prediction confidence scores.. [score, score, ...]
            normalized between 0 and 1.
    """
    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if input_shape[-1] in [2, 3, 4]:
        h, w = input_shape[1:3]
    else:
        h, w = input_shape[2:4]

    grids = []
    expanded_strides = []
    strides = [8, 16, 32] if not p6 else [8, 16, 32, 64]

    hsizes = [h // stride for stride in strides]
    wsizes = [w // stride for stride in strides]
    for hsize, wsize, stride in zip(hsizes, wsizes, strides):
        xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))
        grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        expanded_strides.append(np.full((*shape, 1), stride))

    grids = np.concatenate(grids, 1)
    expanded_strides = np.concatenate(expanded_strides, 1)
    output[..., :2] = (output[..., :2] + grids) * expanded_strides
    output[..., 2:4] = np.exp(output[..., 2:4]) * expanded_strides
    predictions = output[0]

    boxes = predictions[:, :4]
    scores = predictions[:, 4:5] * predictions[:, 5:]

    boxes_xyxy = np.ones_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
    boxes_xyxy /= ratio

    # Typical: nms_thr=0.45, score_thr=0.1
    dets = multiclass_nms(
        boxes=boxes_xyxy,
        scores=scores,
        iou_thr=iou_thr,
        score_thr=score_thr,
        max_detections=max_detections,
        nms_type=nms_type
    )
    if dets is None:
        return np.array([]), np.array([]), np.array([])

    nmsed_boxes = dets[:, :4]
    nmsed_scores = dets[:, 4]
    nmsed_classes = dets[:, 5]
    nmsed_boxes /= np.array([image_shape[1], image_shape[0],
                            image_shape[1], image_shape[0]])

    if box_format == "yolo":
        nmsed_boxes = xyxy2yolo(nmsed_boxes)
    elif box_format == "coco":
        nmsed_boxes = xyxy2xywh(nmsed_boxes)

    return nmsed_boxes, nmsed_classes, nmsed_scores


def process_yolov(
    output: np.ndarray,
    input_shape: tuple,
    nc: int = 80,
    iou_thr: float = 0.60,
    score_thr: float = 0.01,
    max_detections: int = 300,
    nms_type: str = "numpy",
    method: str = "ultralytics",
    box_format: str = "pascalvoc"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Process the outputs from YOLOv5/v8/v11 and YOLOv7
    exported detection models.

    Parameters
    ----------
    output: np.ndarray
        Models converted in YOLOv5 has the
        following shape (batch size, number of boxes, number of classes).

        Models converted in YOLOv7 will already have NMS embedded. The
        output will have the shape of (number of boxes, 7) and formatted as
        [[batch_id, xmin, ymin, xmax, ymax, cls, score], ...].
    input_shape: tuple
        Specifying the model input shape.
    nc: int
        The number of classes in the model.
    iou_thr: float
        The IoU threshold below which boxes will be filtered out during NMS.
        Valid values are between 0.0 and 1.0.
    score_thr: float
        The confidence threshold below which boxes will be filtered out.
        Valid values are between 0.0 and 1.0.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.
    method: str
        The type of validation method. By default "ultralytics" method
        is used. Otherwise, "yolov7" or "edgefirst" can be reproduced.
    box_format: str
        The bounding box format to output. By default "pascvalvoc" is used
        which is [xmin, ymin, xmax, ymax]. However, other options include
        "yolo" for [xc, yc, width, height], or "coco" for
        [xmin, ymin, width, height].

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            The prediction bounding boxes.. [[box1], [box2], ...].
        np.ndarray
            The prediction labels.. [cl1, cl2, ...].
        np.ndarray
            The prediction confidence scores.. [score, score, ...]
            normalized between 0 and 1.
    """
    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if input_shape[-1] in [2, 3, 4]:
        h, w = input_shape[1:3]
    else:
        h, w = input_shape[2:4]

    # YOLOv7 converted model.
    if output.shape[1] == 7:
        outputs = output
        # Quick check: percentage of values between 0 and 1 (inclusive or exclusive)
        # Determine if the boxes are normalized or not.
        normalized_conf = np.mean(
            (outputs[..., 1:5] >= 0) & (outputs[..., 1:5] <= 1))
        # Normalize the boxes if they are unnormalized.
        if normalized_conf < 0.95:
            outputs[..., 1:5] /= [w, h, w, h]

        nmsed_boxes = outputs[..., 1:5]
        # Single dimensional arrays gets converted to the element.
        # Specify the axis into 1 to prevent that.
        nmsed_scores = np.squeeze(outputs[..., 6:7], axis=1)
    # YOLOv8 and YOLOv11 model. shape: (1, 84, 8400).
    elif output.shape[2] > output.shape[1]:
        # Quick check: percentage of values between 0 and 1 (inclusive or exclusive)
        # Determine if the boxes are normalized or not.
        normalized_conf = np.mean((output[:, :4] >= 0) & (output[:, :4] <= 1))
        # Denormalize the boxes if they are unnormalized.
        if normalized_conf >= 0.95:
            output[:, [0, 2]] *= w
            output[:, [1, 3]] *= h

        outputs = v8_nms(
            prediction=output,
            iou_thr=iou_thr,
            score_thr=score_thr,
            max_detections=max_detections,
            nms_type=nms_type,
            nc=nc,
            max_wh=4096 if method == "yolov7" else 7680
        )
        outputs = outputs[0]
        # Normalize the boxes.
        outputs[:, [0, 2]] /= w
        outputs[:, [1, 3]] /= h

        nmsed_boxes = outputs[..., :4]
        nmsed_scores = np.squeeze(outputs[..., 4:5], axis=1)
    # YOLOv5 converted model. (1, 25200, 85)
    else:
        # Quick check: percentage of values between 0 and 1 (inclusive or exclusive)
        # Determine if the boxes are normalized or not.
        normalized_conf = np.mean(
            (output[..., :4] >= 0) & (output[..., :4] <= 1))
        # Denormalize the boxes if they are unnormalized.
        if normalized_conf >= 0.95:
            output[..., :4] *= [w, h, w, h]  # xywh normalized to pixels.

        outputs = v5_nms(
            prediction=output,
            iou_thr=iou_thr,
            score_thr=score_thr,
            max_detections=max_detections,
            nms_type=nms_type,
            max_wh=4096 if method == "yolov7" else 7680
        )
        outputs = outputs[0]
        # Normalize the boxes.
        outputs[..., :4] /= [w, h, w, h]

        nmsed_boxes = outputs[..., :4]
        # Single dimensional arrays gets converted to the element.
        # Specify the axis into 1 to prevent that.
        nmsed_scores = np.squeeze(outputs[..., 4:5], axis=1)

    nmsed_classes = np.squeeze(outputs[..., 5:6], axis=1)

    if box_format == "yolo":
        nmsed_boxes = xyxy2yolo(nmsed_boxes)
    elif box_format == "coco":
        nmsed_boxes = xyxy2xywh(nmsed_boxes)

    return nmsed_boxes, nmsed_classes, nmsed_scores


def process_yolov_segmentation(
    output: np.ndarray,
    outputs: list,
    input_shape: tuple,
    nc: int = 80,
    iou_thr: float = 0.60,
    score_thr: float = 0.01,
    max_detections: int = 300,
    nms_type: str = "numpy",
    method: str = "ultralytics",
    box_format: str = "pascalvoc"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Process the outputs from YOLOv5/v8/v11
    exported segmentation models.

    Parameters
    ----------
    output: np.ndarray
        Models converted in Ultralytics has the
        following shape (batch size, number of boxes, number of classes).
    outputs: list
        A list that contains the index that maps the boxes, scores,
        mask outputs from the model.
    input_shape: tuple
        Specifying the model input shape.
    nc: int
        The number of classes in the model.
    iou_thr: float
        The IoU threshold below which boxes will be filtered out during NMS.
        Valid values are between 0.0 and 1.0.
    score_thr: float
        The confidence threshold below which boxes will be filtered out.
        Valid values are between 0.0 and 1.0.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.
    method: str
        The type of validation method. By default "ultralytics" method
        is used. Otherwise, "yolov7" or "edgefirst" can be reproduced.
    box_format: str
        The bounding box format to output. By default "pascvalvoc" is used
        which is [xmin, ymin, xmax, ymax]. However, other options include
        "yolo" for [xc, yc, width, height], or "coco" for
        [xmin, ymin, width, height].

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            The prediction bounding boxes.. [[box1], [box2], ...].
        np.ndarray
            The prediction labels.. [cl1, cl2, ...].
        np.ndarray
            The prediction confidence scores.. [score, score, ...]
            normalized between 0 and 1.
        np.ndarray
            Model predicted mask.
    """
    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if input_shape[-1] in [2, 3, 4]:
        h, w = input_shape[1:3]
    else:
        h, w = input_shape[2:4]

    _, score_outputs, mask_outputs, decoded_mask_outputs = outputs
    masks, proto = None, None

    if decoded_mask_outputs is not None:
        masks = output[decoded_mask_outputs]
    elif mask_outputs is not None:
        proto = output[mask_outputs][-1] if len(output[mask_outputs]) == 3 \
            else output[mask_outputs]  # second output is len 3 if pt, but only 1 if exported

    output = output[score_outputs]
    # Quick check: percentage of values between 0 and 1 (inclusive or exclusive)
    # Determine if the boxes are normalized or not.
    normalized_conf = np.mean((output[:, :4] >= 0) & (output[:, :4] <= 1))
    # Denormalize the boxes if they are unnormalized.
    if normalized_conf >= 0.95:
        output[:, [0, 2]] *= w
        output[:, [1, 3]] *= h

    outputs = v8_nms(
        prediction=output,
        iou_thr=iou_thr,
        score_thr=score_thr,
        max_detections=max_detections,
        nms_type=nms_type,
        multi_label=True,
        nc=nc,
        max_wh=4096 if method == "yolov7" else 7680
    )
    pred = outputs[0]

    nmsed_boxes = pred[..., :4]
    nmsed_scores = np.squeeze(pred[..., 4:5], axis=1)
    nmsed_classes = np.squeeze(pred[..., 5:6], axis=1)

    # Support for Quantized TFLite which have output shape (1, 160, 160, 32).
    if proto.shape[-1] == 32:
        proto = np.transpose(proto, (0, 3, 1, 2))
    if proto is not None:
        # Squeezing the batch size => currently supports batch 1.
        proto = np.squeeze(proto, axis=0)

        # EdgeFirst validation method requires a 2D mask with all
        # the unique labels at each element.
        if method == "edgefirst":
            masks = process_mask(
                proto, pred[:, 6:], pred[:, :4], shape=input_shape, upsample=True)

            total_mask = np.zeros(masks.shape[1:], dtype=masks.dtype)
            for cls, mask in zip(nmsed_classes, masks):
                # Offset because detection labels start at 0.
                total_mask[mask == 1] = cls + 1
            masks = total_mask
        else:
            masks = process_mask(
                proto, pred[:, 6:], pred[:, :4], shape=input_shape)

    # Normalize the boxes.
    pred[:, [0, 2]] /= w
    pred[:, [1, 3]] /= h

    if box_format == "yolo":
        nmsed_boxes = xyxy2yolo(nmsed_boxes)
    elif box_format == "coco":
        nmsed_boxes = xyxy2xywh(nmsed_boxes)

    return nmsed_boxes, nmsed_classes, nmsed_scores, masks


def process_modelpack(
    output: Union[list, np.ndarray],
    outputs: list,
    iou_thr: float = 0.60,
    score_thr: float = 0.01,
    max_detections: int = 300,
    nms_type: str = "numpy",
    box_format: str = "pascalvoc"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Process ModelPack outputs.

    Parameters
    ----------
    output: Union[list, np.ndarray]
        Models converted internally will be a list with length of 2
        containing the bounding boxes as the first element and the scores
        for the second element which needs to be passed to NMS.
    outputs: list
        A list that contains the index that maps the boxes, scores,
        mask outputs from the model.
    iou_thr: float
        The IoU threshold below which boxes will be filtered out during NMS.
        Valid values are between 0.0 and 1.0.
    score_thr: float
        The confidence threshold below which boxes will be filtered out.
        Valid values are between 0.0 and 1.0.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow'.
    box_format: str
        The bounding box format to output. By default "pascvalvoc" is used
        which is [xmin, ymin, xmax, ymax]. However, other options include
        "yolo" for [xc, yc, width, height], or "coco" for
        [xmin, ymin, width, height].

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            The prediction bounding boxes.. [[box1], [box2], ...].
        np.ndarray
            The prediction labels.. [cl1, cl2, ...].
        np.ndarray
            The prediction confidence scores.. [score, score, ...]
            normalized between 0 and 1.
        np.ndarray
            Segmentation masks array from the model.
    """
    box_outputs, score_outputs, mask_outputs, decoded_mask_outputs = outputs
    nmsed_boxes, nmsed_classes, nmsed_scores, masks = None, None, None, None

    if box_outputs is not None and score_outputs is not None:
        boxes = output[box_outputs]
        scores = output[score_outputs]

        if nms_type == "tensorflow":
            nmsed_boxes, nmsed_classes, nmsed_scores = tensorflow_combined_nms(
                boxes=boxes,
                scores=scores,
                iou_thr=iou_thr,
                score_thr=score_thr,
                max_detections=max_detections,
                class_agnostic=True
            )
        else:
            # Reshape boxes and scores and compute classes.
            boxes = np.reshape(boxes, (-1, 4))
            scores = np.reshape(scores, (boxes.shape[0], -1))
            classes = np.argmax(scores, axis=1).astype(np.int32)

            # Prefilter boxes and scores by minimum score
            max_scores = np.max(scores, axis=1)
            mask = max_scores >= score_thr

            # Prefilter the boxes, scores and classes IDs.
            nmsed_scores = max_scores[mask]
            nmsed_boxes = boxes[mask]
            nmsed_classes = classes[mask]

            keep = nms(
                boxes=nmsed_boxes,
                scores=nmsed_scores,
                iou_thr=iou_thr,
                max_detections=max_detections
            )

            # Filter boxes, scores, and classes.
            if len(keep):
                nmsed_boxes = nmsed_boxes[keep]
                nmsed_scores = nmsed_scores[keep]
                nmsed_classes = nmsed_classes[keep]

        if box_format == "yolo":
            nmsed_boxes = xyxy2yolo(nmsed_boxes)
        elif box_format == "coco":
            nmsed_boxes = xyxy2xywh(nmsed_boxes)

    if decoded_mask_outputs is not None:
        masks = output[decoded_mask_outputs]
    elif mask_outputs is not None:
        masks = output[mask_outputs]
        # Decode the masks
        masks = np.argmax(masks, axis=-1)

    return nmsed_boxes, nmsed_classes, nmsed_scores, masks
