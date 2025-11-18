import time
import warnings
from typing import Optional

import numpy as np

from ria_toolkit_oss.datatypes.recording import Recording
from ria_toolkit_oss.sdr._external.libhackrf import HackRF as hrf
from ria_toolkit_oss.sdr.sdr import SDR


class HackRF(SDR):
    def __init__(self, identifier=""):
        """
        Initialize a HackRF device object and connect to the SDR hardware.

        :param identifier: Not used for HackRF.

        HackRF devices cannot currently be selected with and identifier value.
        If there are multiple connected devices, the device in use may be selected randomly.
        """

        if identifier != "":
            print(f"Warning, radio identifier {identifier} provided for HackRF but will not be used.")

        print("Initializing HackRF radio.")
        try:
            super().__init__()

            self.radio = hrf()
            print("Successfully found HackRF radio.")
        except Exception as e:
            print("Failed to find HackRF radio.")
            raise e

        super().__init__()

    def init_rx(self, sample_rate, center_frequency, gain, channel, gain_mode):
        self._tx_initialized = False
        self._rx_initialized = True
        return NotImplementedError("RX not yet implemented for HackRF")

    def init_tx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initializes the HackRF for transmitting.

        :param sample_rate: The sample rate for transmitting.
        :type sample_rate: int or float
        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float
        :param gain: The gain set for transmitting on the HackRF
        :type gain: int
        :param channel: The channel the HackRF is set to. (Not actually used)
        :type channel: int
        :param buffer_size: The buffer size during transmit. Defaults to 10000.
        :type buffer_size: int
        """

        print("Initializing TX")
        self.tx_sample_rate = sample_rate
        self.radio.sample_rate = int(sample_rate)
        print(f"HackRF sample rate = {self.radio.sample_rate}")

        self.tx_center_frequency = center_frequency
        self.radio.center_freq = int(center_frequency)
        print(f"HackRF center frequency = {self.radio.center_freq}")

        self.radio.enable_amp()

        tx_gain_min = 0
        tx_gain_max = 47
        if gain_mode == "relative":
            if gain > 0:
                raise ValueError(
                    "When gain_mode = 'relative', gain must be < 0. This \
                        sets the gain relative to the maximum possible gain."
                )
            else:
                abs_gain = tx_gain_max + gain
        else:
            abs_gain = gain

        if abs_gain < tx_gain_min or abs_gain > tx_gain_max:
            abs_gain = min(max(gain, tx_gain_min), tx_gain_max)
            print(f"Gain {gain} out of range for Pluto.")
            print(f"Gain range: {tx_gain_min} to {tx_gain_max} dB")

        self.radio.txvga_gain = abs_gain
        print(f"HackRF gain = {self.radio.txvga_gain}")

        self._tx_initialized = True
        self._rx_initialized = False

    def tx_recording(
        self,
        recording: Recording | np.ndarray,
        num_samples: Optional[int] = None,
        tx_time: Optional[int | float] = None,
    ):
        """
        Transmit the given iq samples from the provided recording.
        init_tx() must be called before this function.

        :param recording: The recording to transmit.
        :type recording: Recording or np.ndarray
        :param num_samples: The number of samples to transmit, will repeat or
            truncate the recording to this length. Defaults to None.
        :type num_samples: int, optional
        :param tx_time: The time to transmit, will repeat or truncate the
            recording to this length. Defaults to None.
        :type tx_time: int or float, optional
        """
        if num_samples is not None and tx_time is not None:
            raise ValueError("Only input one of num_samples or tx_time")
        elif num_samples is not None:
            tx_time = num_samples / self.tx_sample_rate
        elif tx_time is not None:
            pass
        else:
            tx_time = len(recording) / self.tx_sample_rate

        if isinstance(recording, np.ndarray):
            samples = recording
        elif isinstance(recording, Recording):
            if len(recording.data) > 1:
                warnings.warn("Recording object is multichannel, only channel 0 data was used for transmission")

            samples = recording.data[0]

        samples = samples.astype(np.complex64, copy=False)
        if np.max(np.abs(samples)) >= 1:
            samples = samples / (np.max(np.abs(samples)) + 1e-12)

        print("HackRF Starting TX...")
        self.radio.start_tx(samples=samples, repeat=True)
        time.sleep(tx_time)
        self.radio.stop_tx()
        print("HackRF Tx Completed.")

    def set_clock_source(self, source):

        self.radio.set_clock_source(source)

    def close(self):
        self.radio.close()

    def _stream_rx(self, callback):
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")
        return NotImplementedError("RX not yet implemented for HackRF")

    def _stream_tx(self, callback):
        return super()._stream_tx(callback)
