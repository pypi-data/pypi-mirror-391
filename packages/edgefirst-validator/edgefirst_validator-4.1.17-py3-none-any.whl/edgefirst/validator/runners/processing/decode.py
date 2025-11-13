import numpy as np

from edgefirst.validator.metrics.utils.math import sigmoid


def decode_modelpack_outputs(outputs: list, metadata: dict) -> dict:
    """
    Decodes raw model outputs into bounding boxes and class scores.

    Parameters
    ----------
    outputs: list
        List of output tensors from the model, one per output layer.
        The order of the outputs is in the same order as it appears in the
        model outputs.
    metadata: dict
        The model metadata stored inside the model.

    Returns
    -------
    dict
        A dictionary containing the index and the array of the decoded
        outputs from ModelPack.
    """
    decoded_outputs = {
        "boxes": None,
        "scores": None,
        "masks": None,
        "segmentation": None,
        "outputs": outputs
    }

    if "outputs" not in metadata.keys():
        return None

    bboxes, bscores = [], []

    for output_details in metadata["outputs"]:
        config_shape = output_details["shape"]
        for i, out in enumerate(outputs):
            shape = [o for o in out.shape]
            if config_shape == shape:
                output_details["output_index"] = i
                decoded_outputs[output_details["type"]] = i
                continue

    for output_details in metadata["outputs"]:
        if output_details["decode"] and output_details["type"] != "segmentation":
            p = sigmoid(outputs[output_details["output_index"]])

            anchors = np.asarray(
                output_details['anchors'], dtype=np.float32)
            na = anchors.shape[0]
            nc = p.shape[-1] // na - 5
            _, h, w, _ = p.shape
            _, h1, w1, _ = output_details["shape"]
            assert (
                h, w) == (
                h1, w1), "Expected output shape did not match."

            p = p.reshape((-1, h, w, na, nc + 5))
            grid = np.meshgrid(np.arange(w), np.arange(h))
            grid = np.expand_dims(np.stack(grid, axis=-1), axis=2)
            grid = np.tile(np.expand_dims(grid, axis=0), [
                1, 1, 1, na, 1])

            # Decoding
            xy = p[..., 0:2]
            wh = p[..., 2:4]
            obj = p[..., 4:5]
            probs = p[..., 5:]

            scores = obj * probs

            xy = (xy * 2.0 + grid - 0.5) / (w, h)
            wh = (wh * 2) ** 2 * anchors * 0.5
            xyxy = np.concatenate([
                xy - wh,
                xy + wh
            ], axis=-1)
            xyxy = xyxy.reshape((1, -1, 1, 4))
            scores = scores.reshape(1, -1, nc)

            bboxes.append(xyxy)
            bscores.append(scores)

    if len(bboxes) and len(bscores):
        bscores = np.concatenate(bscores, axis=1).astype(np.float32)
        bboxes = np.concatenate(bboxes, axis=1).astype(np.float32)

        output = [bboxes, bscores]
        decoded_outputs["boxes"] = 0
        decoded_outputs["scores"] = 1

        if decoded_outputs["masks"] is not None:
            output.append(outputs[decoded_outputs["masks"]])
            decoded_outputs["masks"] = len(output) - 1

        if decoded_outputs["segmentation"] is not None:
            output.append(outputs[decoded_outputs["segmentation"]])
            decoded_outputs["segmentation"] = len(output) - 1

        decoded_outputs["outputs"] = output

    return decoded_outputs
