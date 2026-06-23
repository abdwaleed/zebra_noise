# Zebranoise

Zebranoise is a high-performance Python library designed to generate "zebra noise" and, for advanced users, other Perlin noise-based visual stimulus videos. It relies on an Optimized-C-extension engine to rapidly generate high-framerate, high-resolution stimuli with highly adjustable parameters (resolution, fps, time duration, temporal scale, spatial scale), photodiode support, and a wide array of filters to choose from.

[Zebra Noise Demo Video](http://www.youtube.com/watch?v=-SyjgbNCP4Q)

[![Example zebra noise](http://img.youtube.com/vi/-SyjgbNCP4Q/0.jpg)](http://www.youtube.com/watch?v=-SyjgbNCP4Q "Example zebra noise")

**PRENOTE**: please be sure to read the notes described in the **Filters & Photodiode Support** section below to avoid any errors.

## Installation

Because the core engine is written in C for maximum performance, your system **must have a C compiler installed** to build the package on your machine.

* **Linux:** Ensure `gcc` is installed.
* **Windows:** You must install the **Microsoft C++ Build Tools** (available via the Visual Studio Installer) with the "Desktop development with C++" workload selected.

### Standard Installation

Install the pre-compiled package directly from PyPI:

```bash
pip install git+[https://github.com/abdwaleed/zebra_noise.git](https://github.com/abdwaleed/zebra_noise.git)
```

Then use the code below:
#### Example Code
```python
import zebranoise

if __name__ == "__main__":
    zebranoise.zebra_noise(
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
            # ("photodiode_anywhere", 0, 0, 140) # Photodiode Support
        ]
    )
```

> **Important Note on Filters:** The `zebra_noise` function defaults to `filters=[("comb", 0.08)]` to generate the signature zebra pattern. If you pass a custom list to the `filters` parameter (e.g., to add a photodiode), it will completely overwrite the default list. You **must** explicitly include `("comb", 0.08)`, with any desired comb value, in your new list to retain the zebra visual effect.

> **Important Note for Windows Users**: `if __name__ == "__main__":` must be included for the `multiprocessing` Python module to not throw an error. 

### Installation from Source

Proceed to clone the repository. More information is available on [GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

For this next step, ensure you are working within the repository's root folder.

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

Finally, use the code below:
#### Example Code
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
        # ("photodiode_anywhere", 0, 0, 140) # Photodiode Support
    ]
)
```

### Developer Installation

If you plan to modify the package source code, clone the repository and follow the same steps in the **Installation from Source** section **BUT** install the repository in "editable" mode instead (pip command below). Use the same example code too:

```bash
pip install -e .
```

## Advanced Usage

This package can be used to generate new stimuli based on Perlin noise.

> **Warning: Disk Space Requirements**
> The program will cache large, uncompressed numpy arrays to your hard drive to optimize RAM usage. It creates a `perlcache/` directory in your working folder and utilizes your system's temporary directory. Ensure you have ample free disk space (tens to hundreds of gigabytes) before generating long or high-resolution videos.

To generate a Perlin noise-based video, follow the steps in the 2 code blocks below:

### Step 1: Generate the raw 3D noise matrix and cache it to disk
```python
import zebranoise

# Step 1: Generate the raw 3D noise matrix and cache it to disk
noise_stim = zebranoise.PerlinStimulus(
    xsize=400, 
    ysize=100, 
    tdur=60*5,        # 5 minutes
    xyscale=0.2, 
    tscale=50
)
```

See the function documentation for **perlstim.Perl** for more information about modifying the properties of the noise.

### Step 2: Apply filters and render the final MP4
```python
# Step 2: Apply filters and render the final MP4
noise_stim.save_video(
    "perlin_stimulus.mp4", 
    loop=1, 
    filters=[("comb", 0.08), ("photodiode", 30)]
)
```

See the **Filters & Photodiode Support** section below for more information about filters.

## Filters & Photodiode Support

Filters modify the raw Perlin noise to create distinct visual patterns or add photodiode patches for lab hardware synchronization. 

**NOTE:** Provide filters as a list with strings for filters with no arguments and tuples for filters requiring arguments.Example:

> **Important Note on Filters:** The `zebra_noise` function defaults to `filters=[("comb", 0.08)]` to generate the signature zebra pattern. If you pass a custom list to the `filters` parameter (e.g., to add a photodiode), it will completely overwrite the default list. You **must** explicitly include `("comb", 0.08)`, with any desired comb value, in your new list to retain the zebra visual effect.

```python
# Applies the "reverse" filter (with no arguments) and the "comb" filter with the argument .05
noise.save_video("noise.mp4", filters=["reverse", ("comb", .05)])
```

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

This repository is a fork of the original `zebra_noise` package developed by Max Shinn, modified and maintained by Abdelrahman A.

Portions of the optimized C code (`_perlin.c`) are based on [Casey Duncan's `noise` package for Python](https://github.com/caseman/noise), distributed under the MIT license. Modified and expanded for video stimulus generation by Max Shinn.
