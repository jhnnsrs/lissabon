# %%
from arkitekt_next import interactive, find
from mikro_next.api.schema import Image
import numpy as np

# %%

app = interactive("test")


# %%
segment = find("imswitch.acquire_frame")

# %%
acquire = find("58")
stepper = find("14")

# %%
image = acquire.call()

image.data
# %%
import matplotlib.pyplot as plt

plt.imshow(image.data.squeeze(), cmap="gray")

# %%
segmented = segment.call(image)

plt.imshow(segmented.data.squeeze(), cmap="rainbow")

# %%

stepper.call(steps=56, is_rel=False, speed_hz=100, acceleration=7)

# %%
