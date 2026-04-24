# code code code


from arkitekt_next import easy, find
import numpy as np


image = np.zeros((5, 256, 256))


with easy("my_rasberrypi_pi"):
    x = find("starmist.segment_image")
    segment = x.call(image)
