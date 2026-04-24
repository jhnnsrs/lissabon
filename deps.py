from typing import Dict, Optional, Protocol, Tuple
from arkitekt_next import declare, model
from mikro_next.api.schema import Image


@model
class Position:
    x: float
    y: float
    z: float


@declare(app="test-esp32")
class Esp32LuckyMicroscope0000Like(Protocol):
    def calculator(self, a: float, b: float, operation: str) -> Tuple[float, str]:
        """Performs arithmetic on two numbers"""
        ...

    def get_device_info(self) -> Tuple[str, int, int]:
        """Returns ESP32 hardware information"""
        ...

    def stepper_move(
        self, steps: int, isRel: Optional[bool], speed_hz: int, acceleration: int
    ) -> Tuple[int, int, bool]:
        """Move the stepper motor. Positive steps → forward, negative → backward. Use isRel=true to target an exact position, 'relative' for an offset."""
        ...

    def stepper_stop(self, emergency: bool) -> Tuple[int, bool]:
        """Stop the stepper motor. emergency=false ramps down smoothly; emergency=true halts immediately."""
        ...

    def toggle_led(self) -> Tuple[int, bool]:
        """Toggles the built-in LED"""
        ...


@declare(app="starmist")
class Starmist006Like(Protocol):
    def predict_stardist_he(self, image: Image) -> Image:
        """Segments Cells using the stardist he pretrained model"""
        ...

    def predict_flou2(self, image: Image) -> Image:
        """Segments Cells using the stardist flou2 pretrained model"""
        ...


@declare(app="imswitchlissabon")
class Imswitchlissabon001Like(Protocol):
    def moveToSampleLoadingPosition(
        self, speed: Optional[int], is_blocking: Optional[bool]
    ) -> None:
        """Move to sample loading position."""
        ...

    def runTileScan(
        self,
        center_x_micrometer: Optional[float],
        center_y_micrometer: Optional[float],
        range_x_micrometer: Optional[int],
        range_y_micrometer: Optional[int],
        step_x_micrometer: Optional[float],
        step_y_micrometer: Optional[float],
        overlap_percent: Optional[float],
        illumination_channel: Optional[str],
        illumination_intensity: Optional[int],
        exposure_time: Optional[float],
        gain: Optional[float],
        speed: Optional[int],
        positionerName: Optional[str],
        performAutofocus: Optional[bool],
        autofocus_range: Optional[int],
        autofocus_resolution: Optional[int],
        autofocus_illumination_channel: Optional[str],
        objective_id: Optional[int],
        t_settle: Optional[float],
    ) -> Image:
        """Runs a tile scan by moving the specified positioner in a grid pattern centered
        at the given coordinates, capturing images at each position with specified
        illumination and camera settings, and yielding the images with appropriate
        affine transformations for stitching.

        The step size is automatically calculated based on the current objective's
        field of view and the specified overlap percentage, unless explicitly provided."""
        ...

    def goToPosition(
        self,
        x_micrometer: float,
        y_micrometer: float,
        positionerName: Optional[str],
        speed: Optional[int],
        is_blocking: Optional[bool],
        t_settle: Optional[float],
    ) -> None:
        """Moves the specified positioner (or the first available one) to the given
        X and Y coordinates in micrometers."""
        ...

    def acquireFrame(self, frameSync: Optional[int]) -> Image:
        """Acquire a single frame from the detector."""
        ...

    def getStagePosition(self, positionerName: Optional[str]) -> Position:
        """Get current stage position."""
        ...

    def homeStageAxis(
        self,
        positionerName: Optional[str],
        axis: Optional[str],
        is_blocking: Optional[bool],
    ) -> None:
        """Home stage axis."""
        ...

    def setLaserState(
        self, laserName: str, isActive: bool, value: Optional[int]
    ) -> None:
        """Set laser state."""
        ...

    def moveStage(
        self,
        positionerName: Optional[str],
        axis: Optional[str],
        distance: Optional[int],
        is_absolute: Optional[bool],
        is_blocking: Optional[bool],
        speed: Optional[int],
    ) -> None:
        """Move stage."""
        ...
