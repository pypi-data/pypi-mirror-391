# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

from projectaria_tools.core.sensor_data import ImageData, ImageDataRecord
from projectaria_tools.core.xprs import (
    createDecoder,
    VideoCodec,
    VideoCodecFormat,
    XprsResult,
)


class ImageDecoder:
    """
    Image decoder class that manages video codec decoders for multiple cameras.
    """

    def __init__(self, hw_accel=False):
        """
        Initialize the ImageDecoder.

        Args:
            hw_accel: Whether to enable hardware acceleration
        """
        if hw_accel:
            print(
                "Warning: Hardware acceleration is not supported in opensource XPRS decoder.",
            )
        self.hw_accel = False
        self.image_decoders = {}

    def decode_image(self, image_data: ImageData, image_record: ImageDataRecord):
        """
        Decode image data for a given camera.

        Args:
            image_data: The image data to decode
            image_record: The image data record containing camera_id

        Returns:
            bool: True if decoding was successful, False otherwise
        """
        camera_id = image_record.camera_id

        if camera_id not in self.image_decoders:
            codec = VideoCodec()
            codec.format = VideoCodecFormat.H265
            codec.hw_accel = self.hw_accel
            codec.implementation_name = "hevc"

            self.image_decoders[camera_id] = createDecoder(codec)
            xprsResult = self.image_decoders[camera_id].init(codec.hw_accel)
            if xprsResult != XprsResult.OK:
                print(
                    f"Failed to init decoder for camera: {camera_id} with error: {xprsResult}"
                )
        return self.image_decoders[camera_id].decode_oss_frame(image_data)
