import os

from src.tabpfn_common_utils.telemetry.core.events import SessionEvent
from src.tabpfn_common_utils.telemetry.core.service import capture_event

if __name__ == "__main__":
    import os

    os.environ["TABPFN_TELEMETRY_SOURCE"] = "test"

    from src.tabpfn_common_utils.telemetry.core.service import ProductTelemetry

    # Initialize telemetry with a larger queue size for testing
    # Since ProductTelemetry is a singleton, this instance will be reused
    large_queue_size = 100
    large_flush_at = 50
    telemetry = ProductTelemetry(max_queue_size=large_queue_size, flush_at=large_flush_at)

    event = SessionEvent()
    capture_event(event, max_queue_size=large_queue_size, flush_at=large_flush_at)
    
    event = SessionEvent()
    capture_event(event, max_queue_size=large_queue_size, flush_at=large_flush_at)

    from src.tabpfn_common_utils.telemetry.core.events import (
        PingEvent,
        FitEvent,
        PredictEvent,
    )
    from src.tabpfn_common_utils.telemetry.interactive.flows import (
        ping,
        capture_session,
    )

    # Create and capture Ping event
    ping_event = PingEvent()
    capture_event(ping_event, max_queue_size=large_queue_size, flush_at=large_flush_at)

    # Create and capture FitCalled event
    import time
    for _ in range(20):
        fit_event = FitEvent(task="classification")
        capture_event(fit_event, max_queue_size=large_queue_size, flush_at=large_flush_at)

        # Create and capture PredictCalled event
        predict_event = PredictEvent(task="classification")
        capture_event(predict_event, max_queue_size=large_queue_size, flush_at=large_flush_at)

        time.sleep(0.1)


    # Call ping
    ping()

    # Capture session (may perform additional session logic)
    capture_session()
    
    pass
