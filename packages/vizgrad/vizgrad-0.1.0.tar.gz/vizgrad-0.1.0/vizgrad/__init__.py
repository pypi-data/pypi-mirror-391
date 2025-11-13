"""
VizGrad: A NumPy-based automatic differentiation library with visualization

VizGrad provides an educational and practical implementation of automatic
differentiation with rich visualization capabilities for understanding
gradient computation and optimization trajectories.

Example:
    >>> from vizgrad import Value
    >>> x = Value(2.0, name='x')
    >>> y = x**2 + 3*x
    >>> y.backward()
    >>> print(x.grad)  # dy/dx = 2*x + 3 = 7.0

Main Components:
    Value: Core autodiff class supporting scalar and tensor operations
"""

__version__ = "0.1.0"
__author__ = "Prabhanjana Ghuriki"
__license__ = "MIT"

from .core import Value, ValueVisualization

__all__ = [
    "Value",
    "ValueVisualization",
    "__version__",
]
