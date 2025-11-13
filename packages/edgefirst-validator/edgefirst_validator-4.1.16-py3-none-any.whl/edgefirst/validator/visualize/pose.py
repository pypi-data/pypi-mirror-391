from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw


class PoseDrawer:
    """
    This class draws the three axis for the roll, pitch, and yaw for
    the ground truth and model predictions.
    """

    def __init__(self):
        self.image_draw: ImageDraw.ImageDraw = None

    def draw_axes(
        self,
        nimage: np.ndarray,
        dt_euler: list,
        gt_euler: list,
        starting_position: tuple = None,
        gt_box: list = None
    ) -> Image.Image:
        """
        This function draws both the ground truth and the prediction axes.

        Parameters
        ----------
        nimage: np.ndarray
            This is the image as an NumPy array.
        dt_euler: list
            This is the prediction angles containing [roll, pitch, yaw]
            in radians.
        gt_euler: list
            This is the ground truth angles containing [roll, pitch, yaw]
            in radians.
        starting_position: tuple
            This is the point to start drawing the axis in (x,y).
        gt_box: list
            This is an optional bounding box around the object that is being
            rotated in [xmin, ymin, xmax, ymax].

        Returns
        -------
        Image.Image
            The image with ground truth and prediction axes and
            a bounding box around the object being analyzed.
        """
        image = Image.fromarray(nimage)
        self.image_draw = ImageDraw.Draw(image)

        if starting_position is None:
            if gt_box is None:
                height, width = nimage.shape[:2]
                starting_position = (width / 2, height / 2)
            else:
                x1, y1, x2, y2 = gt_box
                starting_position = (int((x1 + x2) * 0.5),
                                     int((y1 + y2) * 0.5))
                self.draw_2d_bounding_box(((x1, y1), (x2, y2)), "green")

        if len(dt_euler):
            end_positions = self.establish_axis_points(
                dt_euler, starting_position)
            color_infront, color_behind, axis_infront, axis_behind = self.establish_axis_order(
                dt_euler[2],
                end_positions,
                ("lightblue", "lightgreen", "tomato")
            )
            self.draw_axis(
                starting_position,
                (axis_behind, end_positions[2], axis_infront),
                (color_behind, "lightblue", color_infront)
            )

        if len(gt_euler):
            end_positions = self.establish_axis_points(
                gt_euler, starting_position)
            color_infront, color_behind, axis_infront, axis_behind = self.establish_axis_order(
                gt_euler[2],
                end_positions,
                ("blue", "green", "red")
            )
            self.draw_axis(
                starting_position,
                (axis_behind, end_positions[2], axis_infront),
                (color_behind, "blue", color_infront)
            )
        return image

    def draw_axis(
        self,
        start_position: tuple,
        end_positions: tuple,
        colors: tuple,
        width: int = 5
    ):
        """
        This draws the pose axis/compass on a 2D image.

        Parameters
        ----------
        start_position: tuple
            This is the (x,y) starting position of the three lines.
            Ensure the values are integers.
        end_position: tuple
            This is the ((x,y), (x,y), (x,y)) end positions of the lines.
            Ensure the first point is the axis drawn behind, the second
            point is the axis drawn in the middle, and the third point is
            the axis drawn on the front.
        colors: tuple
            This is color of each line ("blue", "green", "red")
            or any other combination for the three axis.
        width: int
            This is the width of the lines.
        """
        self.image_draw.line(
            (start_position, end_positions[0]),
            fill=colors[0],
            width=width)
        self.image_draw.line(
            (start_position, end_positions[1]),
            fill=colors[1],
            width=width)
        self.image_draw.line(
            (start_position, end_positions[2]),
            fill=colors[2],
            width=width)

    def draw_2d_bounding_box(
        self,
        box_position: tuple,
        color: str = "RoyalBlue",
        width: int = 3
    ):
        """
        Draws a 2D bounding box on the image.

        Parameters
        ----------
        box_position: tuple
            ((x1, y1), (x2, y2)) position of the box.
        color: str
            The color of the bounding box. Typically,
            ground truth/false negatives are set to "RoyalBlue",
            false positives are set to "OrangeRed",
            true positives are set to "LimeGreen".
        width: int
            The width of the line to draw the bounding boxes.
        """
        self.image_draw.rectangle(
            box_position,
            outline=color,
            width=width
        )

    @staticmethod
    def establish_axis_points(
        angles: list,
        starting_position: tuple,
        size: int = 150
    ) -> tuple:
        """
        Provides the (x,y) end positions of the lines forming
        the 3 axis for the pose.

        Parameters
        ----------
        angles: list
            This contains the [roll, pitch, yaw] angles in radians.
        starting_position: tuple
            This is the starting positions for
            which to start drawing the lines in (x,y).
        size: int
            This is the pixel length of the lines.

        Returns
        -------
        tuple
            The ((x,y), (x,y), (x,y)) end positions of the lines.
        """
        roll, pitch, yaw = angles
        tdx, tdy = starting_position
        # X-Axis (out of the screen) drawn in red.
        x1 = int(size * (np.sin(yaw)) + tdx)
        y1 = int(size * (-np.cos(yaw) * np.sin(pitch)) + tdy)
        # Y-Axis pointing to right. drawn in green.
        x2 = int(size * (np.cos(yaw) * np.cos(roll)) + tdx)
        y2 = int(size * (np.cos(pitch) * np.sin(roll) +
                 np.cos(roll) * np.sin(pitch) * np.sin(yaw)) + tdy)
        # Z-Axis | drawn in blue.
        x3 = int(size * (-np.cos(yaw) * np.sin(roll)) + tdx)
        y3 = int(size * (np.cos(pitch) * np.cos(roll) -
                 np.sin(pitch) * np.sin(yaw) * np.sin(roll)) + tdy)
        return ((x1, y1), (x2, y2), (x3, y3))

    @staticmethod
    def establish_axis_order(
        yaw: float,
        end_positions: tuple,
        colors: tuple
    ) -> Tuple[str, str, tuple, tuple]:
        """
        This establish the order of which the axis should be drawn and
        their colors per frame to avoid illusions of rotations going
        back and forth and maintain rotations moving in a single direction.

        Parameters
        ----------
        yaw: float
            The yaw angle in radians.
        end_positions: tuple
            This is the ((x,y), (x,y), (x,y)) end points of the axes.
        colors: tuple
            The three distinct colors of each axis.

        Returns
        -------
        Tuple[str, str, tuple, tuple]
            str
                This is the color of the axis that is drawn
                last or the front axis.
            str
                This is the color of the axis that is drawn first or the axis
                behind.
            tuple
                This is the end position of the axis (x,y) that is to be drawn
                last to appear in front.
            tuple
                This is the end position of the axis (x,y) that is to be drawn
                first to appear behind.
        """
        if yaw >= (-80 * np.pi / 180) and yaw <= (170 * np.pi / 180):
            axis_behind = end_positions[1]
            axis_infront = end_positions[0]
            color_behind = colors[1]
            color_infront = colors[2]
        else:
            axis_behind = end_positions[0]
            axis_infront = end_positions[1]
            color_behind = colors[2]
            color_infront = colors[1]
        return color_infront, color_behind, axis_infront, axis_behind
