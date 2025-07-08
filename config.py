WINDOW_HEIGHT = 1080    # px
WINDOW_WIDTH = 1920     # px
FRAME_RATE = 60         # fps
SAMPLE_RATE = 22050     # Hz

# SAMPLE_RATRE must be evenly divisible by FRAME_RATE for analysis routine
if SAMPLE_RATE % FRAME_RATE:
    SAMPLE_RATE = SAMPLE_RATE//FRAME_RATE * FRAME_RATE
