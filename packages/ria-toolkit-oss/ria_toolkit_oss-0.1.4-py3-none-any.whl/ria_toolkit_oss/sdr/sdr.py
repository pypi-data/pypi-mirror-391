import math
import pickle
import warnings
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import zmq

from ria_toolkit_oss.datatypes.recording import Recording


class SDR(ABC):
    """
    This class defines a common interface (a template) for all SDR devices.
    Each specific SDR implementation should subclass SDR and provide concrete implementations
    for the abstract methods.

    To add support for a new radio, subclass this  interface and implement all abstract methods.
    If you experience difficulties, please `contact us <mailto:info@qoherent.ai>`_, we are happy to
    provide additional direction and/or help with the implementation details.
    """

    def __init__(self):

        self._rx_initialized = False
        self._tx_initialized = False
        self._enable_rx = False
        self._enable_tx = False
        self._accumulated_buffer = None
        self._max_num_buffers = None
        self._num_buffers_processed = 0
        self._accumulated_buffer = None
        self._last_buffer = None

    def record(self, num_samples: Optional[int] = None, rx_time: Optional[int | float] = None) -> Recording:
        """
        Create a radio recording of a given length. Either ``num_samples`` or ``rx_time`` must be provided.

        Note that ``init_rx()`` must be called before ``record()``.

        :param num_samples: The number of samples to record.
        :type num_samples: int, optional
        :param rx_time: The time to record.
        :type rx_time: int or float, optional

        :return: The Recording object
        :rtype: Recording
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

        self.buffer_size = self.rx_buffer_size
        num_buffers = self._num_samples_to_record // self.buffer_size + 1

        self._max_num_buffers = num_buffers
        self._num_buffers_processed = 0
        self._num_buffers_processed = 0
        self._last_buffer = None
        self._accumulated_buffer = None
        print("Starting stream")

        self._stream_rx(
            callback=self._accumulate_buffers_callback,
        )

        print("Finished stream")
        metadata = {
            "source": self.__class__.__name__,
            "sample_rate": self.rx_sample_rate,
            "center_frequency": self.rx_center_frequency,
            "gain": self.rx_gain,
        }

        print("Creating recording")
        # build recording, truncate to self._num_samples_to_record
        recording = Recording(data=self._accumulated_buffer[:, : self._num_samples_to_record], metadata=metadata)

        # reset to record again
        self._accumulated_buffer = None
        return recording

    def stream_to_zmq(self, zmq_address, n_samples: int, buffer_size: Optional[int] = 10000):
        """
        Stream iq samples as interleaved bytes via zmq.

        :param zmq_address: The zmq address.
        :type zmq_address:
        :param n_samples: The number of samples to stream.
        :type n_samples: int
        :param buffer_size: The buffer size during streaming. Defaults to 10000.
        :type buffer_size: int, optional

        :return: The trimmed Recording.
        :rtype: Recording
        """

        self._previous_buffer = None
        self._max_num_buffers = np.inf if n_samples == np.inf else math.ceil(n_samples / buffer_size)
        self._num_buffers_processed = 0
        self.zmq_address = _generate_full_zmq_address(str(zmq_address))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(self.zmq_address)

        self._stream_rx(
            self._zmq_bytestream_callback,
        )

        self.context.destroy()
        self.socket.close()

    def _accumulate_buffers_callback(self, buffer, metadata=None):
        """
        Receives a buffer and saves it to self.accumulated_buffer.
        """
        # expected buffer is complex samples range -1 to 1
        # save the buffer until max reached
        # return a recording

        buffer = np.array(buffer)  # make it 1d
        if len(buffer.shape) == 1:
            buffer = np.array([buffer])

        # it runs these checks each time, is that an efficiency issue?

        if self._max_num_buffers is None:
            # default then
            # this should probably print, but that would happen every buffer...
            raise ValueError("Number of buffers for block capture not set.")

        # add the given buffer to the pre-allocated buffer

        if metadata is not None:
            self.received_metadata = metadata

        # TODO optimize, pre-allocate
        if self._accumulated_buffer is not None:
            self._accumulated_buffer = np.concatenate((self._accumulated_buffer, buffer), axis=1)
        else:
            # the first time
            self._accumulated_buffer = buffer.copy()

        self._num_buffers_processed = self._num_buffers_processed + 1
        if self._num_buffers_processed >= self._max_num_buffers:
            self.stop()

        if self._last_buffer is not None:
            if (buffer == self._last_buffer).all():
                print("\033[93mWarning: Buffer Overflow Detected\033[0m")
            self._last_buffer = buffer.copy()
        else:
            self._last_buffer = buffer.copy()

        # print("Number of buffers received: " + str(self._num_buffers_processed))

    def _zmq_bytestream_callback(self, buffer, metadata=None):
        # push to ZMQ port
        data = np.array(buffer).tobytes()  # convert to bytes for transport
        self.socket.send(data)

        # print(f"Sent {self._num_buffers_processed} ZMQ buffers to {self.zmq_address}")

        self._num_buffers_processed = self._num_buffers_processed + 1
        if self._max_num_buffers is not None:
            if self._num_buffers_processed >= self._max_num_buffers:
                self.pause_rx()

        if self._previous_buffer is not None:
            if (buffer == self._previous_buffer).all():
                print("\033[93mWarning: Buffer Overflow Detected\033[0m")
                # TODO: I suggest we think about moving this part to the top of this function
                # and skip the rest of the function in case of overflow.
                # like, it's not necessary to stream repeated IQ data anyways!
        self._previous_buffer = buffer.copy()

    def pickle_buffer_to_zmq(self, zmq_address, buffer_size, num_buffers):
        """
        Stream samples to a zmq address, packaged in binary buffers using numpy.pickle.
        Useful for inference applications with a known input size.
        May reduce transfer rates, but individual buffers will not have discontinuities.

        :param zmq_address: The tcp address to stream to.
        :type zmq_address: str
        :param buffer_size: The number of iq samples in a buffer.
        :type buffer_size: int
        :param num_buffers: The number of buffers to stream before stopping.
        :type num_buffers: int
        """
        self._max_num_buffers = num_buffers
        self.buffer_size = buffer_size
        self._num_buffers_processed = 0
        self.zmq_address = _generate_full_zmq_address(str(zmq_address))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(self.zmq_address)
        self.set_rx_buffer_size(buffer_size)

        self._stream_rx(self._zmq_pickle_buffer_callback)

    def _zmq_pickle_buffer_callback(self, buffer, metadata=None):
        # push to ZMQ port
        # data = np.array(buffer).tobytes()  # convert to bytes for transport
        # self.socket.send(data)

        self.socket.send(pickle.dumps(buffer))

        # print(f"Sent {self._num_buffers_processed} ZMQ buffers to {self.zmq_address}")

        self._num_buffers_processed = self._num_buffers_processed + 1
        if self._max_num_buffers is not None:
            if self._num_buffers_processed >= self._max_num_buffers:
                self.stop()

        if self._last_buffer is not None:
            if (buffer == self._last_buffer).all():
                print("\033[93mWarning: Buffer Overflow Detected\033[0m")
            self._last_buffer = buffer.copy()
        else:
            self._last_buffer = buffer.copy()

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

        if not self._tx_initialized:
            raise RuntimeError(
                "TX was not initialized. init_tx() must be called before _stream_tx() or transmit_recording()"
            )

        if num_samples is not None and tx_time is not None:
            raise ValueError("Only input one of num_samples or tx_time")
        elif num_samples is not None:
            self._num_samples_to_transmit = num_samples
        elif tx_time is not None:
            self._num_samples_to_transmit = tx_time * self.tx_sample_rate
        else:
            self._num_samples_to_transmit = len(recording)

        if isinstance(recording, np.ndarray):
            self._samples_to_transmit = recording
        elif isinstance(recording, Recording):
            if len(recording.data) > 1:
                warnings.warn("Recording object is multichannel, only channel 0 data was used for transmission")

            self._samples_to_transmit = recording.data[0]

        self._num_samples_transmitted = 0

        self._stream_tx(self._loop_recording_callback)

    def _loop_recording_callback(self, num_samples):

        samples_left = self._num_samples_to_transmit - self._num_samples_transmitted
        # find where to start based on num_samples_transmitted
        start_index = self._num_samples_transmitted % len(self._samples_to_transmit)

        # generates an array of indices that wrap around as many times as necessary.
        indices = np.arange(start_index, start_index + num_samples) % len(self._samples_to_transmit)
        samples = self._samples_to_transmit[indices]

        # zero pad at the end so we are still giving the requested buffer size
        # while also giving the exact number of non zero samples
        if len(samples) > samples_left:
            samples[int(samples_left) :] = 0
            self.pause_tx()

        self._num_samples_transmitted = self._num_samples_transmitted + num_samples

        return samples

    def pause_rx(self):
        self._enable_rx = False

    def pause_tx(self):
        self._enable_tx = False

    def stop(self):
        self.pause_rx()

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def init_rx(self, sample_rate, center_frequency, gain, channel, gain_mode):
        pass

    @abstractmethod
    def init_tx(self, sample_rate, center_frequency, gain, channel, gain_mode):
        pass

    @abstractmethod
    def _stream_rx(self, callback):
        pass

    @abstractmethod
    def _stream_tx(self, callback):
        pass

    @abstractmethod
    def set_clock_source(self, source):
        """
        Sets the clock source to external or internal.

        :param source: The clock source
        :type source: str
        """
        pass


def _generate_full_zmq_address(input_address):
    """
    Helper function for zmq streaming.
    If given a port number like 5556,
    return tcp localhost address at that port.
    Otherwise, return the address untouched.
    """

    if ("://" not in str(input_address)) and _is_valid_port(input_address):
        # If no transport protocol specified, assume TCP
        return "tcp://*:" + str(input_address)
    else:
        # Otherwise, return the input unchanged
        return input_address


def _is_valid_port(port):
    """
    Helper function for zmq address.
    """
    try:
        port_num = int(port)
        return 0 <= port_num <= 65535
    except ValueError:
        return False


def _verify_sample_format(samples):
    """
    Verify that the sample data is in the range -1 to 1.

    :param buffer: An array of samples.

    :Return: True if the buffer is in the correct format, false if not.
    :rtype: bool
    """

    return np.max(np.abs(samples)) <= 1
