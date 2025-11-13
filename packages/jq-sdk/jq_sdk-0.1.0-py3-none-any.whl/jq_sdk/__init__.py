"""
JQ-SDK: A Python package for visualizing 1x1024 matrices as 32x32 heatmaps.

This package provides a simple and intuitive API for creating beautiful
heatmap visualizations with multiple color schemes using Plotly.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .heatmap import plot_heatmap, get_available_colorschemes, COLORSCHEMES

__all__ = [
    "plot_heatmap",
    "get_available_colorschemes",
    "COLORSCHEMES",
]
