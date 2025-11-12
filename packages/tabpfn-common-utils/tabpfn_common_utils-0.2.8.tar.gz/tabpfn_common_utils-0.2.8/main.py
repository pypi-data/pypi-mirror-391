import os

from src.tabpfn_common_utils.telemetry.core.events import SessionEvent
from src.tabpfn_common_utils.telemetry.core.service import capture_event

if __name__ == "__main__":
    event = SessionEvent()
    capture_event(event)

    event = SessionEvent()
    capture_event(event)

    pass
