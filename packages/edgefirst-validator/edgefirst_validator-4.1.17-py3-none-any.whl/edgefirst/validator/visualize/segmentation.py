import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from edgefirst.validator.datasets import SegmentationInstance


class Colors:
    """
    Ultralytics color palette for visualization and plotting.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/plotting.py#L19

    This class provides methods to work with the Ultralytics color palette,
    including converting hex color codes to RGB values and accessing predefined
    color schemes for object detection and pose estimation.

    Attributes
    ----------
    palette: List[tuple]
        List of RGB color tuples for general use.
    n: int
        The number of colors in the palette.
    pose_palette: np.ndarray
        A specific color palette array for pose estimation with dtype np.uint8.

    Examples
    --------
    >>> from ultralytics.utils.plotting import Colors
    >>> colors = Colors()
    >>> colors(5, True)  # Returns BGR format: (221, 111, 255)
    >>> colors(5, False)  # Returns RGB format: (255, 111, 221)
    """

    def __init__(self):
        """
        Initialize colors as hex = matplotlib.colors.TABLEAU_COLORS.values().
        """
        hexs = (
            "042AFF",
            "0BDBEB",
            "F3F3F3",
            "00DFB7",
            "111F68",
            "FF6FDD",
            "FF444F",
            "CCED00",
            "00F344",
            "BD00FF",
            "00B4FF",
            "DD00BA",
            "00FFFF",
            "26C000",
            "01FFB3",
            "7D24FF",
            "7B0068",
            "FF1B6C",
            "FC6D2F",
            "A2FF0B",
        )
        self.palette = [self.hex2rgb(f"#{c}") for c in hexs]
        self.n = len(self.palette)
        self.pose_palette = np.array(
            [
                [255, 128, 0],
                [255, 153, 51],
                [255, 178, 102],
                [230, 230, 0],
                [255, 153, 255],
                [153, 204, 255],
                [255, 102, 255],
                [255, 51, 255],
                [102, 178, 255],
                [51, 153, 255],
                [255, 153, 153],
                [255, 102, 102],
                [255, 51, 51],
                [153, 255, 153],
                [102, 255, 102],
                [51, 255, 51],
                [0, 255, 0],
                [0, 0, 255],
                [255, 0, 0],
                [255, 255, 255],
            ],
            dtype=np.uint8,
        )

    def __call__(self, i: int, bgr: bool = False) -> tuple:
        """
        Convert hex color codes to RGB values.

        Parameters
        ----------
        i : int
            Index of the color in the palette.
        bgr : bool, optional
            If True, return color in BGR format. Default is False.

        Returns
        -------
        tuple
            A 3-element tuple representing the RGB or BGR color.
        """
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h: str) -> tuple:
        """
        Convert hex color codes to RGB values (i.e. default PIL order).

        Parameters
        ----------
        h : str
            Hex color string (e.g. "#FF00AA").

        Returns
        -------
        tuple
            A 3-element tuple representing the RGB color.
        """
        return tuple(int(h[1 + i: 1 + i + 2], 16) for i in (0, 2, 4))


