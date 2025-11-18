from typing import Optional

import numpy as np
from bladerf import _bladerf

from ria_toolkit_oss.datatypes import Recording
from ria_toolkit_oss.sdr import SDR


class Blade(SDR):

    def __init__(self, identifier=""):
        """
        Initialize a BladeRF device object and connect to the SDR hardware.

        :param identifier: Not used for BladeRF.

        BladeRF devices cannot currently be selected with and identifier value.
        If there are multiple connected devices, the device in use may be selected randomly.
        """

        if identifier != "":
            print(f"Warning, radio identifier {identifier} provided for Blade but will not be used.")

        uut = self._probe_bladerf()

        if uut is None:
            print("No bladeRFs detected. Exiting.")
            self._shutdown(error=-1, board=None)

        print(uut)

        self.device = _bladerf.BladeRF(uut)
        self._print_versions(device=self.device)

        super().__init__()

    def _shutdown(self, error=0, board=None):
        print("Shutting down with error code: " + str(error))
        if board is not None:
            board.close()

        # TODO why does this create an error under any conditions?
        raise OSError("Shutdown initiated with error code: {}".format(error))

    def _probe_bladerf(self):
        device = None
        print("Searching for bladeRF devices...")
        try:
            devinfos = _bladerf.get_device_list()
            if len(devinfos) == 1:
                device = "{backend}:device={usb_bus}:{usb_addr}".format(**devinfos[0]._asdict())
                print("Found bladeRF device: " + str(device))
            if len(devinfos) > 1:
                print("Unsupported feature: more than one bladeRFs detected.")
                print("\n".join([str(devinfo) for devinfo in devinfos]))
                self._shutdown(error=-1, board=None)
        except _bladerf.BladeRFError:
            print("No bladeRF devices found.")
            pass
        return device

    def _print_versions(self, device=None):
        print("libbladeRF version:\t" + str(_bladerf.version()))
        if device is not None:
            print("Firmware version:\t" + str(device.get_fw_version()))
            print("FPGA version:\t\t" + str(device.get_fpga_version()))
        return 0

    def close(self):
        self.device.close()

    def init_rx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        buffer_size: Optional[int] = 8192,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initializes the BladeRF for receiving.

        :param sample_rate: The sample rate for receiving.
        :type sample_rate: int or float
        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float
        :param gain: The gain set for receiving on the BladeRF
        :type gain: int
        :param channel: The channel the BladeRF is set to.
        :type channel: int
        :param buffer_size: The buffer size during receive. Defaults to 8192.
        :type buffer_size: int
        """
        print("Initializing RX")

        # Configure BladeRF
        self._set_rx_channel(channel)
        self._set_rx_sample_rate(sample_rate)
        self._set_rx_center_frequency(center_frequency)
        self._set_rx_gain(channel, gain, gain_mode)
        self._set_rx_buffer_size(buffer_size)

        bw = self.rx_sample_rate
        if bw < 200000:
            bw = 200000
        elif bw > 56000000:
            bw = 56000000
        self.rx_ch.bandwidth = bw

        self._rx_initialized = True
        self._tx_initialized = False

    def init_tx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        buffer_size: Optional[int] = 8192,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initializes the BladeRF for transmitting.

        :param sample_rate: The sample rate for transmitting.
        :type sample_rate: int or float
        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float
        :param gain: The gain set for transmitting on the BladeRF
        :type gain: int
        :param channel: The channel the BladeRF is set to.
        :type channel: int
        :param buffer_size: The buffer size during transmission. Defaults to 8192.
        :type buffer_size: int
        """

        # Configure BladeRF
        self._set_tx_channel(channel)
        self._set_tx_sample_rate(sample_rate)
        self._set_tx_center_frequency(center_frequency)
        self._set_tx_gain(channel=channel, gain=gain, gain_mode=gain_mode)
        self._set_tx_buffer_size(buffer_size)

        bw = self.tx_sample_rate
        if bw < 200000:
            bw = 200000
        elif bw > 56000000:
            bw = 56000000
        self.tx_ch.bandwidth = bw

        if self.device is None:
            print("TX: Invalid device handle.")
            return -1

        if self.tx_channel is None:
            print("TX: Invalid channel.")
            return -1

        self._tx_initialized = True
        self._rx_initialized = False
        return 0

    def _stream_rx(self, callback):
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        # Setup synchronous stream
        self.device.sync_config(
            layout=_bladerf.ChannelLayout.RX_X1,
            fmt=_bladerf.Format.SC16_Q11,
            num_buffers=16,
            buffer_size=self.rx_buffer_size,
            num_transfers=8,
            stream_timeout=3500000000,
        )

        self.rx_ch.enable = True
        self.bytes_per_sample = 4

        print("Blade Starting RX...")
        self._enable_rx = True

        while self._enable_rx:
            # Create receive buffer and read in samples to buffer
            # Add them to a list to convert and save after stream is finished
            buffer = bytearray(self.rx_buffer_size * self.bytes_per_sample)
            self.device.sync_rx(buffer, self.rx_buffer_size)
            signal = self._convert_rx_samples(buffer)
            # samples = convert_to_2xn(signal)
            self.buffer = buffer
            # send callback complex signal
            callback(buffer=signal, metadata=None)

        # Disable module
        print("Blade RX Completed.")
        self.rx_ch.enable = False

    def record(self, num_samples):
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        # Setup synchronous stream
        self.device.sync_config(
            layout=_bladerf.ChannelLayout.RX_X1,
            fmt=_bladerf.Format.SC16_Q11,
            num_buffers=16,
            buffer_size=self.rx_buffer_size,
            num_transfers=8,
            stream_timeout=3500000000,
        )

        self.rx_ch.enable = True
        self.bytes_per_sample = 4

        print("Blade Starting RX...")
        self._enable_rx = True

        store_array = np.zeros((1, (num_samples // self.rx_buffer_size + 1) * self.rx_buffer_size), dtype=np.complex64)

        for i in range(num_samples // self.rx_buffer_size + 1):
            # Create receive buffer and read in samples to buffer
            # Add them to a list to convert and save after stream is finished
            buffer = bytearray(self.rx_buffer_size * self.bytes_per_sample)
            self.device.sync_rx(buffer, self.rx_buffer_size)
            signal = self._convert_rx_samples(buffer)
            # samples = convert_to_2xn(signal)
            store_array[:, i * self.rx_buffer_size : (i + 1) * self.rx_buffer_size] = signal

        # Disable module
        print("Blade RX Completed.")
        self.rx_ch.enable = False
        metadata = {
            "source": self.__class__.__name__,
            "sample_rate": self.rx_sample_rate,
            "center_frequency": self.rx_center_frequency,
            "gain": self.rx_gain,
        }

        return Recording(data=store_array[:, :num_samples], metadata=metadata)

    def _stream_tx(self, callback):

        # Setup stream
        self.device.sync_config(
            layout=_bladerf.ChannelLayout.TX_X1,
            fmt=_bladerf.Format.SC16_Q11,
            num_buffers=16,
            buffer_size=8192,
            num_transfers=8,
            stream_timeout=3500,
        )

        # Enable module
        self.tx_ch.enable = True
        self._enable_tx = True

        print("Blade Starting TX...")

        while self._enable_tx:
            buffer = callback(self.tx_buffer_size)  # [0]
            byte_array = self._convert_tx_samples(buffer)
            self.device.sync_tx(byte_array, len(buffer))

        # Disable module
        print("Blade TX Completed.")
        self.tx_ch.enable = False

    def _convert_rx_samples(self, samples):
        samples = np.frombuffer(samples, dtype=np.int16).astype(np.float32)
        samples /= 2048
        samples = samples[::2] + 1j * samples[1::2]
        return samples

    def _convert_tx_samples(self, samples):
        tx_samples = np.empty(samples.size * 2, dtype=np.float32)
        tx_samples[::2] = np.real(samples)  # Real part
        tx_samples[1::2] = np.imag(samples)  # Imaginary part

        tx_samples *= 2048
        tx_samples = tx_samples.astype(np.int16)
        byte_array = tx_samples.tobytes()

        return byte_array

    def _set_rx_channel(self, channel):
        self.rx_channel = channel
        self.rx_ch = self.device.Channel(_bladerf.CHANNEL_RX(channel))
        print(f"\nBlade channel = {self.rx_ch}")

    def _set_rx_sample_rate(self, sample_rate):
        self.rx_sample_rate = sample_rate
        self.rx_ch.sample_rate = self.rx_sample_rate
        print(f"Blade sample rate = {self.rx_ch.sample_rate}")

    def _set_rx_center_frequency(self, center_frequency):
        self.rx_center_frequency = center_frequency
        self.rx_ch.frequency = center_frequency
        print(f"Blade center frequency = {self.rx_ch.frequency}")

    def _set_rx_gain(self, channel, gain, gain_mode):

        rx_gain_min = self.device.get_gain_range(channel)[0]
        rx_gain_max = self.device.get_gain_range(channel)[1]

        if gain_mode == "relative":
            if gain > 0:
                raise ValueError(
                    "When gain_mode = 'relative', gain must be < 0. This sets \
                        the gain relative to the maximum possible gain."
                )
            else:
                abs_gain = rx_gain_max + gain
        else:
            abs_gain = gain

        if abs_gain < rx_gain_min or abs_gain > rx_gain_max:
            abs_gain = min(max(gain, rx_gain_min), rx_gain_max)
            print(f"Gain {abs_gain} out of range for Blade.")
            print(f"Gain range: {rx_gain_min} to {rx_gain_max} dB")

        self.rx_gain = abs_gain
        self.rx_ch.gain = abs_gain

        print(f"Blade gain = {self.rx_ch.gain}")

    def _set_rx_buffer_size(self, buffer_size):
        self.rx_buffer_size = buffer_size

    def _set_tx_channel(self, channel):
        self.tx_channel = channel
        self.tx_ch = self.device.Channel(_bladerf.CHANNEL_TX(self.tx_channel))
        print(f"\nBlade channel = {self.tx_ch}")

    def _set_tx_sample_rate(self, sample_rate):
        self.tx_sample_rate = sample_rate
        self.tx_ch.sample_rate = self.tx_sample_rate
        print(f"Blade sample rate = {self.tx_ch.sample_rate}")

    def _set_tx_center_frequency(self, center_frequency):
        self.tx_center_frequency = center_frequency
        self.tx_ch.frequency = center_frequency
        print(f"Blade center frequency = {self.tx_ch.frequency}")

    def _set_tx_gain(self, channel, gain, gain_mode):

        tx_gain_min = self.device.get_gain_range(channel)[0]
        tx_gain_max = self.device.get_gain_range(channel)[1]

        if gain_mode == "relative":
            if gain > 0:
                raise ValueError(
                    "When gain_mode = 'relative', gain must be < 0. This sets\
                          the gain relative to the maximum possible gain."
                )
            else:
                abs_gain = tx_gain_max + gain
        else:
            abs_gain = gain

        if abs_gain < tx_gain_min or abs_gain > tx_gain_max:
            abs_gain = min(max(gain, tx_gain_min), tx_gain_max)
            print(f"Gain {abs_gain} out of range for Blade.")
            print(f"Gain range: {tx_gain_min} to {tx_gain_max} dB")

        self.tx_gain = abs_gain
        self.tx_ch.gain = abs_gain

        print(f"Blade gain = {self.tx_ch.gain}")

    def _set_tx_buffer_size(self, buffer_size):
        self.tx_buffer_size = buffer_size

    def set_clock_source(self, source):
        if source.lower() == "external":
            self.device.set_pll_enable(True)
        elif source.lower() == "internal":
            print("Disabling PLL")
            self.device.set_pll_enable(False)

        print(f"Clock source set to {self.device.get_clock_select()}")
        print(f"PLL Reference set to {self.device.get_pll_refclk()}")
