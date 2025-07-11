WINDOW_HEIGHT = 720     # px
WINDOW_WIDTH = 1280     # px
FRAME_RATE = 60         # fps
SAMPLE_RATE = 22050     # Hz

# SAMPLE_RATRE must be evenly divisible by FRAME_RATE for analysis routine
if SAMPLE_RATE % FRAME_RATE:
    SAMPLE_RATE = SAMPLE_RATE//FRAME_RATE * FRAME_RATE
