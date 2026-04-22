import random

from arkitekt_next import log, register
from mikro_next.api.schema import Image
from rekuest_next.declare import declare


@declare(app="stardist", version="1.0")
class StardistLike:
    def segment_flou2(self, image: Image) -> Image:
        """A method that predicts instances in an image."""
        ...


@declare(app="frame", version="1.0")
class MicroscopeLike:
    def acquireFrame(self) -> Image:
        """A method that acquires an image."""
        ...


@declare(app="test-esp32", version="1.0")
class PumpLike:
    def toggleLed(self) -> None:
        """A method that toggles an LED on or off."""
        ...


def calculate_sphericity(image: Image) -> float:
    """Calculate the sphericity of each instance in the segmentation map
    and mean sphericity across all instances."""
    print(image.data)

    return random.uniform(0, 1)  # Placeholder for actual sphericity calculation


@register
def analyze_organoid(
    microscope: MicroscopeLike, stardist: StardistLike, pump_like: PumpLike
) -> None:
    """Acquire an image and predict instances."""
    image = microscope.acquireFrame()
    segmentation_map = stardist.segment_flou2(image)

    result = calculate_sphericity(segmentation_map)
    if result < 0.5:
        pump_like.toggleLed()
    else:
        log("Sphericity is above threshold, no action taken.")
