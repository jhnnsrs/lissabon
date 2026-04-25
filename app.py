from arkitekt_next import log, register, state, model, startup, progress
from mikro_next.api.schema import Image, from_array_like
from dataclasses import dataclass, field
from rekuest_next.annotations import Description
from rekuest_next.declare import declare
from deps import (
    Esp32LuckyMicroscope0000Like,
    Position,
    Starmist006Like,
    Imswitchlissabon001Like,
)
from typing import Annotated
from rekuest_next.widgets import withStateChoices
import numpy as np
import time


@state
@dataclass
class State:
    """A state class to store the viability of instances."""

    positions: list[Position] = field(default_factory=list)
    viability_scores: dict[int, float] = field(default_factory=dict)


@startup
def startup_state() -> State:
    """Startup function to initialize the application."""
    log("Application has started.")
    return State(
        positions=[],
    )


@register
def save_position(state: State, microscope: Imswitchlissabon001Like, name: str) -> None:
    """Saves a position to the state."""
    get_position = microscope.getStagePosition(None)
    state.positions.append(
        Position(X=get_position.x, Y=get_position.y, Z=get_position.z, name=name)
    )


@register
def clear_positions(state: State) -> None:
    """Clears all saved positions."""
    state.positions.clear()


@register
def workflow(
    microscope: Imswitchlissabon001Like,
    pump: Esp32LuckyMicroscope0000Like,
    stardist: Starmist006Like,
    state: State,
    washing_time: int = 5,
    n_cycles: int = 3,
    wash_cycles: int = 2,
) -> None:
    # % Bind arkitekt functions
    snapNumpyToFastAPI = microscope.acquireFrame
    homeStage = microscope.homeStageAxis
    setLaserState = microscope.setLaserState
    moveStage = microscope.moveStage
    getPosition = microscope.getStagePosition
    movePump = pump.stepper_move

    # %
    # ─────────────────────────────────────────────
    # COMMON VARIABLES
    # ─────────────────────────────────────────────
    LASER_SYTO9 = (
        "LED"  # Green channel — live bacteria (adjust name to match your setup)
    )
    LASER_PI = "LED"  # Red channel   — dead bacteria  (adjust name to match your setup)

    WASH_CYCLES = 2  # Number of PBS wash cycles per staining round
    INTERVAL_TIME = 5  # Seconds between timelapse cycles
    N_CYCLES = 3  # Total number of staining cycles

    Z_UP = 43
    Z_DOWN = -8500
    Z_FOCUS = -90  # Optional autofocus target (adjust based on your sample)

    POS_WASH = {"X": 117000, "Y": 30000}
    POS_STAINING = {"X": 117000, "Y": 30000}
    POS_MEDIUM = {"X": 117000, "Y": 30000}
    POS_WASTE = {"X": 117000, "Y": 49000}
    POS_INJ = {"X": 125500, "Y": 38000}

    PUMP_STEPS = 5000
    PUMP_SPEED = 10000
    PUMP_ACCEL = 100000

    saved_ROI_positions = [
        {"X": 88890, "Y": 29500, "Z": 0, "name": "ROI1"},
        {"X": 87390, "Y": 31230, "Z": 0, "name": "ROI2"},
        {"X": 88309, "Y": 29333, "Z": 0, "name": "ROI3"},
        {"X": 90000, "Y": 34090, "Z": 0, "name": "ROI4"},
    ]  #

    # %
    # ─────────────────────────────────────────────
    # LOW-LEVEL HELPERS
    # ─────────────────────────────────────────────

    def move_down():
        """Lower the stage to the pipetting Z position."""
        log(f"Moving Z down → {Z_DOWN}")
        moveStage(
            None,
            axis="Z",
            distance=Z_DOWN + np.random.randint(-2, 3),
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )
        # time.sleep(2)

    def move_up():
        """Raise the stage to the safe travel Z position."""
        log(f"Moving Z up → {Z_UP}")
        moveStage(
            None,
            axis="Z",
            distance=Z_UP + np.random.randint(-2, 3),
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )

    # time.sleep(2)

    def _move_xy(pos: dict):
        """Move to an XY position dict with keys 'X' and 'Y'."""
        moveStage(
            None,
            axis="X",
            distance=pos["X"],
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )
        moveStage(
            None,
            axis="Y",
            distance=pos["Y"],
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )

    def move_to_wash():
        log("Moving to WASH station")
        _move_xy(POS_WASH)

    def move_to_staining():
        log("Moving to STAINING station")
        _move_xy(POS_STAINING)

    def move_to_media():
        log("Moving to MEDIA station")
        _move_xy(POS_MEDIUM)

    def move_to_waste():
        log("Moving to WASTE station")
        _move_xy(POS_WASTE)

    def move_to_inj():
        log("Moving to INJECTION station")
        _move_xy(POS_INJ)

    def pump_in():
        """Aspirate liquid into the tubing."""
        log("Pumping IN  (aspirate)")
        try:
            movePump(
                steps=PUMP_STEPS,
                isRel=False,
                speed_hz=PUMP_SPEED,
                acceleration=PUMP_ACCEL,
            )
        except Exception as e:
            print("Error during pump IN:", e)
        time.sleep(2)

    def pump_out():
        """Dispense liquid from the tubing."""
        log("Pumping OUT (dispense)")
        try:
            movePump(
                steps=-PUMP_STEPS,
                isRel=False,
                speed_hz=PUMP_SPEED,
                acceleration=PUMP_ACCEL,
            )
        except Exception as e:
            print("Error during pump OUT:", e)
        time.sleep(2)

    # %
    # ─────────────────────────────────────────────
    # ROI MANAGEMENT
    # ─────────────────────────────────────────────

    # %
    # ─────────────────────────────────────────────
    # HIGH-LEVEL PROTOCOL STEPS
    # ─────────────────────────────────────────────

    def remove_media():
        """Remove growth media from the sample chamber."""
        log("── remove_media ──")
        move_up()
        move_to_inj()
        move_down()
        pump_in()  # Aspirate media from chamber
        move_up()
        move_to_waste()
        move_down()
        pump_out()  # Dispense to waste
        move_up()

    def run_staining_cycle():
        """
        Full staining protocol:
        1. PBS rinse
        2. Apply staining mix (SYTO9 + PI)
        3. Incubate
        4. Remove staining mix
        """
        print("── run_staining_cycle ──")

        # --- PBS rinse ---
        move_up()
        move_to_wash()
        move_down()
        pump_in()  # Aspirate PBS
        move_up()
        move_to_inj()
        move_down()
        pump_out()  # Dispense PBS into chamber
        time.sleep(5)  # Short incubation with PBS

        pump_in()  # Re-aspirate PBS from chamber
        move_up()
        move_to_waste()
        move_down()
        pump_out()  # Dispose PBS waste
        move_down()
        move_up()

        # --- Apply staining mix ---
        move_to_staining()
        move_down()
        pump_in()  # Aspirate staining mix
        move_up()
        move_to_inj()
        move_down()
        pump_out()  # Dispense staining mix into chamber
        move_up()
        time.sleep(10)  # Staining incubation (adjust to 5-10 min as needed)

        # --- Remove staining mix ---
        move_to_inj()
        move_down()
        pump_in()  # Aspirate staining mix from chamber
        move_up()
        move_to_waste()
        move_down()
        pump_out()  # Dispose staining waste
        move_up()

    def wash_cycle(n: int = WASH_CYCLES):
        """Perform n PBS wash cycles to remove residual dye."""
        log(f"── wash_cycle × {n} ──")
        for i in range(n):
            log(f"  Wash {i + 1}/{n}")
            move_up()
            move_to_wash()
            move_down()
            pump_in()  # Aspirate PBS
            move_up()
            move_to_inj()
            move_down()
            pump_out()  # Dispense PBS into chamber
            time.sleep(5)  # Brief wash incubation
            move_down()
            pump_in()  # Re-aspirate PBS
            move_up()
            move_to_waste()
            move_down()
            pump_out()  # Dispose waste
        move_up()

    def add_media():
        """Replenish growth media after staining/washing."""
        print("── add_media ──")
        move_up()
        move_to_media()
        move_down()
        pump_in()  # Aspirate fresh media
        move_up()
        move_to_inj()
        move_down()
        pump_out()  # Dispense media into chamber
        move_up()

    # %
    # ─────────────────────────────────────────────
    # IMAGING
    # ─────────────────────────────────────────────

    def snap_channel(laser_name: str, value: int = 1023):
        """Activate a laser, snap an image, then deactivate the laser."""
        setLaserState(laserName=laser_name, isActive=True, value=value)
        img = snapNumpyToFastAPI(2)
        print(img)
        stardist.predict_flou2(img)
        setLaserState(laserName=laser_name, isActive=False, value=0)
        return img

    def image_roi(roi: dict, cycle_index: int):
        """
        Move to an ROI and acquire both SYTO9 (live) and PI (dead) channels.
        Returns a dict with the two images and metadata.
        """
        print(f"  Imaging ROI '{roi['name']}' — cycle {cycle_index + 1}")

        # Navigate to ROI
        moveStage(
            None,
            axis="X",
            distance=roi["X"],
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )
        moveStage(
            None,
            axis="Z",
            distance=roi["Z"],
            is_absolute=True,
            is_blocking=True,
            speed=20000,
        )
        moveStage(
            None,
            axis="Y",
            distance=roi["Y"],
            is_absolute=True,
            is_blocking=False,
            speed=20000,
        )

        # Optional autofocus placeholder:
        # autofocus.call()

        syto9_img = snap_channel(LASER_SYTO9)
        pi_img = snap_channel(LASER_PI)

        print(f"  ✓ Captured SYTO9 + PI images for {roi['name']}")
        return {
            "roi_name": roi["name"],
            "cycle_index": cycle_index + 1,
            "syto9_img": syto9_img,
            "pi_img": pi_img,
        }

    # %
    # ─────────────────────────────────────────────
    # SAVE ROIs  (run these cells interactively
    #             after positioning the stage)
    # ─────────────────────────────────────────────

    """
    save_current_position(name="ROI1")
    save_current_position(name="ROI2")
    save_current_position(name="ROI3")
    save_current_position(name="ROI4")
    """

    # %%
    # ─────────────────────────────────────────────
    # MAIN EXPERIMENT LOOP
    # ─────────────────────────────────────────────

    results = []

    for i, cycle_index in enumerate(range(N_CYCLES)):
        progress(
            int(i / (N_CYCLES - 1) * 100),
            f"Starting cycle {cycle_index + 1} of {N_CYCLES}...",
        )

        # 5. Image every saved ROI
        for roi in saved_ROI_positions:
            print(f"\nImaging ROI '{roi['name']}' (Cycle {cycle_index + 1})")
            result = image_roi(roi, cycle_index)
            results.append(result)
            time.sleep(2)

        print(f"\n{'=' * 50}")
        print(f"CYCLE {cycle_index + 1} / {N_CYCLES}")
        print(f"{'=' * 50}")

        # 1. Remove growth media
        remove_media()

        # 2. Stain with SYTO9 + PI
        run_staining_cycle()

        # 3. Wash out unbound dye
        wash_cycle(n=WASH_CYCLES)

        # 4. Replenish growth media
        add_media()

        # 6. Return home and wait for next cycle
        move_up()
        log(f"Waiting {INTERVAL_TIME}s until next cycle...")
        time.sleep(INTERVAL_TIME)

    log("\nExperiment complete.")
    log(f"Total image sets collected: {len(results)}")
    for r in results:
        log(f"  Cycle {r['cycle_index']} | {r['roi_name']}")


@register
def segment_image(image: Image) -> Image:
    """Example function to segment an image using a dummy threshold."""
    # Convert to numpy array, apply simple threshold, and convert back to Image
    img_array = image.data
    segmented_array = (img_array > 0.5).astype(np.uint8)  # Dummy segmentation
    segmented_image = from_array_like(segmented_array, name=image.name + "_segmented")
    return segmented_image
