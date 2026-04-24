# %%
from arkitekt_next import interactive, find
from mikro_next.api.schema import Image, from_array_like
import numpy as np

# %%

app = interactive("test")

# %%
maxisp = find("82")


# %%
image = from_array_like(np.random.rand(5, 256, 256), name="test_image")
max_isp_image = maxisp.call(image)

max_isp_image.data
# %%
segment = find("34")


# %%
segmented = segment.call(image)

segmented.data
# %%
acquire = find("Mumpuimpione.pump")
stepper = find("14")

# %%
image = acquire.call()

image.data
# %%
import matplotlib.pyplot as plt

plt.imshow(segmented.data.squeeze(), cmap="gray")

# %%
segmented = segment.call(image)

plt.imshow(segmented.data.squeeze(), cmap="rainbow")

# %%

stepper.call(steps=56, is_rel=False, speed_hz=100, acceleration=7)

# %%
