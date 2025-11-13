"""
Core heatmap visualization functionality for JQ-SDK.

This module provides functions to visualize 1x1024 matrices as 32x32 heatmaps
using Plotly with various color schemes.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Union, List


# Available color schemes
COLORSCHEMES = {
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'hot': 'Hot',
    'blues': 'Blues',
    'reds': 'Reds',
    'greens': 'Greens',
    'rainbow': 'Jet',
    'inferno': 'Inferno',
    'magma': 'Magma',
    'cividis': 'Cividis'
}


def plot_heatmap(
    data: Union[List[float], np.ndarray],
    colorscheme: str = 'viridis',
    title: str = 'Heatmap Visualization',
    show_colorbar: bool = True,
    width: int = 800,
    height: int = 800
) -> go.Figure:
    """
    Plot a 1x1024 matrix as a 32x32 heatmap.

    Parameters
    ----------
    data : Union[List[float], np.ndarray]
        Input data as a 1D array or list with exactly 1024 elements.
        Will be reshaped to 32x32 for visualization.

    colorscheme : str, optional
        Color scheme for the heatmap. Default is 'viridis'.
        Available options: 'viridis', 'plasma', 'hot', 'blues', 'reds',
        'greens', 'rainbow', 'inferno', 'magma', 'cividis'

    title : str, optional
        Title of the heatmap. Default is 'Heatmap Visualization'.

    show_colorbar : bool, optional
        Whether to show the colorbar. Default is True.

    width : int, optional
        Width of the figure in pixels. Default is 800.

    height : int, optional
        Height of the figure in pixels. Default is 800.

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly figure object containing the heatmap.
        Call .show() on the returned object to display it.

    Raises
    ------
    ValueError
        If the input data does not contain exactly 1024 elements.

    KeyError
        If an invalid colorscheme is specified.

    Examples
    --------
    >>> import jq_sdk
    >>> data = list(range(1, 1025))
    >>> fig = jq_sdk.plot_heatmap(data)
    >>> fig.show()

    >>> # Use different color scheme
    >>> fig = jq_sdk.plot_heatmap(data, colorscheme='plasma')
    >>> fig.show()
    """
    # Convert to numpy array if list
    if isinstance(data, list):
        data = np.array(data)

    # Validate input size
    if data.size != 1024:
        raise ValueError(
            f"Input data must contain exactly 1024 elements, got {data.size}"
        )

    # Validate colorscheme
    if colorscheme not in COLORSCHEMES:
        available = ', '.join(COLORSCHEMES.keys())
        raise KeyError(
            f"Invalid colorscheme '{colorscheme}'. "
            f"Available options: {available}"
        )

    # Reshape to 32x32
    matrix = data.reshape(32, 32)

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        colorscale=COLORSCHEMES[colorscheme],
        showscale=show_colorbar,
        hovertemplate='Row: %{y}<br>Col: %{x}<br>Value: %{z}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Column',
        yaxis_title='Row',
        width=width,
        height=height,
        xaxis=dict(side='bottom'),
        yaxis=dict(autorange='reversed')  # Top-down indexing
    )

    return fig


def get_available_colorschemes() -> List[str]:
    """
    Get a list of available color schemes.

    Returns
    -------
    List[str]
        List of available colorscheme names.

    Examples
    --------
    >>> import jq_sdk
    >>> schemes = jq_sdk.get_available_colorschemes()
    >>> print(schemes)
    ['viridis', 'plasma', 'hot', 'blues', 'reds', 'greens', 'rainbow',
     'inferno', 'magma', 'cividis']
    """
    return list(COLORSCHEMES.keys())
