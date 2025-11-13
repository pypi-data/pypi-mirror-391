from __future__ import annotations

import io
from typing import TYPE_CHECKING, List

import numpy as np
import seaborn as sn
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure

from edgefirst.validator.metrics.utils.math import batch_iou

if TYPE_CHECKING:
    from edgefirst.validator.datasets import DetectionInstance

matplotlib.use('Agg')


def figure2numpy(figure: matplotlib.figure.Figure) -> np.ndarray:
    """
    Converts a matplotlib.figure.Figure into a NumPy
    array so that it can be published to Tensorboard.

    Parameters
    ----------
    figure: matplotlib.figure.Figure
        This is the figure to convert to a numpy array.

    Returns
    -------
    np.ndarray
        The figure that is represented as a numpy array.
    """
    io_buf = io.BytesIO()
    figure.savefig(io_buf, format='raw')
    io_buf.seek(0)
    nimage = np.reshape(
        np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
        newshape=(int(figure.bbox.bounds[3]), int(figure.bbox.bounds[2]), -1))
    io_buf.close()
    return nimage


def plot_classification_detection(
    class_histogram_data: dict,
    model: str = "Model",
) -> matplotlib.figure.Figure:
    """
    Plots the bar charts showing the precision, recall, and accuracy per class.
    It also shows the number of true positives, false positives,
    and false negatives per class.

    Parameters
    ----------
    class_histogram_data: dict.
        This contains information about the metrics per class.

        .. code-block:: python

            {
                'label_1': {
                    'precision': "The calculated precision at
                            IoU threshold 0.5 for the class",
                    'recall': "The calculated recall at
                            IoU threshold 0.5 for the class",
                    'accuracy': "The calculated accuracy at
                            IoU threshold 0.5 for the class",
                    'tp': "The number of true positives for the class",
                    'fn': "The number of false negatives for the class",
                    'fp': "The number of localization and
                            classification false positives for the class",
                    'gt': "The number of grounds truths for the class"
                },
                'label_2': ...
            }

    model: str
        The name of the model.

    Returns
    -------
    matplotlib.figure.Figure
        This shows two histograms on the left that compares
        the precision, recall, and accuracy and on the right
        compares the number of true positives, false positives,
        and false negatives for each class.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 10))
    # Score = [[prec c1, prec c2, prec c3], [rec c1, rec c2, rec c3], [acc c1,
    # acc c2, acc c3]]
    X = np.arange(len(class_histogram_data))
    labels, precision, recall, accuracy = list(), list(), list(), list()
    tp, fp, fn = list(), list(), list()

    for cls, value, in class_histogram_data.items():
        labels.append(cls)
        precision.append(round(value.get('precision') * 100, 2))
        recall.append(round(value.get('recall') * 100, 2))
        accuracy.append(round(value.get('accuracy') * 100, 2))
        tp.append(value.get('tp'))
        fn.append(value.get('fn'))
        fp.append(value.get('fp'))

    ax1.bar(X + 0.0, precision, color='m', width=0.25)
    ax1.bar(X + 0.25, recall, color='y', width=0.25)
    ax1.bar(X + 0.5, accuracy, color='c', width=0.25)

    ax2.bar(X + 0.0, tp, color='LimeGreen', width=0.25)
    ax2.bar(X + 0.25, fn, color='RoyalBlue', width=0.25)
    ax2.bar(X + 0.5, fp, color='OrangeRed', width=0.25)

    ax1.set_ylim(0, 100)

    ax1.set_ylabel('Score (%)')
    ax2.set_ylabel("Total Number")
    fig.suptitle(f"{model} Evaluation Table")

    ax1.xaxis.set_ticks(range(len(labels)), labels, rotation='vertical')
    ax2.xaxis.set_ticks(range(len(labels)), labels, rotation='vertical')

    colors = {'precision': 'm', 'recall': 'y', 'accuracy': 'c'}
    labels = list(colors.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label])
               for label in labels]
    ax1.legend(handles, labels)
    colors = {'true positives': 'green',
              'false negatives': 'blue',
              'false positives': 'red'}
    labels = list(colors.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label])
               for label in labels]
    ax2.legend(handles, labels)
    return fig


def plot_classification_segmentation(
    class_histogram_data: dict,
    model: str = "Model"
) -> matplotlib.figure.Figure:
    """
    Plots the bar charts showing the precision,
    recall, and accuracy per class.
    It also shows the number of true predictions
    and false predictions per class.

    Parameters
    ----------
    class_histogram_data: dict.
        This contains information about the metrics per class.

        .. code-block:: python

            {
                'label_1': {
                    'precision': "The calculated precision for the class",
                    'recall': "The calculated recall for the class",
                    'accuracy': "The calculated accuracy for the class",
                    'true_predictions': "The number of true prediction
                                        pixels of the class",
                    'false_predictions': "The number of false prediction
                                        pixels of the class",
                    'gt': "The number of grounds truths for the class"
                },
                'label_2': ...
            }

    model: str
        The name of the model.

    Returns
    -------
    matplotlib.figure.Figure
        This shows two histograms on the left that compares
        the precision, recall, and accuracy and on the right
        compares the number of true prediction and
        false prediction pixels for each class.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 10))
    # Score = [[prec c1, prec c2, prec c3], [rec c1, rec c2, rec c3], [acc c1,
    # acc c2, acc c3]]
    X = np.arange(len(class_histogram_data))
    labels, precision, recall, accuracy = list(), list(), list(), list()
    true_predictions, false_predictions = list(), list()

    for cls, value, in class_histogram_data.items():
        labels.append(cls)
        precision.append(round(value.get('precision') * 100, 2))
        recall.append(round(value.get('recall') * 100, 2))
        accuracy.append(round(value.get('accuracy') * 100, 2))
        true_predictions.append(value.get('true_predictions'))
        false_predictions.append(value.get('false_predictions'))

    ax1.bar(X + 0.0, precision, color='m', width=0.25)
    ax1.bar(X + 0.25, recall, color='y', width=0.25)
    ax1.bar(X + 0.5, accuracy, color='c', width=0.25)

    ax2.bar(X + 0.0, true_predictions, color='LimeGreen', width=0.25)
    ax2.bar(X + 0.25, false_predictions, color='OrangeRed', width=0.25)

    ax1.set_ylim(0, 100)

    ax1.set_ylabel('Score (%)')
    ax2.set_ylabel("Total Number")
    fig.suptitle(f"{model} Evaluation Table")

    ax1.xaxis.set_ticks(range(len(labels)), labels, rotation='vertical')
    ax2.xaxis.set_ticks(range(len(labels)), labels, rotation='vertical')

    colors = {'precision': 'm', 'recall': 'y', 'accuracy': 'c'}
    labels = list(colors.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label])
               for label in labels]
    ax1.legend(handles, labels)
    colors = {'true predictions': 'green',
              'false predictions': 'red'}
    labels = list(colors.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label])
               for label in labels]
    ax2.legend(handles, labels)
    return fig


