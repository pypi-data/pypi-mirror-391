# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import aria.image_decoder as image_decoder
import aria.sdk_gen2 as sdk_gen2


class OssDataConverter:
    def __init__(self, enable_image_decoding=True, decoder_class=None):
        self.enable_image_decoding = enable_image_decoding
        self._enable_python_decoding = enable_image_decoding

        try:
            import aria.internal_only as internal_only

            if enable_image_decoding and internal_only.is_internal_only():
                self._enable_python_decoding = False
                print("[OssDataConverter] Using internal c++ image decoder.")
        except ImportError:
            self.enable_image_decoding = False
            print(
                f"[OssDataConverter] Using python image decoder: {self._enable_python_decoding}"
            )

        self.data_converter = sdk_gen2._flatbufferOssConverter(
            self.enable_image_decoding
        )

        hw_accel = False
        if decoder_class is not None:
            print("Warning: custom image decoder class is not supported yet")

        self.image_decoder = image_decoder.ImageDecoder(hw_accel=hw_accel)

    def set_calibration(self, calibration_json):
        """Set calibration from JSON string."""
        self.data_converter.set_calibration(calibration_json)

    def set_python_image_decoding(self, enable):
        """Enable python image decoding."""
        print("[OssDataConverter] Setting python image decoding to: ", enable)
        try:
            import aria.internal_only as internal_only

            if enable and internal_only.is_internal_only():
                self._enable_python_decoding = False
                print("[OssDataConverter] Using internal c++ image decoder instead.")
        except ImportError:
            self.enable_image_decoding = False
            self._enable_python_decoding = enable

    def get_python_image_decoding(self):
        """Get python image decoding status."""
        return self._enable_python_decoding

    def to_image_data_and_record(self, shared_message):
        [image_data, image_record] = self.data_converter.to_image_data_and_record(
            shared_message
        )

        if self._enable_python_decoding:
            decode_success = self.image_decoder.decode_image(image_data, image_record)
            if not decode_success:
                print(
                    f"Warning: Failed to decode image data from camera: {image_record.camera_id}"
                )
        return image_data, image_record

    def to_audio(self, shared_message):
        """Convert flatbuffer message to audio data and record.

        Returns:
            tuple: (audio_data, audio_record) or (None, None) if conversion fails
        """
        return self.data_converter.to_audio(shared_message)

    def to_barometer(self, shared_message):
        """Convert flatbuffer message to barometer data.

        Returns:
            BarometerData or None if conversion fails
        """
        return self.data_converter.to_barometer(shared_message)

    def to_imu(self, shared_message):
        """Convert flatbuffer message to IMU motion data.

        Returns:
            list of MotionData or None if conversion fails
        """
        return self.data_converter.to_imu(shared_message)

    def to_magnetometer(self, shared_message):
        """Convert flatbuffer message to magnetometer motion data.

        Returns:
            list of MotionData or None if conversion fails
        """
        return self.data_converter.to_magnetometer(shared_message)

    def to_eye_gaze(self, shared_message):
        """Convert flatbuffer message to eye gaze data.

        Args:
            shared_message: The flatbuffer message
            T_Cpf_Device: Transformation from CPF to device frame

        Returns:
            EyeGaze or None if conversion fails
        """
        return self.data_converter.to_eye_gaze(shared_message)

    def to_hand_pose(self, shared_message):
        """Convert flatbuffer message to hand pose data.

        Returns:
            HandTrackingResult or None if conversion fails
        """
        return self.data_converter.to_hand_pose(shared_message)

    def to_vio_result(self, shared_message):
        """Convert flatbuffer message to VIO result data.

        Returns:
            FrontendOutput or None if conversion fails
        """
        return self.data_converter.to_vio_result(shared_message)

    def to_vio_high_freq_pose(self, shared_message):
        """Convert flatbuffer message to high frequency VIO pose data.

        Returns:
            list of OpenLoopTrajectoryPose or None if conversion fails
        """
        return self.data_converter.to_vio_high_freq_pose(shared_message)

    def to_gnss(self, shared_message):
        """Convert flatbuffer message to GNSS/GPS data.

        Returns:
            GpsData or None if conversion fails
        """
        return self.data_converter.to_gnss(shared_message)

    def to_phone_location(self, shared_message):
        """Convert flatbuffer message to phone location data.

        Returns:
            GpsData or None if conversion fails
        """
        return self.data_converter.to_phone_location(shared_message)

    def to_ppg(self, shared_message):
        """Convert flatbuffer message to PPG (Photoplethysmogram) data.

        Returns:
            PpgData or None if conversion fails
        """
        return self.data_converter.to_ppg(shared_message)

    def to_bluetooth_beacon(self, shared_message):
        """Convert flatbuffer message to Bluetooth beacon data.

        Returns:
            list of BluetoothBeaconData or None if conversion fails
        """
        return self.data_converter.to_bluetooth_beacon(shared_message)

    def to_wifi_beacon(self, shared_message):
        """Convert flatbuffer message to WiFi beacon data.

        Returns:
            list of WifiBeaconData or None if conversion fails
        """
        return self.data_converter.to_wifi_beacon(shared_message)
