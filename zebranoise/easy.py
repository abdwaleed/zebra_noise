import imageio
from tqdm import tqdm
import warnings
from .util import generate_frames, filter_frames_index_function, apply_filters, discretize
from math import ceil
import multiprocessing
import concurrent.futures
import threading

def _generate_single_frame(args):
    """
    Top-level helper function required for multiprocessing.
    Now includes a queue to signal completion asynchronously.
    """
    _i, i, xsize, ysize, tsize, levels, xyscale, tscale, xscale, yscale, seed, filters, q = args
    
    # Original generation logic
    frame = generate_frames(xsize, ysize, tsize, [i], levels=levels, xyscale=xyscale, tscale=tscale, xscale=xscale, yscale=yscale, seed=seed)
    filtered = apply_filters(frame[None], filters, frame_index=_i)[0] 
    disc = discretize(filtered[:,:,0])
    
    # Send a tiny signal to the background thread that ONE frame is done
    q.put(1)
    
    return disc

def _progress_bar_listener(q, total):
    """
    Background thread target that updates tqdm whenever a frame finishes,
    regardless of chunking order.
    """
    pbar = tqdm(total=total, smoothing=0.1)
    for _ in range(total):
        q.get()  # Blocks until a core signals it finished a frame
        pbar.update(1)
    pbar.close()

def zebra_noise(output_file, xsize, ysize, tdur, levels=10, xyscale=.2, tscale=50, fps=30, xscale=1.0, yscale=1.0, seed=0, filters=[("comb", 0.08)]):
    """Generate a .mp4 of zebra noise.

    This method is a simplified interface for the PerlinStimulus class, designed to only generate zebra noise
    as defined in the paper.

    Parameters
    ----------
    output_file : string
        Filename to save the generated .mp4 file
    xsize, ysize : int
        The x and y dimensions of the output video. (Sometimes these will be rounded up to multiples of 16.)
    tdur : float
        The duration of the video in seconds
    levels : int
        The number of octaves to use when approximating the 1/f spectrum. The default of 10 should be more than enough.
    xyscale : float from (0,1)
        The spatial scale of the Perlin noise. Values near 0 will make the video smoother and near 1 choppier.
    tscale : int
        A scaling factor to set the speed of the video
    xscale, yscale : float
        Resize the x and y dimensions of the output
    fps : int
        Frames per second
    seed : int
        Random seed
    
    Returns
    -------
    None, but saves the video file to the desired filename
    """ 
    tsize = int(tdur * fps)
    tscale = tscale * (fps / 30)
    textra = (tscale - (tsize % tscale)) % tscale
    
    if textra > 0:
        warnings.warn(f"Adding {textra} extra timepoints to make tscale a multiple of tdur")
        
    tsize += round(textra) if (textra % 1 < 1e-5) else ceil(textra)
    get_index = filter_frames_index_function(filters, tsize)
    
    writer = imageio.get_writer(output_file, fps=fps)
    
    num_cores = max(1, multiprocessing.cpu_count() - 1)
    
    # MEMORY & UI OPTIMIZATION: Use a multiprocessing Manager to create a shared Queue
    manager = multiprocessing.Manager()
    progress_queue = manager.Queue()
    
    # This ensures the thread is killed instantly if the main program crashes, preventing terminal hangs.
    progress_thread = threading.Thread(
        target=_progress_bar_listener, 
        args=(progress_queue, tsize), 
        daemon=True
    )
    progress_thread.start()
    
    # Add the queue to our generator tasks
    tasks = (
        (_i, get_index(_i), xsize, ysize, tsize, levels, xyscale, tscale, xscale, yscale, seed, filters, progress_queue)
        for _i in range(tsize)
    )
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        # We cap the chunk_size at a maximum of 10. 
        # This keeps CPU IPC overhead low, but strictly limits RAM usage no matter how long the video is.
        chunk_size = min(10, max(1, tsize // (num_cores * 4)))
        
        # executor.map works silently at max speed while the thread handles UI
        for disc in executor.map(_generate_single_frame, tasks, chunksize=chunk_size):
            writer.append_data(disc)
            
    writer.close()
    
    # Ensure the background thread closes out cleanly
    progress_thread.join()
