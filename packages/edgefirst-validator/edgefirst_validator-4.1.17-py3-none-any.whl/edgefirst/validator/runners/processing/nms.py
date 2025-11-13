from typing import Tuple, List, Union

import numpy as np

from edgefirst.validator.datasets.utils.transformations import yolo2xyxy
from edgefirst.validator.metrics.utils.math import batch_iou


def nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    max_detections: int = 300,
    eps: float = 1e-7
) -> list:
    """
    Single class NMS implemented in NumPy.
    Method taken from:: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/utils/demo_utils.py#L57
    Original source from:: https://github.com/amusi/Non-Maximum-Suppression/blob/master/nms.py

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS with shape (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    max_detections: int
        Specify the maximum number of detections to return after NMS.
    eps: float
        Scalar to avoid division by zeros.

    Returns
    -------
    list
        This contains the indices of the boxes to keep.
    """
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        ovr = inter / np.maximum((areas[i] + areas[order[1:]] - inter), eps)

        inds = np.nonzero(ovr <= iou_thr)[0]
        order = order[inds + 1]

    keep = np.array(keep)
    if keep.shape[0] > max_detections:  # limit detections
        keep = keep[:max_detections]  # This limits detections.
    return keep


def torch_nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    max_detections: int = 300
):
    """
    Return output from single class torchvision NMS.
    https://docs.pytorch.org/vision/0.9/ops.html#torchvision.ops.nms

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS with shape (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    max_detections: int
        Specify the maximum number of detections to return after NMS.

    Returns
    -------
    torch.Tensor
        This contains the indices of the boxes to keep.
    """
    try:
        import torch  # type: ignore
        import torchvision  # type: ignore
    except ImportError:
        raise ImportError(
            "Torch and Torchvision is needed to use `torch_nms`.")

    i = torchvision.ops.nms(torch.tensor(
        boxes), torch.tensor(scores), iou_thr)

    if i.shape[0] > max_detections:  # limit detections
        i = i[:max_detections]  # This limits detections.
    return i


def tensorflow_nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int
):
    """
    Return output from single class TensorFlow NMS.
    https://www.tensorflow.org/api_docs/python/tf/image/non_max_suppression

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS with shape (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS with shape (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        The confidence score threshold for the NMS.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.

    Returns
    -------
    Tensor
        This contains the indices of the boxes to keep.
    """
    try:
        import tensorflow as tf  # type: ignore
    except ImportError:
        raise ImportError("TensorFlow is needed to use `tensorflow_nms`.")

    # Sort boxes by score
    boxes = tf.reshape(boxes, [-1, 4])
    N = boxes.shape[0]
    scores = tf.reshape(scores, [N, -1])
    scores = tf.reduce_max(scores, axis=1)

    return tf.image.non_max_suppression(
        boxes=boxes,
        scores=scores,
        max_output_size=max_detections,
        iou_threshold=iou_thr,
        score_threshold=score_thr
    )