def plot_score_histogram(
        tp_scores: np.ndarray, fp_scores: np.ndarray, model: str = "Model",):
    """
    Create a score histogram to compare the number of true positives
    and false positives based on the scores. This provides insight
    on the optimal thresholds to use. Also draws count labels
    on each histogram bar.

    Parameters
    ----------
    tp_scores: np.ndarray
        All the scores for the true positives.
    fp_scores: np.ndarray
        All the scores for the false positives.
    model: str
        The name of the model evaluated.

    Returns
    -------
    matplotlib.figure.Figure
        This shows the histogram comparing the scores of the
        true positives and false positives.
    """
    # Define histogram bins: 0.0 to 1.0 with step of 0.05
    bins = np.arange(0, 1.05, 0.05)

    # Compute histograms (counts only)
    tp_hist, _ = np.histogram(tp_scores, bins=bins)
    fp_hist, _ = np.histogram(fp_scores, bins=bins)

    # Plot histograms
    fig, ax = plt.subplots(1, 1, figsize=(10, 5), tight_layout=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    tp_bars = ax.bar(bin_centers - 0.01,
                     tp_hist,
                     width=0.02,
                     label='True Positives',
                     alpha=0.7, color='green')
    fp_bars = ax.bar(bin_centers + 0.01,
                     fp_hist,
                     width=0.02,
                     label='False Positives',
                     alpha=0.7, color='red')

    # Annotate each bar with count
    for i, (tp_bar, fp_bar) in enumerate(zip(tp_bars, fp_bars)):
        tp_count = tp_hist[i]
        fp_count = fp_hist[i]
        if tp_count > 0:
            ax.text(tp_bar.get_x() + tp_bar.get_width() / 2,
                    tp_bar.get_height() + 0.5,
                    str(tp_count),
                    ha='center', va='bottom', fontsize=8, color='green')
        if fp_count > 0:
            ax.text(fp_bar.get_x() + fp_bar.get_width() / 2,
                    fp_bar.get_height() + 0.5,
                    str(fp_count),
                    ha='center', va='bottom', fontsize=8, color='red')

    ax.set_xlabel('Score')
    ax.set_ylabel('Count')
    ax.set_title(f'{model} Histogram of TP vs FP Scores')
    ax.set_xticks(bins)
    ax.legend()
    ax.grid(True)
    return fig


def plot_pr(
    precision: np.ndarray,
    recall: np.ndarray,
    ap: np.ndarray,
    names: list = [],
    model: str = "Model",
    iou_threshold: float = 0.50
) -> matplotlib.figure.Figure:
    """
    Version 1 Ploting precision and recall per class and the average metric.
    Use this method for edgefirst-validator implementation of precision recall
    curve.

    Parameters
    ----------
    precision: (NxM) np.ndarray
        N => number of classes and M is the number of precision values.
    recall: (NxM) np.ndarray
        N => number of classes and M is the number of recall values.
    ap: (NxM) np.ndarray
        N => number of classes, M => 10 denoting each IoU threshold
        from (0.5 to 0.95 at 0.05 intervals).
    names: list
        This contains the unique string labels captured in the order
        that respects the data for precision and recall.
    model: str
        The name of the model evaluated.
    iou_threshold: float
        The iou threshold used for the mAP calculation.

    Returns
    -------
    matplotlib.figure.Figure
        The precision recall plot where recall is denoted
        on the x-axis and precision is denoted
        on the y-axis.
    """
    fig, ax = plt.subplots(1, 1, figsize=(9, 6), tight_layout=True)
    if 0 < len(names) < 21:  # display per-class legend if < 21 classes
        for i, (p, r) in enumerate(zip(precision, recall)):
            # plot(recall, precision)
            ax.plot(r, p, linewidth=1, label=f'{names[i]} {ap[i, 0]:.3f}')
    else:
        # plot(recall, precision)
        for prec, rec in zip(precision, recall):
            ax.plot(rec, prec, linewidth=1, color='grey')

    ax.plot(
        np.mean(recall, axis=0),
        np.mean(precision, axis=0),
        linewidth=3,
        color='blue',
        label='all classes %.3f mAP@%.2f' % (ap[:, 0].mean(), iou_threshold))

    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    ax.set_title(f'{model} Precision-Recall Curve')
    return fig


def plot_pr_curve(
    precision: np.ndarray,
    recall: np.ndarray,
    ap: np.ndarray,
    names: list = [],
    model: str = "Model",
    iou_threshold: float = 0.50
) -> matplotlib.figure.Figure:
    """
    Version 2 Ploting precision and recall per class and the average metric.
    Use this method for YoloV5 implementation of precision recall
    curve.

    Parameters
    ----------
    precision: (NxM) np.ndarray
        N => number of classes and M is the number of precision values.
    recall: (NxM) np.ndarray
        N => number of classes and M is the number of recall values.
    ap: (NxM) np.ndarray
        N => number of classes, M => 10 denoting each IoU threshold
        from (0.5 to 0.95 at 0.05 intervals).
    names: list
        This contains the unique string labels captured in the order
        that respects the data for precision and recall.
    model: str
        The name of the model evaluated.
    iou_threshold: float
        The iou threshold used for the mAP calculation.

    Returns
    -------
    matplotlib.figure.Figure
        The precision recall plot where recall is denoted
        on the x-axis and precision is denoted
        on the y-axis.
    """
    # Precision-recall curve
    fig, ax = plt.subplots(1, 1, figsize=(9, 6), tight_layout=True)
    if len(precision) == 0:
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        ax.set_title(f'{model} Precision-Recall Curve')
        return fig

    precision = np.stack(precision, axis=1)
    if (0 < len(names) < 21):  # display per-class legend if < 21 classes
        for i, y in enumerate(precision.T):
            # plot(recall, precision)
            ax.plot(recall, y, linewidth=1, label=f"{names[i]} {ap[i, 0]:.3f}")
    else:
        # plot(recall, precision)
        ax.plot(recall, precision, linewidth=1, color="grey")

    ax.plot(
        recall,
        precision.mean(1),
        linewidth=3,
        color="blue",
        label="all classes %.3f mAP@%.2f" % (ap[:, 0].mean(), iou_threshold))
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    ax.set_title(f'{model} Precision-Recall Curve')
    return fig


def plot_mc_curve(
    px: np.ndarray,
    py: np.ndarray,
    names: list = [],
    model: str = "Model",
    xlabel: str = 'Confidence',
    ylabel: str = 'Metric'
) -> matplotlib.figure.Figure:
    """
    This function is used for plotting either the F1-curve or the
    precision/recall versus confidence curves.

    Parameters
    ----------
    px: (NxM) np.ndarray
        N => number of classes.
    py: (NxM) np.ndarray
        This could be values for the F1, precision, or recall.
    names: list
        This contains the unique string labels captured in the order
        that respects the data for precision and recall.
    model: str
        The name of the model evaluated.
    xlabel: str
        The metric on the x-axis.
    ylabel: str
        The metric on the y-axis.

    Returns
    -------
    matplotlib.figure.Figure
        The plot where recall is denoted
        on the x-axis and either  is denoted
        on the y-axis.
    """
    # Metric-confidence curve
    fig, ax = plt.subplots(1, 1, figsize=(9, 6), tight_layout=True)

    if 0 < len(names) < 21:  # display per-class legend if < 21 classes
        for i, y in enumerate(py):
            # plot(confidence, metric)
            ax.plot(px, y, linewidth=1, label=f'{names[i]}')
    else:
        # plot(confidence, metric)
        ax.plot(px, py.T, linewidth=1, color='grey')

    y = py.mean(0)
    ax.plot(px, y, linewidth=3, color='blue',
            label=f'all classes {y.max():.2f} at {px[y.argmax()]:.3f}')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f'{model} {ylabel}-{xlabel} Curve')
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    return fig


