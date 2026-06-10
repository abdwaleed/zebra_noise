# Zebranoise

Zebranoise is a high-performance Python library designed to generate "zebra noise" and, for advanced users, other Perlin noise-based visual stimulus videos. It relies on an Optimized-C-extension engine to rapidly generate high-framerate, high-resolution stimuli with highly adjustable parameters (resolution, fps, time duration, temporal scale, spatial scale), photodiode support, and a wide array of filters to choose from.

[Zebra Noise Demo Video](http://www.youtube.com/watch?v=-SyjgbNCP4Q)

[![Example zebra noise](http://img.youtube.com/vi/-SyjgbNCP4Q/0.jpg)](http://www.youtube.com/watch?v=-SyjgbNCP4Q "Example zebra noise")

## Quick Start

The `easy.py` module provides a simplified interface to generate a standard zebra noise video and output it directly to an `.mp4` file.

Create a Python script and use the following code to generate a stimulus:

```python
from zebranoise import easy

easy.zebra_noise(
    output_file="zebra.mp4", 
    xsize=1280, 
    ysize=720, 
    tdur=60*10,           # Duration in seconds (10 minutes)
    tscale=50,          # Temporal speed (higher is slower)
    xyscale=0.2,        # Spatial scale (closer to 0 is smoother, closer to 1 is choppier)
    fps=30, 
    seed=0, 
    filters=[
        ("comb", 0.08), 
        ("photodiode_anywhere", 0, 0, 140)
    ]
)

```

> **Important Note on Filters:** The `zebra_noise` function defaults to `filters=[("comb", 0.08)]` to generate the signature zebra pattern. If you pass a custom list to the `filters` parameter (e.g., to add a photodiode), it will completely overwrite the default list. You **must** explicitly include `("comb", 0.08)` in your new list to retain the zebra visual effect.

## Installation

### Standard Installation

Install the pre-compiled package directly from PyPI:

```bash
pip install zebranoise

```

### Installation from Source

Because the core engine is written in C for performance, your system must have a C compiler installed to build the package from source.

* **Linux:** Ensure `gcc` is installed.
* **Windows:** You must install the **Microsoft C++ Build Tools** (available via the Visual Studio Installer) with the "Desktop development with C++" workload selected.

**Modern Environments (Recommended)**
Modern versions of `pip` automatically provision a build environment and fetch necessary dependencies (like Cython) in the background. Once your compiler is ready, run:

```bash
pip install .

```

**Legacy Environments**
If you are using an older Python environment or an outdated version of `pip` that does not support isolated builds, you must manually install Cython before invoking the legacy setup script:

```bash
pip install cython
python setup.py install

```

### Development Installation

If you plan to modify the package source code, clone the repository and install it in "editable" mode. This allows your changes to reflect immediately without needing to reinstall:

```bash
pip install -e .

```

## Advanced Usage

For researchers generating highly complex stimuli or those needing to apply filters iteratively without regenerating the base noise, use the `PerlinStimulus` class.

> **Warning: Disk Space Requirements**
> The `PerlinStimulus` class caches large, uncompressed numpy arrays to your hard drive to optimize RAM usage. It creates a `perlcache/` directory in your working folder and utilizes your system's temporary directory. Ensure you have ample free disk space (tens to hundreds of gigabytes) before generating long or high-resolution videos.

```python
import zebranoise

# Step 1: Generate the raw 3D noise matrix and cache it to disk
stim = zebranoise.PerlinStimulus(
    xsize=480, 
    ysize=128, 
    tdur=60*5,        # 5 minutes
    xyscale=0.2, 
    tscale=50
)

# Step 2: Apply filters and render the final MP4
stim.save_video(
    "perlin_stimulus.mp4", 
    loop=1, 
    filters=[("comb", 0.08), ("photodiode", 30)]
)

```

## Filters & Photodiode Support

Filters modify the raw Perlin noise to create distinct visual patterns or add synchronization metadata for laboratory recording hardware. Provide filters as a list of strings (for filters with no arguments) or tuples (for filters requiring arguments).

### Pattern Filters

* **`("comb", value)`**: Alternates black and white thresholds at the given interval to create zebra stripes. The default threshold for standard zebra noise is **0.08**.
* **`("threshold", value)`**: Sets all values above the argument to pure white, and all below to pure black.
* **`("softthresh", temp)`**: Similar to `threshold`, but renders gray edges based on the provided temperature argument using a sigmoid function.
* **`("wood", value)`**: Uses a sawtooth wave to create a gradient-heavy pattern resembling wood grain.
* **`"center"`**: Forces extreme darks and lights toward the center (gray).
* **`("blur", sigma)`**: Applies a Gaussian blur with the defined standard deviation.

### Utility Filters

* **`"invert"`**: Swaps white and black pixels.
* **`"reverse"`**: Renders the video frames in reverse chronological order.
* **`[custom_function]`**: Pass any Python function. It will receive a 3D image array chunk and must return the modified array.

### Hardware Synchronization (Photodiodes)

* **`("photodiode", size)`**: Draws a sync square in the corner of the specified size, alternating black on even frames and white on odd frames.
* **`("photodiode_anywhere", x, y, size)`**: Draws an alternating sync square at the exact X/Y coordinates provided.
* **`"photodiode_b2"`** / **`"photodiode_fusi"`** / **`"photodiode_bscope"`**: Pre-configured sync squares tailored for specific rig setups.

## Credits

Portions of the optimized C code (`_perlin.c`) are based on Casey Duncan's `noise` package for Python, distributed under the MIT license. Modified and expanded for video stimulus generation by Max Shinn.
