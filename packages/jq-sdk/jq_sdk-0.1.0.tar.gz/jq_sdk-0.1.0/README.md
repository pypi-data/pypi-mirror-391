# JQ-SDK

A Python package for visualizing 1x1024 matrices as beautiful 32x32 heatmaps with multiple color schemes.

## Features

- Convert 1D arrays (1024 elements) into 32x32 heatmap visualizations
- Interactive Plotly-based heatmaps
- 10 beautiful pre-configured color schemes
- Simple and intuitive API
- Python 3.7+ support

## Installation

Install from PyPI:

```bash
pip install jq-sdk
```

Or install from source:

```bash
git clone https://github.com/yourusername/JQ-SDK.git
cd JQ-SDK
pip install -e .
```

## Quick Start

```python
import jq_sdk

# Create sample data (1024 elements)
data = list(range(1, 1025))

# Plot with default color scheme (viridis)
fig = jq_sdk.plot_heatmap(data)
fig.show()

# Use a different color scheme
fig = jq_sdk.plot_heatmap(data, colorscheme='plasma')
fig.show()

# Customize the plot
fig = jq_sdk.plot_heatmap(
    data,
    colorscheme='hot',
    title='My Custom Heatmap',
    width=1000,
    height=1000
)
fig.show()
```

## Available Color Schemes

JQ-SDK provides 10 beautiful color schemes:

- `viridis` (default) - Purple to yellow gradient
- `plasma` - Dark purple to yellow gradient
- `hot` - Black to red to yellow
- `blues` - White to dark blue
- `reds` - White to dark red
- `greens` - White to dark green
- `rainbow` - Full spectrum rainbow
- `inferno` - Black to purple to yellow
- `magma` - Black to purple to white
- `cividis` - Colorblind-friendly blue to yellow

You can get the list programmatically:

```python
import jq_sdk

schemes = jq_sdk.get_available_colorschemes()
print(schemes)
```

## API Reference

### `plot_heatmap(data, colorscheme='viridis', title='Heatmap Visualization', show_colorbar=True, width=800, height=800)`

Plot a 1x1024 matrix as a 32x32 heatmap.

**Parameters:**

- `data` (list or numpy.ndarray): Input data with exactly 1024 elements
- `colorscheme` (str, optional): Color scheme name. Default is 'viridis'
- `title` (str, optional): Title of the heatmap. Default is 'Heatmap Visualization'
- `show_colorbar` (bool, optional): Whether to show the colorbar. Default is True
- `width` (int, optional): Width of the figure in pixels. Default is 800
- `height` (int, optional): Height of the figure in pixels. Default is 800

**Returns:**

- `plotly.graph_objects.Figure`: Plotly figure object. Call `.show()` to display.

**Raises:**

- `ValueError`: If input data does not contain exactly 1024 elements
- `KeyError`: If an invalid colorscheme is specified

### `get_available_colorschemes()`

Get a list of available color schemes.

**Returns:**

- `list`: List of available colorscheme names

## Examples

### Basic Usage

```python
import jq_sdk
import numpy as np

# Using a list
data = list(range(1024))
fig = jq_sdk.plot_heatmap(data)
fig.show()

# Using numpy array
data = np.random.rand(1024)
fig = jq_sdk.plot_heatmap(data, colorscheme='plasma')
fig.show()
```

### Comparing Different Color Schemes

```python
import jq_sdk
import numpy as np

# Generate sample data
data = np.sin(np.linspace(0, 4*np.pi, 1024))

# Try different color schemes
for scheme in ['viridis', 'plasma', 'hot', 'rainbow']:
    fig = jq_sdk.plot_heatmap(
        data,
        colorscheme=scheme,
        title=f'Heatmap with {scheme} colorscheme'
    )
    fig.show()
```

### Saving to File

```python
import jq_sdk

data = list(range(1, 1025))
fig = jq_sdk.plot_heatmap(data, colorscheme='viridis')

# Save as HTML
fig.write_html('heatmap.html')

# Save as PNG (requires kaleido)
# pip install kaleido
fig.write_image('heatmap.png')
```

## Requirements

- Python >= 3.7
- numpy >= 1.19.0
- plotly >= 5.0.0

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub issue tracker](https://github.com/yourusername/JQ-SDK/issues).

## Changelog

### 0.1.0 (Initial Release)

- Initial release with basic heatmap visualization
- Support for 10 color schemes
- Interactive Plotly-based visualizations
- Python 3.7+ support