def plot_confusion_matrix(
    confusion_data: np.ndarray,
    labels: list,
    model: str = "Model"
) -> matplotlib.figure.Figure:
    """
    Plots the confusion matrix using the method defined below:
    https://stackoverflow.com/questions/5821125/how-to-plot-confusion-matrix-with-string-axis-rather-than-integer-in-python/74152927#74152927

    Parameters
    ----------
    confusion_data: np.ndarray
        This is a square matrix representing the confusion matrix data
        where the rows are the predictions and the columns are the
        ground truth.
    labels: list
        This contains the unique string labels in the dataset.
    model: str
        The name of the model being validated.

    Returns
    --------
    matplotlib.figure.Figure
        The confusion matrix plot.
    """
    norm_conf = []
    for i in confusion_data:
        a = 0
        tmp_arr = []
        a = sum(i, 0)
        for j in i:
            try:
                tmp_arr.append(float(j) / float(a))
            except ZeroDivisionError:
                tmp_arr.append(0.)
        norm_conf.append(tmp_arr)

    fig = plt.figure()
    plt.clf()
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    res = ax.imshow(np.array(norm_conf), cmap=plt.cm.jet,
                    interpolation='nearest')
    width, height = confusion_data.shape

    for x in range(width):
        for y in range(height):
            ax.annotate(str(int(confusion_data[x][y])), xy=(y, x),
                        horizontalalignment='center',
                        verticalalignment='center')
    fig.colorbar(res)
    plt.xticks(range(width), labels[:width], rotation="vertical")
    plt.yticks(range(height), labels[:height])
    plt.ylabel("Prediction")
    plt.xlabel("Ground Truth")
    plt.title(f"{model} Confusion Matrix")
    return fig