class SegmentationDrawer:
    """
    This class draws segmentation masks from the ground truth and
    model predictions on the image.
    """

    def __init__(self):
        self.font = ImageFont.load_default()
        self.colors = Colors()

    def mask2maskimage(
        self,
        gt_instance: SegmentationInstance,
        dt_instance: SegmentationInstance,
    ) -> Image.Image:
        """
        Masks the original image and returns the original image
        with mask prediction on the left and mask ground truth on the right.

        Parameters
        ----------
        gt_instance: SegmentationInstance
            This object contains the ground truth mask.
        dt_instance: SegmentationInstance
            This object contains the predictions mask.

        Returns
        -------
        Image.Image
            The image with drawn masks where on the right pane
            shows the ground truth mask and on the left pane shows
            the prediction mask.
        """

        gt_image = Image.fromarray(np.uint8(gt_instance.image))
        if dt_instance.image is not None:
            dt_image = Image.fromarray(np.uint8(dt_instance.image))
        else:
            dt_image = gt_image

        gt_mask = gt_instance.mask
        dt_mask = dt_instance.mask

        # Create image from numpy masks.
        mask_gt = self.mask2imagetransform(gt_mask)
        mask_dt = self.mask2imagetransform(dt_mask)

        image_gt = gt_image.convert("RGBA")
        image_dt = dt_image.convert("RGBA")
        mask_image_gt = Image.alpha_composite(image_gt, mask_gt).convert("RGB")
        mask_image_dt = Image.alpha_composite(image_dt, mask_dt).convert("RGB")

        dst = Image.new(
            'RGB',
            (mask_image_dt.width + mask_image_gt.width, mask_image_dt.height))
        dst.paste(mask_image_gt, (0, 0))
        dst.paste(mask_image_dt, (mask_image_dt.width, 0))

        draw_text = ImageDraw.Draw(dst)
        draw_text.text(
            (0, 0),
            "GROUND TRUTH",
            font=self.font,
            align='left',
            fill=(0, 0, 0)
        )
        draw_text.text(
            (mask_image_dt.width, 0),
            "MODEL PREDICTION",
            font=self.font,
            align='left',
            fill=(0, 0, 0)
        )
        return dst

    def duo_image_mask(
        self,
        nimage: np.ndarray,
        dt_polygons: list,
        gt_polygons: list
    ) -> Image.Image:
        """
        Masks the original image and returns the masked image
        with mask predictions on the left and ground truth
        masks on the right.

        Parameters
        ----------
        nimage: np.ndarray
            The original image as a numpy array.
        dt_polygons: list
            A list of predictions with polygon vertices
            [ [cls, x1, y1, x2, y2, x3, y3, ...] ...].
        gt_polygons: list
            A list of ground truth with polygon vertices
            [ [cls, x1, y1, x2, y2, x3, y3, ...] ...].

        Returns
        -------
        Image.Image
            The image with drawn mask where the left
            pane shows the ground truth mask and the right pane shows the
            prediction mask.
        """
        dt_mask = self.polygon2masktransform(nimage, dt_polygons)
        gt_mask = self.polygon2masktransform(nimage, gt_polygons)
        dst = Image.new('RGB', (dt_mask.width + gt_mask.width, dt_mask.height))
        dst.paste(dt_mask, (0, 0))
        dst.paste(gt_mask, (dt_mask.width, 0))
        return dst

    def mask2imagetransform(
        self,
        mask: np.ndarray,
        union: bool = False
    ) -> Image.Image:
        """
        Transform a NumPy array of mask into an RGBA image.

        Parameter
        ---------
        mask: np.ndarray
            Array (height, width) representing the mask.
        union: bool
            Specify to mask all objects with one color (True). Otherwise
            each label in the mask have distinct colors.

        Returns
        -------
        Image.Image
            The masked image.
        """
        # Transform dimension of masks from a 2D numpy array to 4D with RGBA
        # channels.
        mask_4_channels = np.stack((mask,) * 4, axis=-1)

        if union:
            # Assign all classes with color white.
            mask_4_channels[mask_4_channels == 1] = 255
            # Temporarily unpack the bands for readability.
            red, green, blue, _ = mask_4_channels.T
            # Areas of all classes.
            u_areas = (red == 255) & (blue == 255) & (green == 255)
            # Color all classes with blue.
            mask_4_channels[..., :][u_areas.T] = (0, 0, 255, 130)
        else:
            labels = np.sort(np.unique(mask))
            for label in labels:
                if label != 0:
                    # Designate a color for each class.
                    mask_4_channels[mask_4_channels == label] = \
                        self.colors(label)[0]

            # Temporarily unpack the bands for readability.
            red, green, blue, _ = mask_4_channels.T
            for label in labels:
                if label != 0:
                    # Find object areas ... (leaves alpha values alone...).
                    object_areas = (red == self.colors(label)[0]) &\
                        (blue == self.colors(label)[0]) & (
                            green == self.colors(label)[0])
                    # Transpose back needed.
                    mask_4_channels[..., :][object_areas.T] = \
                        np.append(self.colors(label), 130)

        # Convert array to image object for image processing.
        return Image.fromarray(mask_4_channels.astype(np.uint8))

    def maskimage(self, nimage: np.ndarray, instance: SegmentationInstance):
        """
        Masks the original image and returns the original image
        with mask prediction on the left and mask ground truth on the right.

        Parameters
        ----------
        nimage: np.ndarray
            This is the image to draw masks on as a numpy array.
        instance: SegmentationInstance
            An object container of the masks. This can either be a ground truth
            or a prediction instance. Only one of the either masks are being
            drawn.

        Returns
        -------
        Image.Image
            The image with drawn masks.
        """
        image = Image.fromarray(np.uint8(nimage))
        # Convert array to image object for image processing.
        mask = self.mask2imagetransform(instance.mask)
        # convert img to RGBA mode.
        image = image.convert("RGBA")
        mask_image = Image.alpha_composite(image, mask)
        mask_image = mask_image.convert("RGB")
        dst = Image.new('RGB', (mask_image.width, mask_image.height))
        dst.paste(mask_image, (0, 0))
        return dst

    @staticmethod
    def generate_distinct_colors(nc: int, seed: int = 42) -> np.ndarray:
        """
        Generate distinct colors for the masks in the dataset.

        Parameters
        ----------
        nc: int
            The number of distinct classes will be the number of
            distinct colors.
        seed: int
            Sets the random seed in NumPy to ensure the colors are
            being reproduced for each run.

        Returns
        -------
        np.ndarray
            The RGB colors as a NumPy array (nc, 3).
        """
        np.random.seed(seed)  # Ensure colors are reproduced.
        colors = plt.cm.get_cmap('tab20', nc)  # or 'hsv', 'tab20b', etc.
        colors = (colors(np.arange(nc))[:, :3] * 255).astype(np.uint8)
        return colors

    @staticmethod
    def polygon2masktransform(nimage: np.ndarray,
                              polygons: list) -> Image.Image:
        """
        Given a set of polygons, the provided image will be
        masked with these polygons.

        Parameters
        ----------
        nimage: np.ndarray
            This is the image as a NumPy array.
        polygons: list
            This is the list of polgons
            [ [cls, x1, y1, x2, y2, x3, y3, ...] ...].

        Returns
        -------
        Image.Image
            This is the image with segmentation masks.
        """
        image = Image.fromarray(np.uint8(nimage))
        image = image.convert("RGBA")
        mask = Image.new('RGBA', image.size, (255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)

        for polygon in polygons:
            mask_draw.polygon(polygon, fill=(0, 0, 255, 125))
            image_mask = Image.alpha_composite(image, mask)

        image_mask = image_mask.convert("RGB")
        return image_mask
