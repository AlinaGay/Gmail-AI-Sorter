# src/utils/retry.py
import time
from typing import TypeVar, Callable, Optional
from functools import wraps
from google.api_core.exceptions import ResourceExhausted


T = TypeVar('T')


def retry_on_quota(
    max_retries: int = 3,
    wait_time: int = 60,
    logger: Optional[Callable[[str], None]] = None
):
    """Decorator for retrying when quota is exceeded."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            log = logger or print

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ResourceExhausted:
                    if attempt < max_retries - 1:
                        log(f"Quota exceed. Waiting {wait_time}s ..."
                            f"(attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        log("Max retries reached. Aborting.")
                        raise
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper

    return decorator
