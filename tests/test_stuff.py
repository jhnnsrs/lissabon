from app import workflow, State
import pytest
from .testing_devices import FakeEsp32, FakeStardist, FakeFrame


def test_workflow():
    fake_esp32 = FakeEsp32()
    fake_stardist = FakeStardist()
    fake_frame = FakeFrame()

    state = State()

    result = workflow(fake_frame, fake_esp32, fake_stardist, state)