def close_figures(figures: List[matplotlib.figure.Figure]):
    """
    Closes the matplotlib figures opened to prevent
    errors such as "Fail to allocate bitmap."

    Parameters
    ----------
    figures: List[matplotlib.figure.Figure]
        Contains matplotlib.pyplot figures to close.
    """
    if len(figures) > 0:
        for figure in figures:
            plt.close(figure)


class ConfusionMatrix:
    """
    This confusion matrix implementation was taken from YoloV7 to
    follow their validation implementation.

    Parameters
    -----------
    nc: int
        The number of classes in the dataset.
    conf: float
        The confidence threshold for plotting.
    iou_thres: float
        The IoU threshold for plotting.
    offset: int
        If the dataset labels already contains background,
        then this offset is 0. Otherwise the offset is +1
        to include the background class.
    """
    # Updated version of
    # https://github.com/kaanakan/object_detection_confusion_matrix

    def __init__(
        self,
        nc: int,
        conf: float = 0.25,
        iou_thres: float = 0.45,
        offset: int = 0
    ):
        self.matrix = np.zeros((nc + offset, nc + offset), dtype=np.int32)
        self.nc = nc  # number of classes
        self.conf = conf
        self.iou_thres = iou_thres
        self.offset = offset

    def process_batch(self, dt_instance: DetectionInstance,
                      gt_instance: DetectionInstance):
        """
        Return intersection-over-union (Jaccard index) of boxes.
        Both sets of boxes are expected to be in (x1, y1, x2, y2) format.

        Parameters
        ----------
        dt_instance: DetectionInstance
            A prediction instance container of the boxes, labels, and scores.
        gt_instance: DetectionInstance
            A ground truth instance container of the boxes and the labels.
        """

        if dt_instance is None:
            gt_classes = gt_instance.labels.astype(np.int32)
            for gc in gt_classes:
                self.matrix[0, gc + self.offset] += 1  # background FN
            return

        filt = dt_instance.scores > self.conf
        dt_boxes = dt_instance.boxes[filt]
        dt_classes = dt_instance.labels[filt]

        gt_boxes = gt_instance.boxes
        gt_classes = gt_instance.labels.astype(np.int32)
        dt_classes = dt_classes.astype(np.int32)
        iou = batch_iou(gt_boxes, dt_boxes)

        x = np.where(iou > self.iou_thres)
        if x[0].shape[0]:
            matches = np.concatenate(
                (np.stack(x, 1), iou[x[0], x[1]][:, None]), 1)
            if x[0].shape[0] > 1:
                matches = matches[matches[:, 2].argsort()[::-1]]
                matches = matches[np.unique(
                    matches[:, 1], return_index=True)[1]]
                matches = matches[matches[:, 2].argsort()[::-1]]
                matches = matches[np.unique(
                    matches[:, 0], return_index=True)[1]]
        else:
            matches = np.zeros((0, 3))

        n = matches.shape[0] > 0
        m0, m1, _ = matches.transpose().astype(int)
        for i, gc in enumerate(gt_classes):
            j = m0 == i
            # Asserting a unique match.
            if n and sum(j) == 1:
                self.matrix[dt_classes[m1[j]] + self.offset,
                            gc + self.offset] += 1  # correct
            else:
                self.matrix[0, gc + self.offset] += 1  # true background

        matched_detections = m1 if n else np.array([], dtype=int)
        for i, dc in enumerate(dt_classes):
            if i not in matched_detections:
                # false positive (predicted something not matched to GT)
                self.matrix[dc + self.offset, 0] += 1

    def plot(self, names=()) -> matplotlib.figure.Figure:
        """
        Plots the Confusion Matrix.

        Parameters
        ----------
        names: tuple
            All the unique labels in the dataset.

        Returns
        -------
        matplotlib.figure.Figure
            The Confusion Matrix figure.
        """
        array = self.matrix / \
            (self.matrix.sum(0).reshape(1, self.nc + self.offset) + 1E-6)  # normalize
        array[array < 0.005] = np.nan  # don't annotate (would appear as 0.00)

        fig = plt.figure(figsize=(12, 9), tight_layout=True)
        sn.set(font_scale=1.0 if self.nc < 50 else 0.8)  # for label size
        labels = (0 < len(names) < 99) and len(
            names) == self.nc  # apply names to ticklabels
        sn.heatmap(array, annot=self.nc < 30, annot_kws={"size": 8}, cmap='Blues', fmt='.2f', square=True,
                   xticklabels=names if labels else "auto",
                   yticklabels=names if labels else "auto").set_facecolor((1, 1, 1))
        fig.axes[0].set_xlabel('True')
        fig.axes[0].set_ylabel('Predicted')
        return fig

    def print(self):
        """
        Prints the Confusion Matrix.
        """
        for i in range(self.nc + self.offset):
            print(' '.join(map(str, self.matrix[i])))
