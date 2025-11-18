import subprocess
import time
import warnings
from typing import Optional

import numpy as np
import uhd

from ria_toolkit_oss.datatypes.recording import Recording
from ria_toolkit_oss.sdr.sdr import SDR


class USRP(SDR):
    def __init__(self, identifier: str = None):
        """
        Initialize a USRP device object and connect to the SDR hardware.

        This software supports all USRP SDRs created by Ettus Research.

        :param identifier: Identifier of the device. Can be an IP address (e.g. "192.168.0.0"),
            a device name (e.g. "MyB210"), or any name/address found via ``uhd_find_devices``.
            If not provided, the first available device is selected with a warning.
            If multiple devices match the identifier, the first one is selected.
        :type identifier: str, optional
        """
        super().__init__()

        self.default_buffer_size = 8000

        # get all the info from only one of the parameters
        self.device_dict = _create_device_dict(identifier)

        self._rx_initialized = False
        self._tx_initialized = False

    def init_rx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        channel: int,
        gain: int,
        gain_mode: Optional[str] = "absolute",
        rx_buffer_size: int = 960000,
    ):
        """
        Initialize the USRP for receiving.

        :param sample_rate: The sample rate for receiving.
        :type sample_rate: int or float

        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float

        :param channel: The channel the USRP is set to.
        :type channel: int

        :param gain: The gain set for receiving on the USRP.
        :type gain: int

        :param gain_mode: Gain mode setting. ``"absolute"`` passes gain directly to the SDR.
            ``"relative"`` means gain should be a negative value, which will be subtracted
            from the maximum gain.
        :type gain_mode: str

        :param rx_buffer_size: Internal buffer size for receiving samples. Defaults to 960000.
        :type rx_buffer_size: int

        :return: Dictionary with the actual RX parameters after configuration.
        :rtype: dict
        """

        self.rx_buffer_size = rx_buffer_size

        # build USRP object
        usrp_args = _generate_usrp_config_string(sample_rate=sample_rate, device_dict=self.device_dict)
        self.usrp = uhd.usrp.MultiUSRP(usrp_args)

        # check if  channel arg is valid
        max_num_channels = self.usrp.get_rx_num_channels()
        if channel + 1 > max_num_channels:
            raise IOError(f"Channel {channel} not valid for device with {max_num_channels} channels.")

        # check if gain arg is valid
        gain_range = self.usrp.get_rx_gain_range()
        if gain_mode == "relative":
            if gain > 0:
                raise ValueError(
                    "When gain_mode = 'relative', gain must be < 0. This sets\
                          the gain relative to the maximum possible gain."
                )
            else:
                # set gain relative to max
                abs_gain = gain_range.stop() + gain
        else:
            abs_gain = gain
        if abs_gain < gain_range.start() or abs_gain > gain_range.stop():
            print(f"Gain {abs_gain} out of range for this USRP.")
            print(f"Gain range: {gain_range.start()} to {gain_range.stop()} dB")
            abs_gain = min(max(abs_gain, gain_range.start()), gain_range.stop())
        self.usrp.set_rx_gain(abs_gain, channel)

        # check if sample rate arg is valid
        sample_rate_range = self.usrp.get_rx_rates()
        if sample_rate < sample_rate_range.start() or sample_rate > sample_rate_range.stop():
            raise IOError(
                f"Sample rate {sample_rate} not valid for this USRP.\nValid\
                      range is {sample_rate_range.start()}\
                          to {sample_rate_range.stop()}."
            )
        self.usrp.set_rx_rate(sample_rate, channel)

        center_frequency_range = self.usrp.get_rx_freq_range()
        if center_frequency < center_frequency_range.start() or center_frequency > center_frequency_range.stop():
            raise IOError(
                f"Center frequency {center_frequency} out of range for USRP.\
                    \nValid range is {center_frequency_range.start()} \
                    to {center_frequency_range.stop()}."
            )
        self.usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(center_frequency), channel)

        # set internal variables for metadata
        self.rx_sample_rate = self.usrp.get_rx_rate(channel)
        self.rx_gain = self.usrp.get_rx_gain(channel)
        self.rx_center_frequency = self.usrp.get_rx_freq(channel)
        self.rx_channel = channel

        print(f"USRP RX Sample Rate = {self.rx_sample_rate}")
        print(f"USRP RX Center Frequency = {self.rx_center_frequency}")
        print(f"USRP RX Channel = {self.rx_channel}")
        print(f"USRP RX Gain = {self.rx_gain}")

        # flag to prevent user from calling certain functions before this one.
        self._rx_initialized = True
        self._tx_initialized = False

        return {"sample_rate": self.rx_sample_rate, "center_frequency": self.rx_center_frequency, "gain": self.rx_gain}

    def get_rx_sample_rate(self):
        """
        Retrieve the current sample rate of the receiver.

        Returns:
            float: The receiver's sample rate in samples per second (Hz).
        """
        return self.rx_sample_rate

    def get_rx_center_frequency(self):
        """
        Retrieve the current center frequency of the receiver.

        Returns:
            float: The receiver's center frequency in Hertz (Hz).
        """
        return self.rx_center_frequency

    def get_rx_gain(self):
        """
        Retrieve the current gain setting of the receiver.

        Returns:
            float: The receiver's gain in decibels (dB).
        """
        return self.rx_gain

    def _stream_rx(self, callback):

        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
        stream_args.channels = [self.rx_channel]

        self.metadata = uhd.types.RXMetadata()
        self.rx_stream = self.usrp.get_rx_stream(stream_args)

        stream_command = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
        stream_command.stream_now = True
        self.rx_stream.issue_stream_cmd(stream_command)

        # receive loop
        self._enable_rx = True
        print("USRP Starting RX...")
        receive_buffer = np.zeros((1, self.rx_buffer_size), dtype=np.complex64)

        while self._enable_rx:

            # 1 is the timeout #TODO maybe set this intelligently based on the desired sample rate
            self.rx_stream.recv(receive_buffer, self.metadata, 1)

            # TODO set metadata correctly, sending real sample rate plus any error codes
            # sending complex signal
            callback(buffer=receive_buffer, metadata=self.metadata)

            if self.metadata.error_code != uhd.types.RXMetadataErrorCode.none:
                print(f"Error while receiving samples: {self.metadata.strerror()}")
                if self.metadata.error_code == uhd.types.RXMetadataErrorCode.timeout:
                    print("Stopping receive due to timeout error.")
                    self.stop()
        wait_time = 0.1
        stop_time = self.usrp.get_time_now() + wait_time
        stop_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
        stop_cmd.stream_now = False
        stop_cmd.time_spec = stop_time
        self.rx_stream.issue_stream_cmd(stop_cmd)
        time.sleep(wait_time)  # TODO figure out what a realistic wait time is here.
        del self.rx_stream
        print("USRP RX Completed.")

    def record(self, num_samples):
        if not self._rx_initialized:
            raise RuntimeError("RX was not initialized. init_rx() must be called before _stream_rx() or record()")

        stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
        stream_args.channels = [self.rx_channel]

        self.metadata = uhd.types.RXMetadata()
        self.rx_stream = self.usrp.get_rx_stream(stream_args)

        stream_command = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
        stream_command.stream_now = True
        self.rx_stream.issue_stream_cmd(stream_command)

        # receive loop
        self._enable_rx = True
        print("USRP Starting RX...")
        store_array = np.zeros((1, (num_samples // self.rx_buffer_size + 1) * self.rx_buffer_size), dtype=np.complex64)
        receive_buffer = np.zeros((1, self.rx_buffer_size), dtype=np.complex64)
        for i in range(num_samples // self.rx_buffer_size + 1):

            # write samples to receive buffer
            # they should already be complex

            # 1 is the timeout #TODO maybe set this intelligently based on the desired sample rate
            self.rx_stream.recv(receive_buffer, self.metadata, 1)

            # TODO set metadata correctly, sending real sample rate plus any error codes
            # sending complex signal
            store_array[:, i * self.rx_buffer_size : (i + 1) * self.rx_buffer_size] = receive_buffer

        wait_time = 0.1
        stop_time = self.usrp.get_time_now() + wait_time
        stop_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
        stop_cmd.stream_now = False
        stop_cmd.time_spec = stop_time
        self.rx_stream.issue_stream_cmd(stop_cmd)
        time.sleep(wait_time)  # TODO figure out what a realistic wait time is here.
        del self.rx_stream
        print("USRP RX Completed.")
        metadata = {
            "source": self.__class__.__name__,
            "sample_rate": self.rx_sample_rate,
            "center_frequency": self.rx_center_frequency,
            "gain": self.rx_gain,
        }

        return Recording(data=store_array[:, :num_samples], metadata=metadata)

    def init_tx(
        self,
        sample_rate: int | float,
        center_frequency: int | float,
        gain: int,
        channel: int,
        gain_mode: Optional[str] = "absolute",
    ):
        """
        Initialize the USRP for transmitting.

        :param sample_rate: The sample rate for transmitting.
        :type sample_rate: int or float

        :param center_frequency: The center frequency of the recording.
        :type center_frequency: int or float

        :param gain: The gain set for transmitting on the USRP.
        :type gain: int

        :param channel: The channel the USRP is set to.
        :type channel: int

        :param gain_mode: Gain mode setting. ``"absolute"`` passes gain directly to the SDR.
            ``"relative"`` means gain should be a negative value, which will be subtracted
            from the maximum gain.
        :type gain_mode: str
        """

        self.tx_buffer_size = 2000

        print(f"USRP TX Gain Mode = '{gain_mode}'")

        config_str = _generate_usrp_config_string(sample_rate=sample_rate, device_dict=self.device_dict)
        self.usrp = uhd.usrp.MultiUSRP(config_str)

        # check if channel arg is valid
        max_num_channels = self.usrp.get_rx_num_channels()
        if channel + 1 > max_num_channels:
            raise IOError(f"Channel {channel} not valid for device with {max_num_channels} channels.")

        # Ensure gain is within valid range
        gain_range = self.usrp.get_tx_gain_range()
        if gain_mode == "relative":
            if gain > 0:
                raise ValueError(
                    "When gain_mode = 'relative', gain must be < 0. This sets\
                          the gain relative to the maximum possible gain."
                )
            else:
                # set gain relative to max
                abs_gain = gain_range.stop() + gain
        else:
            abs_gain = gain
        if abs_gain < gain_range.start() or abs_gain > gain_range.stop():
            print(f"Gain {abs_gain} out of range for this USRP.")
            print(f"Gain range: {gain_range.start()} to {gain_range.stop()} dB")
            abs_gain = min(max(abs_gain, gain_range.start()), gain_range.stop())

        self.usrp.set_tx_gain(abs_gain, channel)

        # check if sample rate arg is valid
        sample_rate_range = self.usrp.get_tx_rates()
        if sample_rate < sample_rate_range.start() or sample_rate > sample_rate_range.stop():
            raise IOError(
                f"Sample rate {sample_rate} not valid for this USRP.\nValid\
                      range is {sample_rate_range.start()} to {sample_rate_range.stop()}."
            )
        self.usrp.set_tx_rate(sample_rate, channel)

        center_frequency_range = self.usrp.get_tx_freq_range()
        if center_frequency < center_frequency_range.start() or center_frequency > center_frequency_range.stop():
            raise IOError(
                f"Center frequency {center_frequency} out of range for USRP.\
                    \nValid range is {center_frequency_range.start()}\
                      to {center_frequency_range.stop()}."
            )
        self.usrp.set_tx_freq(uhd.libpyuhd.types.tune_request(center_frequency), channel)

        self.usrp.set_clock_source("internal")
        self.usrp.set_time_source("internal")
        self.usrp.set_tx_rate(sample_rate)
        self.usrp.set_tx_freq(uhd.types.TuneRequest(center_frequency), channel)
        self.usrp.set_tx_antenna("TX/RX", channel)

        # set internal variables for metadata
        self.tx_sample_rate = self.usrp.get_tx_rate(channel)
        self.tx_gain = self.usrp.get_tx_gain(channel)
        self.tx_center_frequency = self.usrp.get_tx_freq(channel)
        self.tx_channel = channel

        print(f"USRP TX Sample Rate = {self.tx_sample_rate}")
        print(f"USRP TX Center Frequency = {self.tx_center_frequency}")
        print(f"USRP TX Channel = {self.tx_channel}")
        print(f"USRP TX Gain = {self.tx_gain}")

        self._tx_initialized = True
        self._rx_initialized = False

    def close(self):
        pass

    def _stream_tx(self, callback):

        stream_args = uhd.usrp.StreamArgs("fc32", "sc16")  # wire and cpu data formats
        stream_args.channels = [self.tx_channel]
        tx_stream = self.usrp.get_tx_stream(stream_args)

        metadata = uhd.types.TXMetadata()

        metadata.start_of_burst = True
        metadata.end_of_burst = False
        self._enable_tx = True
        print("USRP Starting TX...")

        while self._enable_tx:
            buffer = callback(self.tx_buffer_size)
            tx_stream.send(buffer, metadata)
            metadata.start_of_burst = False

        print("USRP TX Completed.")

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
            self._num_samples_to_transmit = num_samples
        elif tx_time is not None:
            self._num_samples_to_transmit = int(tx_time * self.tx_sample_rate)
        else:
            self._num_samples_to_transmit = len(recording)

        if isinstance(recording, np.ndarray):
            samples = recording
        elif isinstance(recording, Recording):
            if len(recording.data) > 1:
                warnings.warn("Recording object is multichannel, only channel 0 data was used for transmission")

            samples = recording.data[0]

        samples = samples.astype(np.complex64, copy=False)

        # This is extremely important
        # Ensure array is contiguous
        samples = np.ascontiguousarray(samples)

        # Ensure correct byte order
        if samples.dtype.byteorder == ">":
            samples = samples.byteswap().newbyteorder()

        self._samples_to_transmit = samples
        self._num_samples_transmitted = 0

        self._stream_tx(self._loop_recording_callback)

    def set_clock_source(self, source):
        source = source.lower()
        if source == "external":
            self.usrp.set_clock_source(source)

        print(f"USRP clock source set to {self.usrp.get_clock_source(0)}")


def _create_device_dict(identifier_value=None):
    """
    Get the dictionary of information corresponding to any unique identifier,
    using uhd_find_devices.
    """

    available_devices = _parse_uhd_find_devices()
    print(available_devices)
    if identifier_value is None:
        print("\033[93mWarning: No USRP device identifier provided. Defaulting to the first USRP device found.\033[0m")
        if len(available_devices) > 0:
            formatted_dict_str = "\n".join([f"\t{key}: {value}" for key, value in available_devices[0].items()])
        else:
            raise IOError("\033[91mError: No USRP devices found.\033[0m")
        print(f"Device information: \n{formatted_dict_str}")
        return available_devices[0]

    identified_devices = []
    for device_dict in available_devices:
        for key, value in device_dict.items():
            if identifier_value is not None and str(value).lower() == str(identifier_value).lower():
                identified_devices.append(device_dict)
                break

    if len(identified_devices) > 1:
        print(f"\033[93mWarning: Found multiple USRP devices with identifier '{identifier_value}'.\033[0m")
        print("\033[93mDefaulting to the first USRP device found with this identifier.\033[0m")
        formatted_dict_str = "\n".join([f"\t{key}: {value}" for key, value in identified_devices[0].items()])
        print(f"Device information: \n{formatted_dict_str}")
        return identified_devices[0]

    elif len(identified_devices) == 1:
        print(f"\033[92mSuccessfully found USRP device with identifier '{identifier_value}'\033[0m")
        formatted_dict_str = "\n".join([f"\t{key}: {value}" for key, value in identified_devices[0].items()])
        print(f"Device information: \n{formatted_dict_str}")
        return identified_devices[0]

    elif len(identified_devices) == 0:
        raise IOError(f"\033[31mError: No USRP device found for identifier '{identifier_value}'.\033[0m")


def _generate_usrp_config_string(sample_rate, device_dict):
    """
    Create a correctly formatted string as expected by
    uhd.usrp.MultiUSRP constructor

    If it is a x300 there are two options for internal master clock settings
    master_clock_rate_string = self.force_srate_xseries(sample_rate)
    """

    if "type" in device_dict and device_dict["type"] == "x300":
        master_clock_rate_string = _force_srate_xseries(sample_rate)
    else:
        master_clock_rate_string = ""

    if "addr" in device_dict:
        ip_address_string = f"addr={device_dict['addr']},"
    else:
        ip_address_string = ""

    if "name" in device_dict:
        name_string = f"name={device_dict['name']},"
    else:
        name_string = ""

    config_string = ip_address_string + master_clock_rate_string + name_string

    return config_string


def _force_srate_xseries(sample_rate):
    two_hundred_rates = [200.0e6 / i for i in range(1, 201)]  # down to 1MHz wide
    one_eighty_four_rates = [184.32e6 / i for i in range(1, 185)]  # down to ~ 1MHz wide

    diff_two_hundred = min([abs(x - sample_rate) for x in two_hundred_rates])
    diff_one_eighty_four = min([abs(x - sample_rate) for x in one_eighty_four_rates])

    closest_list = "two_hundred_rates" if diff_two_hundred < diff_one_eighty_four else "one_eighty_four_rates"
    if closest_list == "one_eighty_four_rates":
        mcr_str = "master_clock_rate=184.32e6,"
        # print("MCR set to 184.32 MHz")
    else:
        mcr_str = ""
    return mcr_str


def _parse_uhd_find_devices():
    """
    Parse the uhd_find_devices subprocess command output into usable data.
    Returns: an array length = num_devices of dicts containing the data.
    """
    p = subprocess.Popen("uhd_find_devices", stdout=subprocess.PIPE)
    output, err = p.communicate()
    separate_devices = output.rsplit(b"--")
    cleaned_separate_devices = [device for device in separate_devices if len(device) >= 20]
    list_of_dicts = []
    for device_string in cleaned_separate_devices:
        device_as_list = device_string.split(b"\n")
        device_as_list = [device for device in device_as_list if len(device) >= 2]
        for i in range(len(device_as_list)):
            device_as_list[i] = device_as_list[i].strip(b" ")

        device_dict = {}
        for i in range(len(device_as_list)):
            [key, value] = device_as_list[i].split(b":")
            key = key.strip()
            value = value.strip()
            key = key.decode("utf-8")  # cast to string
            value = value.decode("utf-8")
            device_dict.update({key: value})

        list_of_dicts.append(device_dict)
    return list_of_dicts
