import numpy as np
import scipy.ndimage
from . import _perlin

XYSCALEBASE = 100

def filter_frames(im, filt, *args, frame_index):
    """Apply a filter/transformation to an image batch

    Parameters
    ----------
    im : 3D float ndarray, values ∈ [0,1]
        Frames to filter
    filt : str
        The name of the filter
    *args : tuple
        Extra arguments are passed to the filter

    Returns
    -------
    im : 3D float ndarray, values ∈ [0,1]
        Filtered noise movie
    """
    if filt == "threshold":
        return (im>args[0]).astype(np.float32)
    if filt == "softthresh":
        # Pre-allocate one array, then perform all math in-place to prevent RAM spikes
        res = np.subtract(im, 0.5)
        np.multiply(res, -args[0], out=res)
        np.exp(res, out=res)
        np.add(res, 1.0, out=res)
        np.divide(1.0, res, out=res)
        return res
    if filt == "comb":
        return (im//args[0] % 2 == 1).astype(np.float32)
    if filt == "invert":
        return 1-im
    if filt == "reverse":
        return im # We need to use filter_index_function for this
    if filt == "blur":
        # Vectorized in C: Blurs X and Y (sigma=args[0]), ignores Time axis (sigma=0).
        return scipy.ndimage.gaussian_filter(im, sigma=(args[0], args[0], 0), mode='wrap')
    if filt == "wood":
        return (im % args[0]) / args[0]
    if filt == "center":
        return 1-(np.abs(im-.5)*2)
    if filt == "photodiode":
        s = args[0]
        if frame_index % 2 == 0:
            im[..., :s, -s:, :] = 1 
        else:
            im[..., :s, -s:, :] = 0 
        return im
    if filt == "photodiode_anywhere":
        x = args[0]
        y = args[1]
        s = args[2]
        
        if frame_index % 2 == 0:
            im[..., y:(y+s),x:(x+s),:] = 1
        else:
            im[..., y:(y+s),x:(x+s),:] = 0
        return im
    if filt == "photodiode_b2":
        s = 125
        if frame_index % 2 == 0:
            im[..., :s, -s:, :] = 1 
        else:
            im[..., :s, -s:, :] = 0 
        return im
    if filt == "photodiode_fusi":
        s = 75
        if frame_index % 2 == 0:
            im[..., :s, -s:, :] = 1 
        else:
            im[..., :s, -s:, :] = 0 
        return im
    if filt == "photodiode_bscope":
        s = 100
        if frame_index % 2 == 0:
            im[..., :s, -s:, :] = 1 
        else:
            im[..., :s, -s:, :] = 0 
        return im
    if callable(filt):
        return filt(im)
    raise ValueError("Invalid filter specified")

def apply_filters(arr, filters, frame_index=None):
    for f in filters:
        if isinstance(f, str):
            n = f
            args = []
        else:
            n = f[0]
            args = f[1:]
        arr = filter_frames(arr, n, *args, frame_index=frame_index)
    return arr


def filter_frames_index_function(filters, nframes):
    """Reordering frames in the video based on the filter.


    Parameters
    ----------
    filters : list of strings or tuples
        the list of filters passed to save_video

    Returns
    -------
    function mapping int -> int
        Reindexing function

    Notes
    -----
    Some filters may need to operate on the global video instead of in
    batches.  However, for large videos, batches are necessary due to
    limited amounts of RAM.  Thus, this function should return another
    function which takes an index as input and outputs a new index,
    remapping the initial noise frame to the output video frame.  This
    was primarily designed to support reversing the video, but it might be
    useful for other things too.

    """
    if "reverse" in filters:
        return lambda x : nframes - x - 1
    return lambda x : x

def discretize(im):
    """Convert movie to an unsigned 8-bit integer

    Parameters
    ----------
    im : 3D float ndarray, values ∈ [0,1]
        Noise movie

    Returns
    -------
    3D int ndarray, values ∈ [0,255]
        Noise movie
    """
    im *= 255
    return im.astype(np.uint8, copy=False)

def generate_frames(xsize, ysize, tsize, timepoints, levels=10, xyscale=.5, tscale=1, xscale=1.0, yscale=1.0, fps=30, seed=0):
    """Preprocess arguments before passing to the C implementation of Perlin noise.
    """
    # Use the temporal scale and number of timepoints to compute how many
    # units to make the stimulus across the temporal dimension
    tunits = int(tsize/(tscale*(fps/30)))
    if tunits >= 4096:
        raise ValueError("Too many time points.  Either make the tscale larger or tsize smaller")
    ts_all = np.arange(0, tsize, dtype="float32")/(tscale*(fps/30))
    ratio = int(xsize/ysize*XYSCALEBASE)
    arr = _perlin.make_perlin(np.arange(0, xsize, dtype="float32")/ysize/xscale, # Yes, divide by y size
                              np.arange(0, ysize, dtype="float32")/ysize/yscale,
                              ts_all[timepoints],
                              octaves=levels,
                              persistence=xyscale,
                              repeatx=ratio,
                              repeaty=XYSCALEBASE,
                              repeatz=tunits,
                              base=seed)
    arr = arr.swapaxes(0,1)
    return arr
