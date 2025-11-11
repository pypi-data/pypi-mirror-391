from typing import Literal, cast

RecordState = Literal[0, 1, 2]

RECORD_STATE_VALUES: set[RecordState] = { 0, 1, 2,  }

def check_record_state(value: int) -> RecordState:
    if value in RECORD_STATE_VALUES:
        return cast(RecordState, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RECORD_STATE_VALUES!r}")
