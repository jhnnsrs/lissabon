import random
from arkitekt_next import log, register, state
from mikro_next.api.schema import Image
from rekuest_next.declare import declare


@state
class ViabilityState:
    """A state class to store the viability of instances."""

    viability_scores: dict[int, float] = {}


@declare(app="starmist", version="1.0")
class StardistLike:
    def predict_flou2(self, image: Image) -> Image:
        """A method that predicts instances in an image."""
        ...


@declare(app="imswitchlissabon", version="1.0")
class MicroscopeLike:
    def acquireFrame(self) -> Image:
        """A method that acquires an image."""
        ...

    def moveStage(self, axis: str, position: float) -> None:
        """A method that moves the microscope stage to the specified coordinates."""
        ...


@declare(app="test-esp32", version="1.0")
class PumpLike:
    def stepper_move(
        self, steps: int, is_rel: bool, speed_hz: int, acceleration: int
    ) -> None:
        """A method that moves the stepper motor."""
        ...


@register
def team_z_workflow(
    microscope: MicroscopeLike, pump_like: PumpLike, steps: int, state: ViabilityState
) -> None:
    """Acquire an image and predict instances."""
    image = microscope.acquireFrame()

    state.viability_scores[1] = calculate_sphericity(image)

    pump_like.stepper_move(steps=steps, is_rel=False, speed_hz=10000, acceleration=800)
