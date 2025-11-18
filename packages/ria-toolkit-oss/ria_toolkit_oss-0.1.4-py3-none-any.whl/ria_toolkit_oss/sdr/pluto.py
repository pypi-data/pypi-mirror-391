import threading
import time
import traceback
import warnings
from typing import Optional

import adi
import numpy as np

from ria_toolkit_oss.datatypes.recording import Recording
from ria_toolkit_oss.sdr.sdr import SDR


class Pluto(SDR):

    def __init__(self, identifier=None):
        """
        Initialize a Pluto SDR device object and connect to the SDR hardware.

        This software supports the ADALAM Pluto SDR created by Analog Devices.

        :param identifier: The value of the parameter that identifies the device.
        :type identifier: str = "192.168.3.1", "pluto.local", etc

        If no identifier is provided, it will select the first device found, with a warning.
        If more than one device is found with the identifier, it will select the first of those devices.
        """
        print(f"Initializing Pluto radio with identifier [{identifier}].")
        try:
            super().__init__()

            if identifier is None:
                uri = "ip:pluto.local"
            else:
                uri = f"ip:{identifier}"

            self.radio = adi.ad9361(uri)
            print(f"Successfully found Pluto radio with identifier [{identifier}].")
        except Exception as e:
            print(f"Failed to find Pluto radio with identifier [{identifier}].")
            raise e

    def init_rx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initializes the Pluto for receiving.

        :param sample_rate: The sample rate for receiving.
        :type sample_rate: int or float
        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float
        :param gain: The gain set for receiving on the Pluto
        :type gain: int
        :param channel: The channel the Pluto is set to. Must be 0 or 1. 0 enables channel 1, 1 enables both channels.
        :type channel: int
        :param buffer_size: The buffer size during receive. Defaults to 10000.
        :type buffer_size: int
        """
        print("Initializing RX")

        self.set_rx_sample_rate(sample_rate=int(sample_rate))
        print(f"Pluto sample rate = {self.radio.sample_rate}")

        self.set_rx_center_frequency(center_frequency=int(center_frequency))
        print(f"Pluto center frequency = {self.radio.rx_lo}")

        if channel == 0:
            self.radio.rx_enabled_channels = [0]
            print(f"Pluto channel(s) = {self.radio.rx_enabled_channels}")
        elif channel == 1:
            self.radio.rx_enabled_channels = [0, 1]
            print(f"Pluto channel(s) = {self.radio.rx_enabled_channels}")
        else:
            raise ValueError("Channel must be either 0 or 1.")

        rx_gain_min = 0
        rx_gain_max = 74

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
            print(f"Gain {gain} out of range for Pluto.")
            print(f"Gain range: {rx_gain_min} to {rx_gain_max} dB")

        self.set_rx_gain(gain=abs_gain, channel=channel)
        if channel == 0:
            print(f"Pluto gain = {self.radio.rx_hardwaregain_chan0}")
        elif channel == 1:
            self.set_rx_gain(gain=abs_gain, channel=0)
            print(f"Pluto gain = {self.radio.rx_hardwaregain_chan0}, {self.radio.rx_hardwaregain_chan1}")

        self.radio.rx_buffer_size = 1024  # TODO deal with this for zmq
        self._rx_initialized = True
        self._tx_initialized = False

    def init_tx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initializes the Pluto for transmitting. Will transmit garbage during
        center frequency tuning and setting the sample rate.

        :param sample_rate: The sample rate for transmitting.
        :type sample_rate: int or float
        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float
        :param gain: The gain set for transmitting on the Pluto
        :type gain: int
        :param channel: The channel the Pluto is set to. Must be 0 or 1. 0 enables channel 1, 1 enables both channels.
        :type channel: int
        :param buffer_size: The buffer size during transmit. Defaults to 10000.
        :type buffer_size: int
        """

        print("Initializing TX")

        self.set_tx_sample_rate(sample_rate=int(sample_rate))
        print(f"Pluto sample rate = {self.radio.sample_rate}")

        self.set_tx_center_frequency(center_frequency=int(center_frequency))
        print(f"Pluto center frequency = {self.radio.tx_lo}")

        if channel == 1:
            self.radio.tx_enabled_channels = [0, 1]
            print(f"Pluto channel(s) = {self.radio.tx_enabled_channels}")
        elif channel == 0:
            self.radio.tx_enabled_channels = [0]
            print(f"Pluto channel(s) = {self.radio.tx_enabled_channels}")
        else:
            raise ValueError("Channel must be either 0 or 1.")

        tx_gain_min = -89
        tx_gain_max = 0

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
            print(f"Gain {gain} out of range for Pluto.")
            print(f"Gain range: {tx_gain_min} to {tx_gain_max} dB")

        self.set_tx_gain(gain=abs_gain, channel=channel)
        if channel == 0:
            print(f"Pluto gain = {self.radio.tx_hardwaregain_chan0}")
        elif channel == 1:
            self.set_tx_gain(gain=abs_gain, channel=0)
            print(f"Pluto gain = {self.radio.tx_hardwaregain_chan0}, {self.radio.tx_hardwaregain_chan1}")

        self._tx_initialized = True
        self._rx_initialized = False

    def _stream_rx(self, callback):
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        # print("Starting rx...")

        self._enable_rx = True
        while self._enable_rx is True:
            signal = self.radio.rx()
            signal = self._convert_rx_samples(signal)
            # send callback complex signal
            callback(buffer=signal, metadata=None)

    def record(self, num_samples: Optional[int] = None, rx_time: Optional[int | float] = None):
        """
        Create a radio recording (iq samples and metadata) of a given length from the SDR.
        Either num_samples or rx_time must be provided.
        init_rx() must be called before record()

        :param num_samples: The number of samples to record. Pluto max = 16M.
        :type num_samples: int, optional
        :param rx_time: The time to record.
        :type rx_time: int or float, optional

        returns: Recording object (iq samples and metadata)
        """
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        if num_samples is not None and rx_time is not None:
            raise ValueError("Only input one of num_samples or rx_time")
        elif num_samples is not None:
            self._num_samples_to_record = num_samples
        elif rx_time is not None:
            self._num_samples_to_record = int(rx_time * self.rx_sample_rate)
        else:
            raise ValueError("Must provide input of one of num_samples or rx_time")

        if self._num_samples_to_record > 16000000:
            raise NotImplementedError("Pluto record for num_samples>16M not implemented yet.")
        self.radio.rx_buffer_size = self._num_samples_to_record

        print("Pluto Starting RX...")
        samples = self.radio.rx()
        if self.radio.rx_enabled_channels == [0]:
            samples = self._convert_rx_samples(samples)
            samples = [samples]
        else:
            channel1 = self._convert_rx_samples(samples[0])
            channel2 = self._convert_rx_samples(samples[1])
            samples = [channel1, channel2]
        print("Pluto RX Completed.")

        metadata = {
            "source": self.__class__.__name__,
            "sample_rate": self.rx_sample_rate,
            "center_frequency": self.rx_center_frequency,
            "gain": self.rx_gain,
        }

        recording = Recording(data=samples, metadata=metadata)
        return recording

    def _format_tx_data(self, recording: Recording | np.ndarray | list):
        if isinstance(recording, np.ndarray):
            data = self._convert_tx_samples(samples=recording)
        elif isinstance(recording, Recording):
            if self.radio.tx_enabled_channels == [0]:
                samples = recording.data[0]
                data = self._convert_tx_samples(samples=samples)

                if len(recording.data) > 1:
                    warnings.warn("Recording object is multichannel, only channel 0 data was used for transmission")

            else:
                if len(recording.data) == 1:
                    warnings.warn(
                        "Recording has only 1 channel, the same data will be transmitted over both Pluto channels"
                    )
                    samples = recording.data[0]
                    data = [self._convert_tx_samples(samples), self._convert_tx_samples(samples)]
                else:
                    if len(recording) > 2:
                        warnings.warn(
                            "More recordings were provided than channels in the Pluto. \
                            Only the first two recordings will be used"
                        )
                    sample0 = self._convert_tx_samples(recording.data[0])
                    sample1 = self._convert_tx_samples(recording.data[1])
                    data = [sample0, sample1]

        elif isinstance(recording, list):
            if len(recording) > 2:
                warnings.warn(
                    "More recordings were provided than channels in the Pluto. \
                    Only the first two recordings will be used"
                )

            if isinstance(recording[0], np.ndarray):
                data = [self._convert_tx_samples(recording[0]), self._convert_tx_samples(recording[1])]
            elif isinstance(recording[0], Recording):
                sample0 = self._convert_tx_samples(recording[0].data[0])
                sample1 = self._convert_tx_samples(recording[1].data[0])
                data = [sample0, sample1]

        return data

    def _timeout_cyclic_buffer(self, timeout):
        time.sleep(timeout)
        self.radio.tx_destroy_buffer()
        self.radio.tx_cyclic_buffer = False
        print("Pluto TX Completed.")

    def interrupt_transmit(self):
        self.radio.tx_destroy_buffer()
        self.radio.tx_cyclic_buffer = False
        print("Pluto TX Completed.")

    def close(self):
        if self.radio.tx_cyclic_buffer:
            self.radio.tx_destroy_buffer()
        del self.radio

    def tx_recording(self, recording: Recording | np.ndarray | list, num_samples=None, tx_time=None, mode="timed"):
        """
        Transmit the given iq samples from the provided recording.
        init_tx() must be called before this function.

        :param recording: The recording(s) to transmit.
        :type recording: Recording, np.ndarray, list[Recording, np.ndarray]
        :param num_samples: The number of samples to transmit, will repeat or
            truncate the recording to this length. Defaults to None.
        :type num_samples: int, optional
        :param tx_time: The time to transmit, will repeat or truncate the
            recording to this length. Defaults to None.
        :type tx_time: int or float, optional
        :param mode: The mode of transmission, either timed or continuous. Defaults to timed.
        :type mode: str, optional
        """
        if num_samples is not None and tx_time is not None:
            raise ValueError("Only input one of num_samples or tx_time")
        elif num_samples is not None:
            tx_time = num_samples / self.tx_sample_rate
        elif tx_time is not None:
            pass
        else:
            tx_time = len(recording) / self.tx_sample_rate

        data = self._format_tx_data(recording=recording)

        try:
            if self.radio.tx_cyclic_buffer:
                print("Destroying existing TX buffer...")
                self.radio.tx_destroy_buffer()
                self.radio.tx_cyclic_buffer = False
        except Exception as e:
            print(f"Error while destroying TX buffer: {e}")

        self.radio.tx_cyclic_buffer = True
        print("Pluto Starting TX...")
        self.radio.tx(data_np=data)
        if mode == "timed":
            timeout_thread = threading.Thread(target=self._timeout_cyclic_buffer, args=([tx_time]))
            timeout_thread.start()
            timeout_thread.join()

    def _stream_tx(self, callback):
        if self._tx_initialized is False:
            raise RuntimeError("TX was not initialized, init_tx must be called before _stream_tx")

        num_samples = 10000
        # TODO remove hardcode

        self._enable_tx = True
        while self._enable_tx is True:
            buffer = self._convert_tx_samples(callback(num_samples))
            self.radio.tx(buffer[0])

    def set_rx_center_frequency(self, center_frequency):
        try:
            self.radio.rx_lo = int(center_frequency)
            self.rx_center_frequency = center_frequency
        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_rx_sample_rate(self, sample_rate):
        self.rx_sample_rate = sample_rate

        # TODO add logic for limiting sample rate

        try:
            self.radio.sample_rate = int(sample_rate)

            # set the front end filter width
            self.radio.rx_rf_bandwidth = int(sample_rate)
        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_rx_gain(self, gain, channel=0):
        self.rx_gain = gain
        try:
            if channel == 0:

                if gain is None:
                    self.radio.gain_control_mode_chan0 = "automatic"
                    print("Using Pluto Automatic Gain Control.")

                else:
                    self.radio.gain_control_mode_chan0 = "manual"
                    self.radio.rx_hardwaregain_chan0 = gain  # dB

            elif channel == 1:
                try:
                    if gain is None:
                        self.radio.gain_control_mode_chan1 = "automatic"
                        print("Using Pluto Automatic Gain Control.")

                    else:
                        self.radio.gain_control_mode_chan1 = "manual"
                        self.radio.rx_hardwaregain_chan1 = gain  # dB

                except Exception as e:
                    print("Failed to use channel 1 on the PlutoSDR. \nThis is only available for revC versions.")
                    raise e

            else:
                raise ValueError(f"Pluto channel must be 0 or 1 but was {channel}.")

        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_rx_channel(self, channel):
        self.rx_channel = channel

    def set_rx_buffer_size(self, buffer_size):
        raise NotImplementedError

    def set_tx_center_frequency(self, center_frequency):
        try:
            self.radio.tx_lo = int(center_frequency)
            self.tx_center_frequency = center_frequency

        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_tx_sample_rate(self, sample_rate):
        try:
            self.radio.sample_rate = sample_rate
            self.tx_sample_rate = sample_rate

        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_tx_gain(self, gain, channel=0):
        try:
            self.tx_gain = gain

            if channel == 0:
                self.radio.tx_hardwaregain_chan0 = int(gain)
            elif channel == 1:
                self.radio.tx_hardwaregain_chan1 = int(gain)
            else:
                raise ValueError(f"Pluto channel must be 0 or 1 but was {channel}.")

        except OSError as e:
            _handle_OSError(e)
        except ValueError as e:
            _handle_OSError(e)

    def set_tx_channel(self, channel):
        raise NotImplementedError

    def set_tx_buffer_size(self, buffer_size):
        raise NotImplementedError

    def shutdown(self):
        del self.radio

    def _convert_rx_samples(self, samples):
        return samples / (2**11)

    def _convert_tx_samples(self, samples):
        return samples.astype(np.complex64) * (2**14)

    def set_clock_source(self, source):
        raise NotImplementedError


def _handle_OSError(e):

    # process a common difficult to read error message into a more intuitive format

    print("PlutoSDR valid arguments:")

    print("Standard: ")
    print("\tCenter frequency: 325-3800Mhz")
    print("\tSample rate: 521kHz-20Mhz")
    print("\tGain: -90-0")
    print("Hacked:")
    print("\tCenter frequency: 70-6000Mhz")
    print("\tSample rate: 521kHz-56Mhz")
    print("\tGain: -90-0")

    stack_trace = traceback.format_exc()
    print(stack_trace)
    if "sampling_frequency" in stack_trace or "sample rates" in stack_trace:
        raise ValueError("The sample rate was out of range for the Pluto SDR.\n")
    if "tx_lo" in stack_trace or "rx_lo" in stack_trace:
        raise ValueError("The center frequency was out of range for the Pluto SDR.\n")
    if "hardwaregain" in stack_trace:
        raise ValueError("The gain was out of range for the Pluto SDR.\n")
