import asyncio

import pytest

from app.core.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreaker:

    def test_initialization(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker(failure_threshold=3, timeout_duration=30)
        assert cb.failure_threshold == 3
        assert cb.timeout_duration == 30
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful function execution"""
        cb = CircuitBreaker()

        async def successful_function():
            return "success"

        result = await cb.call(successful_function)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_failure_accumulation(self):
        """Test that failures accumulate correctly"""
        cb = CircuitBreaker(failure_threshold=3)

        async def failing_function():
            raise Exception("Test failure")

        for i in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_function)
            assert cb.state == CircuitState.CLOSED
            assert cb.failure_count == i + 1

        with pytest.raises(Exception):
            await cb.call(failing_function)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_circuit_blocks_calls(self):
        """Test that open circuit blocks all calls"""
        cb = CircuitBreaker(failure_threshold=1)

        async def failing_function():
            raise Exception("Test failure")

        with pytest.raises(Exception):
            await cb.call(failing_function)
        assert cb.state == CircuitState.OPEN

        async def any_function():
            return "should not execute"

        with pytest.raises(Exception) as exc_info:
            await cb.call(any_function)
        assert "Circuit breaker is OPEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_half_open_success_recovery(self):
        """Test recovery from HALF_OPEN to CLOSED on success"""
        cb = CircuitBreaker(failure_threshold=1, timeout_duration=0.1)

        async def failing_function():
            raise Exception("Test failure")

        async def successful_function():
            return "success"

        with pytest.raises(Exception):
            await cb.call(failing_function)
        assert cb.state == CircuitState.OPEN

        await asyncio.sleep(0.2)

        result = await cb.call(successful_function)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_reopen(self):
        """Test HALF_OPEN back to OPEN on failure"""
        cb = CircuitBreaker(failure_threshold=1, timeout_duration=0.1)

        async def failing_function():
            raise Exception("Test failure")

        # Open the circuit
        with pytest.raises(Exception):
            await cb.call(failing_function)
        assert cb.state == CircuitState.OPEN

        await asyncio.sleep(0.2)

        with pytest.raises(Exception):
            await cb.call(failing_function)
        assert cb.state == CircuitState.OPEN

    def test_manual_reset(self):
        """Test manual circuit breaker reset"""
        cb = CircuitBreaker()
        cb.failure_count = 5
        cb.state = CircuitState.OPEN

        cb.reset()

        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_get_state(self):
        """Test get_state method returns correct string"""
        cb = CircuitBreaker()
        assert cb.get_state() == "CLOSED"

        cb.state = CircuitState.OPEN
        assert cb.get_state() == "OPEN"

        cb.state = CircuitState.HALF_OPEN
        assert cb.get_state() == "HALF_OPEN"

    @pytest.mark.asyncio
    async def test_unexpected_exception_ignored(self):
        """Test that unexpected exceptions don't affect circuit state"""
        cb = CircuitBreaker(expected_exception=ValueError)

        async def runtime_error_function():
            raise RuntimeError("Unexpected error")

        with pytest.raises(RuntimeError):
            await cb.call(runtime_error_function)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
