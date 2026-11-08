"""Cost guards for public deployments: per-session token meter and a shared daily run cap."""
import datetime
import threading


class BudgetExceeded(RuntimeError):
    pass


class Meter:
    """Counts Claude calls/tokens for one session and refuses calls past a token limit."""

    def __init__(self, token_limit: int = 80_000):
        self.token_limit, self.tokens_in, self.tokens_out, self.calls = token_limit, 0, 0, 0

    @property
    def used(self) -> int:
        return self.tokens_in + self.tokens_out

    def check(self) -> None:
        if self.used >= self.token_limit:
            raise BudgetExceeded('Session token budget reached.')

    def add(self, tokens_in: int, tokens_out: int) -> None:
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        self.calls += 1

    def snapshot(self) -> dict:
        return {'calls': self.calls, 'input_tokens': self.tokens_in, 'output_tokens': self.tokens_out}


class DailyCap:
    """Process-wide cap on live runs per UTC day (reset on restart; pair with provider spend limits)."""

    def __init__(self, max_runs: int = 25):
        self.max_runs, self._day, self._count, self._lock = max_runs, None, 0, threading.Lock()

    def try_acquire(self) -> bool:
        today = datetime.datetime.now(datetime.timezone.utc).date()
        with self._lock:
            if self._day != today:
                self._day, self._count = today, 0
            if self._count >= self.max_runs:
                return False
            self._count += 1
            return True
