# app/core/circuit_breaker.py
import logging
import time
from collections.abc import Callable
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_duration: int = 30,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed < self.timeout_duration:
                logger.warning("Circuit breaker is OPEN – skipping call")
                raise Exception("Circuit breaker is OPEN")
            self.state = CircuitState.HALF_OPEN
            logger.info("Circuit breaker transitioning to HALF_OPEN")

        try:
            result = await func(*args, **kwargs)
            self._reset()
            return result
        except self.expected_exception as e:
            self._record_failure()
            raise e
        except Exception as e:
            logger.warning(f"Unexpected error in circuit breaker: {e}")
            raise

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.debug(f"Failure count: {self.failure_count}/{self.failure_threshold}")
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker state set to OPEN")

    def _reset(self):
        if self.state != CircuitState.CLOSED:
            logger.info("Circuit breaker reset to CLOSED")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def reset(self):
        """Manually reset breaker (optional external use)"""
        logger.info("Circuit breaker manually reset")
        self._reset()

    def get_state(self) -> str:
        return self.state.value