def tensorflow_combined_nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    clip_boxes: bool = False,
    class_agnostic: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return output from multiclass TensorFlow NMS.
    https://www.tensorflow.org/api_docs/python/tf/image/combined_non_max_suppression
    Optional is to run class-agnostic NMS.

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS with shape (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        The confidence score threshold for the NMS.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    clip_boxes: bool
        If set to True, boxes will be clipped between 0 and 1. If False,
        the coordinates are kept as it is.
    class_agnostic: bool
        Run class-agnostic NMS. Default includes class.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            This contains only the valid bounding boxes.
        np.ndarray
            This contains only the valid classes.
        np.ndarray
            This contains only the valid scores.
    """

    try:
        import tensorflow as tf  # type: ignore
    except ImportError:
        raise ImportError("TensorFlow is needed to use `tensorflow_nms`.")

    if class_agnostic:
        # Sort boxes by score
        boxes = tf.reshape(boxes, [-1, 4])
        N = boxes.shape[0]
        scores = tf.reshape(scores, [N, -1])
        nms_scores = tf.reduce_max(scores, axis=1)
        classes = tf.argmax(scores, axis=1)

        keep = tf.image.non_max_suppression(
            boxes=boxes,
            scores=nms_scores,
            max_output_size=max_detections,
            iou_threshold=iou_thr,
            score_threshold=score_thr
        )
        boxes = tf.gather(boxes, keep).numpy()
        scores = tf.gather(nms_scores, keep).numpy()
        classes = tf.gather(classes, keep).numpy().astype(np.int32)

        return boxes, classes, scores
    else:
        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
            tf.image.combined_non_max_suppression(
                boxes=boxes,
                scores=scores,
                max_output_size_per_class=max_detections,
                max_total_size=max_detections,
                iou_threshold=iou_thr,
                score_threshold=score_thr,
                clip_boxes=clip_boxes
            )
        valid_boxes = valid_boxes.numpy()[0]
        nmsed_boxes = nmsed_boxes.numpy()[0]
        nmsed_classes = nmsed_classes.numpy()[0]
        nmsed_scores = nmsed_scores.numpy()[0]

        boxes = nmsed_boxes[:valid_boxes]
        scores = nmsed_scores[:valid_boxes]
        classes = nmsed_classes[:valid_boxes].astype(np.int32)

        return boxes, classes, scores


def multiclass_nms_class_aware(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    nms_type: str = "numpy"
) -> np.ndarray:
    """
    This is the YOLOx Multiclass NMS implemented in NumPy. Class-aware version.

    Source:: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/utils/demo_utils.py#L96

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        This contains the score threshold input for the NMS.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.

    Returns
    -------
    np.ndarray
        Post-NMS detections (number of detections, 6) which contains
        (xyxy, score, class) a total of 6 columns.
    """
    final_dets = []
    num_classes = scores.shape[1]
    for cls_ind in range(num_classes):
        cls_scores = scores[:, cls_ind]
        valid_score_mask = cls_scores > score_thr
        if valid_score_mask.sum() == 0:
            continue
        else:
            valid_scores = cls_scores[valid_score_mask]
            valid_boxes = boxes[valid_score_mask]

            if nms_type == "numpy":
                keep = nms(
                    boxes=valid_boxes,
                    scores=valid_scores,
                    iou_thr=iou_thr,
                    max_detections=max_detections
                )
            elif nms_type == "tensorflow":
                keep = tensorflow_nms(
                    boxes=valid_boxes,
                    scores=valid_scores,
                    iou_thr=iou_thr,
                    score_thr=score_thr,
                    max_detections=max_detections
                )
            elif nms_type == "torch":
                keep = torch_nms(
                    boxes=valid_boxes,
                    scores=valid_scores,
                    iou_thr=iou_thr,
                    max_detections=max_detections
                )
            else:
                raise TypeError(
                    "Unrecognized NMS type '{}' provided.".format(nms_type))

            if len(keep) > 0:
                cls_inds = np.ones((len(keep), 1)) * cls_ind
                dets = np.concatenate(
                    [valid_boxes[keep], valid_scores[keep, None], cls_inds], 1
                )
                final_dets.append(dets)
    if len(final_dets) == 0:
        return None
    return np.concatenate(final_dets, 0)


def multiclass_nms_class_agnostic(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    nms_type: str = "numpy"
) -> np.ndarray:
    """
    This is the YOLOx Multiclass NMS implemented in NumpPy. Class-agnostic version.

    Source:: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/utils/demo_utils.py#L120.

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        This contains the score threshold input for the NMS.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.

    Returns
    -------
    np.ndarray
        Post-NMS detections (number of detections, 6) which contains
        (xyxy, score, class) a total of 6 columns.
    """
    cls_inds = scores.argmax(1)
    cls_scores = scores[np.arange(len(cls_inds)), cls_inds]

    valid_score_mask = cls_scores > score_thr
    if valid_score_mask.sum() == 0:
        return None
    valid_scores = cls_scores[valid_score_mask]
    valid_boxes = boxes[valid_score_mask]
    valid_cls_inds = cls_inds[valid_score_mask]

    if nms_type == "numpy":
        keep = nms(
            boxes=valid_boxes,
            scores=valid_scores,
            iou_thr=iou_thr,
            max_detections=max_detections
        )
    elif nms_type == "tensorflow":
        keep = tensorflow_nms(
            boxes=valid_boxes,
            scores=valid_scores,
            iou_thr=iou_thr,
            score_thr=score_thr,
            max_detections=max_detections
        )
    elif nms_type == "torch":
        keep = torch_nms(
            boxes=valid_boxes,
            scores=valid_scores,
            iou_thr=iou_thr,
            max_detections=max_detections
        )
    else:
        raise TypeError(
            "Unrecognized NMS type '{}' provided.".format(nms_type))

    if len(keep) > 0:
        dets = np.concatenate(
            [valid_boxes[keep], valid_scores[keep, None],
                valid_cls_inds[keep, None]], 1
        )
    return dets


def multiclass_nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    class_agnostic: bool = True,
    nms_type: str = "numpy"
) -> np.ndarray:
    """
    This is the YOLOx Multiclass NMS implemented in NumPy.

    Source:: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/utils/demo_utils.py#L87

    Parameters
    ----------
    boxes: np.ndarray
        Input boxes to the NMS (n, 4) in xyxy non-normalized format.
    scores: np.ndarray
        Input scores to the NMS (n,).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        This contains the score threshold input for the NMS.
    class_agnostic: bool
        This is to determine which type of NMS to perform.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.

    Returns
    -------
    np.ndarray
        Post-NMS detections (number of detections, 6) which contains
        (xyxy, score, class) a total of 6 columns.
    """
    if class_agnostic:
        nms_method = multiclass_nms_class_agnostic
    else:
        nms_method = multiclass_nms_class_aware
    return nms_method(
        boxes=boxes,
        scores=scores,
        iou_thr=iou_thr,
        score_thr=score_thr,
        max_detections=max_detections,
        nms_type=nms_type
    )


def v5_nms(
    prediction: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    nms_type: str = "numpy",
    agnostic: bool = False,
    multi_label: bool = True,
    max_wh: int = 7680,  # YOLOv5 defaults to 7680, 4096 in YOLOv7.
    max_nms: int = 30000,
    redundant: bool = True,
    merge: bool = False
):
    """
    This is the YOLOv5/YOLOv7 NMS implementation.
    Source:: https://github.com/ultralytics/yolov5/blob/master/utils/general.py#L1010

    Reproducing the same parameters as YoloV5 requires score_thr = 0.001,
    iou_thr = 0.60, max detections = 300

    Parameters
    ----------
    prediction: np.ndarray
        Raw predictions from the model (inference_out, loss_out).
        This has the shape (batch size, number of boxes, number of classes).
    iou_thr: float
        This is the IoU threshold for the NMS.
    score_thr: float
        The confidence score threshold for the NMS.
    max_detections: int
        The maximum number of boxes to be selected by NMS per class.
    nms_type: str
        Specify the type of NMS algorithm. By default, using a simple case
        using NumPy. Otherwise, other options include 'tensorflow' and 'torch'.
    agnostic: bool
        If True, the model is agnostic to the number of classes, and all
        classes will be considered as one.
    multi_label: bool
        If True, each box may have multiple labels.
    max_wh: int
        The maximum box width and height (pixels).
    max_nms: int
        The maximum number of boxes into nms.
    redundant: bool
        Require redundant detections.
    merge: bool
        Use merge NMS.

    Returns
    -------
    list
        A list of length one which has a shape of shape of
        (1, number of boxes, 6) and formatted as
        [[[xmin, ymin, xmax, ymax, confidence, label], [...], ...]].
    """
    # Offset of -5 is described in
    # https://medium.com/@KrashKart/i-wish-i-knew-this-about-yolov5-2fbab3584906
    nc = prediction.shape[2] - 5  # The number of classes.
    xc = prediction[..., 4] > score_thr  # Candidates.
    multi_label &= nc > 1  # Multiple labels per box (adds 0.5ms/img).

    output = [np.zeros((0, 6))] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # Image index, image inference.
        x = x[xc[xi]]  # Confidence.
        if not x.shape[0]:
            continue

        # Compute conf
        if nc == 1:
            # for models with one class, cls_loss is 0 and cls_conf is always
            # 0.5,
            x[:, 5:] = x[:, 4:5]
            # so there is no need to multiplicate.
        else:
            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf # NOSONAR

        # (center_x, center_y, width, height) to (x1, y1, x2, y2).
        box = yolo2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls).
        if multi_label:
            i, j = (x[:, 5:] > score_thr).nonzero()
            x = np.concatenate(
                (box[i], x[i, j + 5, None], j[:, None].astype(np.float32)), 1)
        else:  # Best class only.
            conf = x[:, 5:].max(1, keepdims=True)
            j = x[:, 5:].argmax(1, keepdims=True)

            x = np.concatenate(
                (box, conf, j.astype(np.float32)), 1)[
                    conf.flatten() > score_thr]

        # Check shape.
        n = x.shape[0]  # Number of boxes.
        if not n:  # No boxes.
            continue
        # Sort by confidence and remove excess boxes.
        # elif n > max_nms:  # excess boxes
        #     x = x[x[:, 4].argsort(descending=True)[:max_nms]]
        x = x[np.argsort(x[:, 4])[::-1][:max_nms]]

        # Batched NMS.
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # The classes.
        # boxes (offset by class), scores.
        boxes, scores = x[:, :4] + c, x[:, 4]

        if nms_type == "numpy":
            i = nms(
                boxes=boxes,
                scores=scores,
                iou_thr=iou_thr,
                max_detections=max_detections
            )
        elif nms_type == "tensorflow":
            i = tensorflow_nms(
                boxes=boxes,
                scores=scores,
                iou_thr=iou_thr,
                score_thr=score_thr,
                max_detections=max_detections
            )
        elif nms_type == "torch":
            i = torch_nms(
                boxes=boxes,
                scores=scores,
                iou_thr=iou_thr,
                max_detections=max_detections
            )
        else:
            raise TypeError(
                "Unrecognized NMS type '{}' provided.".format(nms_type))

        # Merge NMS (boxes merged using weighted mean).
        if merge and (1 < n < 3e3):
            # Update boxes as boxes(i,4) = weights(i,n) * boxes(n,4).
            iou = batch_iou(boxes[i], boxes) > iou_thr  # IoU matrix.
            weights = iou * scores[None]  # Box weights.
            # Merged boxes.
            x[i, :4] = np.matmul(
                weights, x[:, :4]).astype(np.float32) / weights.sum(1, keepdims=True)

            if redundant:
                i = i[iou.sum(1) > 1]  # Require redundancy.
        output[xi] = x[i]
    return output


def v8_nms(
    prediction: np.ndarray,
    iou_thr: float,
    score_thr: float,
    max_detections: int,
    nms_type: str = "numpy",
    classes: List[int] = None,
    agnostic: bool = False,
    multi_label: bool = False,
    labels: List[List[Union[int, float, np.ndarray]]] = [],
    nc: int = 0,  # number of classes (optional)
    max_nms: int = 30000,
    max_wh: int = 7680,
    in_place: bool = True,
    rotated: bool = False,
    end2end: bool = False,
    return_idxs: bool = False,
) -> List[np.ndarray]:
    """
    This is the YOLOv8-v11 NMS implementation. Perform non-maximum suppression (NMS)
    on a set of boxes, with support for masks and multiple labels per box.

    Source:: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L192

    Parameters
    ----------
    prediction: np.ndarray
        A tensor of shape (batch_size, num_classes + 4 + num_masks, num_boxes)
        containing the predicted boxes, classes, and masks.
        The tensor should be in the format output by a model, such as YOLO.
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
    classes: List[int]
        A list of class indices to consider. If None, all classes
        will be considered.
    agnostic: bool
        If True, the model is agnostic to the number of classes, and all
        classes will be considered as one.
    multi_label: bool
        If True, each box may have multiple labels.
    labels: List[List[Union[int, float, np.ndarray]]]
        A list of lists, where each inner list contains the apriori labels
        for a given image. The list should be in the format output by a
        dataloader, with each label being a tuple of
        (class_index, x1, y1, x2, y2).
    max_det: int
        The maximum number of boxes to keep after NMS.
    nc: int
        The number of classes output by the model.
        Any indices after this will be considered masks.
    max_nms: int
        The maximum number of boxes into nms().
    max_wh: int
        The maximum box width and height in pixels.
    in_place: bool
        If True, the input prediction tensor will be modified in place.
    rotated: bool
        If Oriented Bounding Boxes (OBB) are being passed for NMS.
    end2end: bool
        If the model doesn't require NMS.
    return_idxs: bool
        Whether to return the indices of kept detections.

    Returns
    -------
    List[np.ndarray]
        A list of length batch_size, where each element is a tensor of
        shape (num_boxes, 6 + num_masks) containing the kept boxes,
        with columns (x1, y1, x2, y2, confidence, class, mask1, mask2, ...).
    """
    # YOLOv8 model in validation model, output = (inference_out, loss_out)
    if isinstance(prediction, (list, tuple)):
        prediction = prediction[0]  # select only inference output
    if classes is not None:
        classes = np.array(classes)

    # end-to-end model (BNC, i.e. 1,300,6)
    if prediction.shape[-1] == 6 or end2end:
        output = [pred[pred[:, 4] > score_thr][:max_detections]
                  for pred in prediction]
        if classes is not None:
            output = [pred[(pred[:, 5:6] == classes).any(1)]
                      for pred in output]
        return output

    bs = prediction.shape[0]  # batch size (BCN, i.e. 1,84,6300)
    nc = nc or (prediction.shape[1] - 4)  # number of classes
    nm = prediction.shape[1] - nc - 4  # number of masks
    mi = 4 + nc  # mask start index
    xc = np.amax(prediction[:, 4:mi], axis=1) > score_thr  # candidates
    # to track idxs.
    xinds = np.stack([np.arange(len(i)) for i in xc])[..., None]

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)

    # shape(1,classes,boxes) to shape(1,boxes,classes)
    prediction = prediction.transpose(0, -1, -2)

    if not rotated:
        if in_place:
            prediction[..., :4] = yolo2xyxy(
                prediction[..., :4])  # xywh to xyxy
        else:
            prediction = np.concatenate(
                (yolo2xyxy(prediction[..., :4]), prediction[..., 4:]), -1)  # xywh to xyxy

    output = [np.zeros((0, 6 + nm))] * bs
    keepi = [np.zeros((0, 1))] * bs
    for xi, (x, xk) in enumerate(
            zip(prediction, xinds)):  # image index, image inference
        # Apply constraints
        # x[((x[:, 2:4] < min_wh) | (x[:, 2:4] > max_wh)).any(1), 4] = 0  #
        # width-height
        filt = xc[xi]  # confidenc
        x, xk = x[filt], xk[filt]

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]) and not rotated:
            lb = labels[xi]
            v = np.zeros((len(lb), nc + nm + 4))
            v[:, :4] = yolo2xyxy(lb[:, 1:5])  # box
            v[range(len(lb)), lb[:, 0].astype(np.int64) + 4] = 1.0  # cls
            x = np.concatenate((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        box = x[:, :4]
        cls = x[:, 4:4 + nc]
        mask = x[:, 4 + nc:4 + nc + nm]

        if multi_label:
            i, j = np.where(cls > score_thr)
            x = np.concatenate(
                (box[i], x[i, 4 + j, None], j[:, None].astype(np.float32), mask[i]), 1)
            xk = xk[i]
        else:  # best class only
            conf = cls.max(1, keepdims=True)
            j = cls.argmax(1, keepdims=True)
            filt = conf.flatten() > score_thr
            x = np.concatenate(
                (box, conf, j.astype(np.float32), mask), 1)[filt]
            xk = xk[filt]

        # Filter by class
        if classes is not None:
            filt = (x[:, 5:6] == classes).any(1)
            x, xk = x[filt], xk[filt]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        if n > max_nms:  # excess boxes
            # sort by confidence in descending order and remove excess boxes
            filt = np.argsort(x[:, 4])[::-1][:max_nms]
            x, xk = x[filt], xk[filt]

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        scores = x[:, 4]  # scores

        if rotated:
            raise NotImplementedError(
                "NMS with rotation is not yet implemented.")
        else:
            boxes = x[:, :4] + c  # boxes (offset by class)
            if nms_type == "numpy":
                i = nms(
                    boxes=boxes,
                    scores=scores,
                    iou_thr=iou_thr,
                    max_detections=max_detections
                )
            elif nms_type == "tensorflow":
                i = tensorflow_nms(
                    boxes=boxes,
                    scores=scores,
                    iou_thr=iou_thr,
                    score_thr=score_thr,
                    max_detections=max_detections
                )
            elif nms_type == "torch":
                i = torch_nms(
                    boxes=boxes,
                    scores=scores,
                    iou_thr=iou_thr,
                    max_detections=max_detections
                )
            else:
                raise TypeError(
                    "Unrecognized NMS type '{}' provided.".format(nms_type))

        x_i = x[i]
        if x_i.ndim == 1:
            x_i = x_i[None, :]  # reshape (6,) → (1, 6)
        output[xi] = x_i
        keepi[xi] = xk[i].reshape(-1)

    return (output, keepi) if return_idxs else output
