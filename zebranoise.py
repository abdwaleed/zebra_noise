from zebranoise import easy

easy.zebra_noise("zebra.mp4", xsize=1280, ysize=720, xyscale=.2, tdur=60*0.5, tscale=50, fps=30, seed=0, filters=[("comb", 0.08), ("photodiode_anywhere", 0, 0, 140)])