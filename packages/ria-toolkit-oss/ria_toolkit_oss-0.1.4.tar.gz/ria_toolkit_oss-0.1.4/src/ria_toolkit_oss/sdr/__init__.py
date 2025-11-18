"""
This package provides a unified API for working with a variety of software-defined radios.
It streamlines tasks involving signal reception and transmission, as well as common administrative
operations such as detecting and configuring available devices.
"""

__all__ = ["SDR"]

from .sdr import SDR
