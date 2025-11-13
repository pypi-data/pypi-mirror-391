from __future__ import annotations

import collections.abc
from typing import TYPE_CHECKING, Tuple

import numpy as np

from edgefirst.validator.datasets.utils.transformations import convert_to_serializable
from edgefirst.validator.evaluators.callbacks import Callback

if TYPE_CHECKING:
    from edgefirst.validator.publishers import StudioPublisher
    from edgefirst.validator.evaluators import CombinedParameters
    from edgefirst.validator.metrics import Metrics, Plots


class PlotsCallback(Callback):
    """
    Generates the plots compatible for ApexCharts
    and saves as JSON files to be published to EdgeFirst Studio.

    Parameters
    -----------
    studio_publisher: StudioPublisher
        Publishes metrics, timings, plots, and
        progress to EdgeFirst Studio.
    parameters: CombinedParameters
        These are the model, dataset, and validation parameters
        set from the command line.
    """

    def __init__(
        self,
        studio_publisher: StudioPublisher,
        parameters: CombinedParameters
    ):
        super(PlotsCallback, self).__init__(studio_publisher=studio_publisher,
                                            parameters=parameters)

    def create_apexchart_bar(
        self,
        series: list,
        title: str,
        categories: list,
        xlabel: str = None,
        ylabel: str = None,
        enabled_labels: bool = True
    ) -> dict:
        """
        Create a bar chart config dictionary for ApexCharts.

        Parameters
        ----------
        series : list
            Data series for the bar chart.
        title : str
            Title of the chart.
        categories : list
            X-axis categories.
        xlabel : str, optional
            Label for the x-axis.
        ylabel : str, optional
            Label for the y-axis.
        enabled_labels : bool, default=True
            Whether to show data labels.

        Returns
        -------
        dict
            Configuration dictionary for an ApexCharts bar chart.
        """
        chart = {
            "series": series,
            "chart": {"type": "bar"},
            "title": {"text": title},
            "dataLabels": {
                "enabled": enabled_labels,
                "style": {
                    "colors": ['#000000']
                },
            },
        }

        if xlabel is not None:
            chart["xaxis"] = {
                "categories": categories,
                "title": {
                    "text": xlabel
                }
            }
        else:
            chart["xaxis"] = {"categories": categories}

        if ylabel is not None:
            chart["yaxis"] = {
                "title": {
                    "text": ylabel
                }
            }
        return chart

    def create_apexchart_pie(
        self,
        series: list,
        title: str,
        categories: list
    ) -> dict:
        """
        Creates a pie chart config dictionary for ApexCharts.

        Parameters
        ----------
        series: list
            A list of values to display as a pie chart. These
            values will automatically be converted into percentages.
        title: str
            Specify the title for the chart.
        categories: list
            Specify the categories for each value in the series.

        Returns
        -------
        dict
            Configuration dictionary for an ApexCharts pie chart.
        """
        chart = {
            "series": series,
            "chart": {"type": "pie"},
            "title": {"text": title},
            "labels": categories,
        }
        return chart

    def create_apexchart_grid(
        self,
        data: dict,
        labels: list,
        title: str
    ) -> dict:
        """
        Create a heatmap chart config for ApexCharts from grid data.

        Parameters
        ----------
        data : dict
            Mapping of label to data rows (2D array-like).
        labels : list
            Class labels for axes.
        title : str
            Title of the chart.

        Returns
        -------
        dict
            Configuration dictionary for an ApexCharts heatmap chart.
        """
        chart = {
            "series": [{"name": label, "data": row.tolist()}
                       for row, label in zip(data, labels)],
            "chart": {"type": "heatmap"},
            "xaxis": {
                "categories": labels,
                "title": {"text": "Ground Truth"}
            },
            "yaxis": {
                "categories": labels,
                "title": {"text": "Predictions"}
            },
            "title": {"text": title}
        }

        return chart

    def create_apexchart_lines(
        self,
        x: np.ndarray,
        data: np.ndarray,
        labels: list,
        title: str,
        xlabel: str = "Recall",
        ylabel: str = "Precision"
    ) -> dict:
        """
        Create a line chart config for precision-recall visualization.

        Parameters
        ----------
        x : np.ndarray
            X-axis values (e.g., recall).
        data : np.ndarray
            Y-axis values (e.g., precision) per label.
        labels : list
            List of label names for the lines.
        title : str
            Title of the chart.
        xlabel : str
            The x-axis label.
        ylabel : str
            The y-axis label.

        Returns
        -------
        dict
            Configuration dictionary for an ApexCharts line chart.
        """
        lines = []
        labels = labels.tolist() if isinstance(labels, np.ndarray) else labels
        if len(x):
            for i, row in enumerate(data):
                if isinstance(row, collections.abc.Iterable):
                    lines.append({
                        "name": labels[i + 1] if "background" in labels else labels[i],
                        "data": np.concatenate([np.round(x[:, None], 2),
                                                np.round(row[:, None], 2)],
                                               axis=1).tolist()
                    })

        chart = {
            "series": lines,
            "chart": {"type": "line"},
            "xaxis": {
                "type": "numeric",
                "title": {"text": xlabel},
                "min": 0.0,
                "max": 1.0
            },
            "yaxis": {
                "type": "numeric",
                "title": {"text": ylabel},
                "min": 0.0,
                "max": 1.0
            },
            "title": {"text": title}
        }

        return chart

    @staticmethod
    def create_histogram(
        data: np.ndarray,
        num_bins: int = None
    ) -> Tuple[list, list]:
        """
        Create histogram bin counts and edges from data.

        Parameters
        ----------
        data : np.ndarray
            1D array of numeric values.
        num_bins : int, optional
            Number of bins to use (default uses Sturges' formula).

        Returns
        -------
        Tuple[list, list]
            list
                List of bin counts.
            list
                List of bin edge values (as ints).
        """
        min_value = np.min(data)
        max_value = np.max(data)

        # Use Sturges' formula if number of bins is not provided.
        if num_bins is None:
            num_bins = int(np.ceil(np.log2(len(data)) + 1))

        bin_edges = np.linspace(min_value, max_value, num_bins + 1)
        bin_edges_int = np.floor(bin_edges).astype(int)
        counts, _ = np.histogram(data, bins=bin_edges)

        return counts.tolist(), bin_edges_int.tolist()

    def save_detection_metrics(self, metrics: Metrics, plots: Plots):
        """
        Save detection charts and metrics as ApexChart JSON files.

        Parameters
        ----------
        metrics : Metrics
            Detection evaluation metrics.
        plots : Plots
            Curves and confusion matrix data for plotting.
        """
        # Save Confusion Matrix
        chart = self.create_apexchart_grid(plots.confusion_matrix,
                                           plots.confusion_labels,
                                           title="Confusion Matrix [Detection]")
        self.studio_publisher.save_json(
            filename="detection_confusion_matrix.json",
            plot=chart
        )

        # Save Precision vs. Recall Curve
        precision = plots.py
        recall = plots.px

        x = np.linspace(0.0, 1.0, recall.shape[0])
        x_downsampled = np.linspace(0.0, 1.0, 100)
        r_downsampled = np.interp(x_downsampled, x, recall)
        p_downsampled = []

        for p in precision:
            p = np.interp(x_downsampled, x, p)
            p_downsampled.append(p)

        p_downsampled = np.array(p_downsampled)

        chart = self.create_apexchart_lines(
            r_downsampled,
            p_downsampled,
            plots.curve_labels,
            title="Precision vs. Recall [Detection]"
        )

        p_mean = p_downsampled.mean(0) if len(p_downsampled) else None
        if p_mean is not None:
            chart["series"].append({
                "name": "all classes",
                "data": np.concatenate(
                    [np.round(r_downsampled[:, None], 2),
                     np.round(p_mean[:, None], 2)], axis=1).tolist()
            })

        self.studio_publisher.save_json(
            filename="detection_precision_recall.json",
            plot=chart
        )

        if self.parameters.validation.method in ["ultralytics", "yolov7"]:
            # Save Ultralytics Metrics
            categories = ["Mean Precision", "Mean Recall", "F1",
                          "mAP@0.50", "mAP@0.75", "mAP@0.50:0.95"]
            series = [{"name": "Score",
                       "data": [round(metrics.precision["mean"], 4),
                                round(metrics.recall["mean"], 4),
                                round(metrics.f1["mean"], 4),
                                round(metrics.precision["map"]["0.50"], 4),
                                round(metrics.precision["map"]["0.75"], 4),
                                round(metrics.precision["map"]["0.50:0.95"], 4)]}]

            chart = self.create_apexchart_bar(
                series=series,
                title="Detection Metrics",
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="detection_metrics.json",
                plot=chart
            )

            # Save F1 Curve
            f1_downsampled = []
            for f1 in plots.f1:
                f1 = np.interp(x_downsampled, x, f1)
                f1_downsampled.append(f1)
            f1_downsampled = np.array(f1_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                f1_downsampled,
                plots.curve_labels,
                title="F1 vs. Confidence [Detection]",
                xlabel="Confidence",
                ylabel="F1"
            )
            self.studio_publisher.save_json(
                filename="detection_f1_curve.json",
                plot=chart
            )

            # Save Precision Curve
            precision_downsampled = []
            for p in plots.precision:
                p = np.interp(x_downsampled, x, p)
                precision_downsampled.append(p)
            precision_downsampled = np.array(precision_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                precision_downsampled,
                plots.curve_labels,
                title="Precision vs. Confidence [Detection]",
                xlabel="Confidence",
            )
            self.studio_publisher.save_json(
                filename="detection_precision_curve.json",
                plot=chart
            )

            # Save Recall Curve
            recall_downsampled = []
            for r in plots.recall:
                r = np.interp(x_downsampled, x, r)
                recall_downsampled.append(r)
            recall_downsampled = np.array(recall_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                recall_downsampled,
                plots.curve_labels,
                title="Recall vs. Confidence [Detection]",
                xlabel="Confidence",
                ylabel="Recall"
            )
            self.studio_publisher.save_json(
                filename="detection_recall_curve.json",
                plot=chart
            )

        else:
            # Save EdgeFirst Overall Metrics
            categories = ["accuracy", "precision", "recall"]
            series = [{"data": [
                round(metrics.accuracy["overall"], 4),
                round(metrics.precision["overall"], 4),
                round(metrics.recall["overall"], 4)
            ]}]
            chart = self.create_apexchart_bar(
                series=series,
                title="Overall Metrics [Detection]",
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="detection_overall_metrics.json",
                plot=chart
            )

            # Save EdgeFirst Mean Average Metrics
            categories = ["mACC", "mAP", "mAR"]
            series = []
            for key in ["0.50", "0.75", "0.50:0.95"]:
                series.append({"data": [
                    round(metrics.accuracy["macc"].get(key, 0), 4),
                    round(metrics.precision["map"].get(key, 0), 4),
                    round(metrics.recall["mar"].get(key, 0), 4),
                ], "name": "IoU threshold @ %s" % (key)})

            chart = self.create_apexchart_bar(
                series=series,
                title="Mean Average Metrics [Detection]",
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="detection_metrics.json",
                plot=chart
            )

            # Save Raw Classifications
            categories = ["True Positives", "False Negatives",
                          "Classification False Positives",
                          "Localization False Positives"]
            series = [{"data": [metrics.tp,
                                metrics.fn,
                                metrics.cfp,
                                metrics.lfp]}]
            chart = self.create_apexchart_bar(
                series=series,
                title="Prediction Classifications",
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="prediction_classifications.json",
                plot=chart
            )

            # Save Class Histogram
            # Only save this chart if there are multiple classes.
            if len(plots.class_histogram_data.keys()) > 1:
                series = []
                categories = ["accuracy", "precision", "recall"]
                for key, item in plots.class_histogram_data.items():
                    series.append({"data": [round(item.get('accuracy', 0), 4),
                                            round(item.get('precision', 0), 4),
                                            round(item.get('recall', 0), 4),
                                            ], "name": key})

                chart = self.create_apexchart_bar(
                    series=series,
                    title="Class Metrics [Detection]",
                    categories=categories,
                    enabled_labels=False
                )
                self.studio_publisher.save_json(
                    filename="detection_class_metrics.json",
                    plot=chart
                )

            # Save TP and FP scores Histogram
            bins = np.arange(0, 1.05, 0.05)  # 0.0 to 1.0 with step 0.05
            tp_scores = np.concatenate(plots.tp_scores, axis=0),
            fp_scores = np.concatenate(plots.fp_scores, axis=0),

            tp_hist, _ = np.histogram(tp_scores, bins=bins)
            fp_hist, _ = np.histogram(fp_scores, bins=bins)

            # Convert bin ranges to readable category labels
            categories = [
                f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins) - 1)]

            series = [
                {
                    "name": "True Positives",
                    "data": tp_hist.tolist(),
                    "color": "#00FF00"  # Green
                },
                {
                    "name": "False Positives",
                    "data": fp_hist.tolist(),
                    "color": "#FF0000"  # Red
                }
            ]

            chart = self.create_apexchart_bar(
                series=series,
                title="Histogram of True Positive vs False Positive Scores",
                categories=categories,
                xlabel="Score",
                ylabel="Count",
                enabled_labels=True
            )

            self.studio_publisher.save_json(
                filename="tp_fp_scores.json",
                plot=chart
            )

    def save_segmentation_metrics(self, metrics: Metrics, plots: Plots):
        """
        Save segmentation metrics and class-wise histogram charts.

        Parameters
        ----------
        metrics : Metrics
            Segmentation evaluation metrics.
        plots : Plots
            Class histogram and plot data.
        """
        if self.parameters.validation.method in ["ultralytics", "yolov7"]:
            # Save Precision vs. Recall Curve
            precision = plots.py
            recall = plots.px

            x = np.linspace(0.0, 1.0, recall.shape[0])
            x_downsampled = np.linspace(0.0, 1.0, 100)
            if len(recall):
                r_downsampled = np.interp(x_downsampled, x, recall)
            else:
                r_downsampled = []
            p_downsampled = []

            for p in precision:
                p = np.interp(x_downsampled, x, p)
                p_downsampled.append(p)

            p_downsampled = np.array(p_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                p_downsampled,
                plots.curve_labels,
                title="Precision vs. Recall [Segmentation]"
            )

            p_mean = p_downsampled.mean(0) if len(p_downsampled) else None
            if p_mean is not None:
                chart["series"].append({
                    "name": "all classes",
                    "data": np.concatenate(
                        [np.round(r_downsampled[:, None], 2),
                         np.round(p_mean[:, None], 2)], axis=1).tolist()
                })

            self.studio_publisher.save_json(
                filename="segmentation_precision_recall.json",
                plot=chart
            )

            # Save Ultralytics Metrics
            categories = ["Mean Precision", "Mean Recall", "F1",
                          "mAP@0.50", "mAP@0.75", "mAP@0.50:0.95"]
            series = [{"name": "Score",
                       "data": [round(metrics.precision["mean"], 4),
                                round(metrics.recall["mean"], 4),
                                round(metrics.f1["mean"], 4),
                                round(metrics.precision["map"]["0.50"], 4),
                                round(metrics.precision["map"]["0.75"], 4),
                                round(metrics.precision["map"]["0.50:0.95"], 4)]}]

            chart = self.create_apexchart_bar(
                series=series,
                title="Segmentation Metrics",
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="segmentation_metrics.json",
                plot=chart
            )

            # Save F1 Curve
            f1_downsampled = []
            for f1 in plots.f1:
                f1 = np.interp(x_downsampled, x, f1)
                f1_downsampled.append(f1)
            f1_downsampled = np.array(f1_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                f1_downsampled,
                plots.curve_labels,
                title="F1 vs. Confidence [Segmentation]",
                xlabel="Confidence",
                ylabel="F1"
            )
            self.studio_publisher.save_json(
                filename="segmentation_f1_curve.json",
                plot=chart
            )

            # Save Precision Curve
            precision_downsampled = []
            for p in plots.precision:
                p = np.interp(x_downsampled, x, p)
                precision_downsampled.append(p)
            precision_downsampled = np.array(precision_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                precision_downsampled,
                plots.curve_labels,
                title="Precision vs. Confidence [Segmentation]",
                xlabel="Confidence"
            )
            self.studio_publisher.save_json(
                filename="segmentation_precision_curve.json",
                plot=chart
            )

            # Save Recall Curve
            recall_downsampled = []
            for r in plots.recall:
                r = np.interp(x_downsampled, x, r)
                recall_downsampled.append(r)
            recall_downsampled = np.array(recall_downsampled)

            chart = self.create_apexchart_lines(
                r_downsampled,
                recall_downsampled,
                plots.curve_labels,
                title="Recall vs. Confidence [Segmentation]",
                xlabel="Confidence",
                ylabel="Recall"
            )
            self.studio_publisher.save_json(
                filename="segmentation_recall_curve.json",
                plot=chart
            )

        else:
            # Save Segmentation Metrics
            series = [{"data": [round(metrics.accuracy["mean"], 4),
                                round(metrics.precision["mean"], 4),
                                round(metrics.recall["mean"], 4)]}]
            categories = ["accuracy", "precision", "recall"]

            chart = self.create_apexchart_bar(
                series=series,
                title='Segmentation Metrics',
                categories=categories
            )
            self.studio_publisher.save_json(
                filename="segmentation_metrics.json",
                plot=chart
            )

            # Save Class Histogram
            # Only save this chart if there are multiple classes.
            if len(plots.class_histogram_data.keys()) > 1:
                series = []
                for key, item in plots.class_histogram_data.items():
                    series.append({"data": [round(item.get('accuracy', 0), 4),
                                            round(item.get('precision', 0), 4),
                                            round(item.get('recall', 0), 4),
                                            ], "name": key})

                chart = self.create_apexchart_bar(
                    series=series,
                    title="Segmentation Class Metrics",
                    categories=categories,
                    enabled_labels=False
                )
                self.studio_publisher.save_json(
                    filename="segmentation_class_metrics.json",
                    plot=chart
                )

    def save_timings(self, timings: dict):
        """
        Save model timing metrics for input, inference, and output stages.

        Parameters
        ----------
        timings : dict
            Timing stats (min, max, avg) in milliseconds.
        """
        categories = ["Read Time", "Load Time", "Backbone Time",
                      "Decode Time", "Box Time"]
        keys = ["read_time", "load_time", "backbone_time",
                "decode_time", "box_time"]

        # Create a bar chart of the timings.
        series = []
        for name in ["Min", "Max", "Avg"]:
            data = []
            for key in keys:
                data.append(
                    round(float(timings.get(f"{name.lower()}_{key}")), 2))
            series.append({"data": data, "name": name})

        chart = self.create_apexchart_bar(
            series=series,
            title='Timings (ms)',
            categories=categories
        )

        self.studio_publisher.save_json(
            filename="timings.json",
            plot=chart
        )

        # Create a pie chart of the timings.
        series = []
        for key in ["avg_read_time", "avg_load_time", "avg_backbone_time",
                    "avg_decode_time", "avg_box_time"]:
            series.append(round(float(timings.get(key, 2))))

        chart = self.create_apexchart_pie(
            series=series,
            title="Distribution of the Average Timings",
            categories=categories
        )

        self.studio_publisher.save_json(
            filename="average_timings.json",
            plot=chart
        )

    def post_metrics(self, logs=None):
        """
        Post the final metrics to EdgeFirst Studio.

        Parameters
        ----------
        logs: dict, optional
            This is a container of the final metrics.
        """
        metrics = dict()
        if "multitask" in logs.keys():
            metrics = logs.get("multitask")
            metrics = metrics.to_dict(method=self.parameters.validation.method)

        elif "detection" in logs.keys():
            metrics = logs.get("detection")
            metrics = metrics.to_dict(with_boxes=True,
                                      method=self.parameters.validation.method)

        elif "segmentation" in logs.keys():
            metrics = logs.get("segmentation")
            metrics = metrics.to_dict(with_boxes=False,
                                      method=self.parameters.validation.method)

        parameters = self.parameters.to_dict()
        metrics["parameters"] = parameters

        self.studio_publisher.post_metrics(convert_to_serializable(metrics))

    def on_test_batch_end(self, step: int, logs=None):
        """
        Update progress status at the end of a validation batch.

        Parameters
        ----------
        step : int
            Current validation batch index.
        logs : dict, optional
            Contains total number of steps for percentage calculation.
        """

        percentage = 0
        if logs is not None:
            total = logs.get("total")
            if total > 0:
                percentage = int((step / total) * 100)

        self.studio_publisher.update_stage(
            stage=self.stage,
            status="running",
            message=self.message,
            percentage=percentage
        )

    def on_test_error(self, step: int, error, logs=None):
        """
        Report an error during validation and update the progress.

        Parameters
        ----------
        step : int
            Batch step at which the error occurred.
        error : Exception
            The exception raised during validation.
        logs : dict, optional
            Contains total number of steps for percentage calculation.
        """
        percentage = 0
        if logs is not None:
            total = logs.get("total")
            if total > 0:
                percentage = int((step / total) * 100)

        self.studio_publisher.update_stage(
            stage=self.stage,
            status="error",
            message=str(error),
            percentage=percentage
        )

    def on_test_end(self, logs=None):
        """
        Report the final stages of validation
        and post the metrics.

        logs : dict, optional
            Contains the metrics.
        """
        plots = logs.get("plots")
        timings = logs.get("timings")

        if "multitask" in logs.keys():
            self.save_detection_metrics(
                logs.get("multitask").detection_metrics, plots.detection_plots)
            self.save_segmentation_metrics(
                logs.get("multitask").segmentation_metrics, plots.segmentation_plots)
        elif "detection" in logs.keys():
            self.save_detection_metrics(logs.get("detection"), plots)
        elif "segmentation" in logs.keys():
            self.save_segmentation_metrics(logs.get("segmentation"), plots)
        self.save_timings(timings)
        self.post_metrics(logs)

        self.studio_publisher.update_stage(
            stage=self.stage,
            status="complete",
            message=self.message,
            percentage=100
        )
        self.studio_publisher.post_plots()
