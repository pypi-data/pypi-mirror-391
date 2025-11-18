"""
PWQ_QR_Gen_4 – A fully customizable QR Code Generator.
Developed by PawlexCode95.
"""

from .PWQ_QR_Gen_4 import (
    PWQ_QR_GEN_4,
    PWQ_QR_Segmentation,
    BitOverflowError,
    ECIEncodingError,
    PWQAIUnprovidedError,
    DataTooLongError,
)

__all__ = [
    "PWQ_QR_GEN_4",
    "PWQ_QR_Segmentation",
    "BitOverflowError",
    "ECIEncodingError",
    "PWQAIUnprovidedError",
    "DataTooLongError",
]

__version__ = "4.0.42"
