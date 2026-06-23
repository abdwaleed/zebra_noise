from zebranoise import easy

if __name__ == '__main__':
    # easy.zebra_noise("zebra_30.mp4", xsize=1280, ysize=720, xyscale=.2, tdur=60*10, tscale=50, fps=30, seed=0, filters=[("comb", 0.08), ("photodiode_anywhere", 0, 0, 140)])

    fps = 30
    time = 60 * 10 # 60 * minutes
    easy.zebra_noise(f"zebra_{fps}_{time}min.mp4", xsize=1280, ysize=720, xyscale=.2, tdur=time, tscale=50, fps=fps, seed=0, filters=[("comb", 0.08), ("photodiode_anywhere", 1140, 0, 140)])