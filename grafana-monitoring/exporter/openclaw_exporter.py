import json
import os
import re
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from prometheus_client import REGISTRY, start_http_server
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def normalize_label(value: Any, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    label = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    if not label:
        return fallback
    return label[:64]


def walk_json(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_json(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_json(item)


class ExporterState:
    def __init__(self) -> None:
        self.model_calls: Dict[str, float] = {}
        self.provider_cost: Dict[str, float] = {}
        self.tokens_input = 0.0
        self.tokens_output = 0.0
        self.session_context_bytes = 0.0
        self.cron_jobs_active = 0.0
        self.sessions_active = 0.0
        self.last_poll_ts = 0.0
        self.parse_errors_total = 0.0


class OpenClawCollector:
    def __init__(self) -> None:
        self.sessions_json = Path(os.getenv("SESSIONS_JSON", "/data/sessions/sessions.json"))
        self.poll_seconds = max(_env_int("POLL_SECONDS", 10), 1)
        self.top_models = max(_env_int("TOP_MODELS", 10), 1)
        self.top_providers = max(_env_int("TOP_PROVIDERS", 10), 1)
        self.max_file_mb = max(_env_int("MAX_FILE_MB", 50), 1)

        self._lock = threading.Lock()
        self._state = ExporterState()

    def start(self) -> None:
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def _poll_loop(self) -> None:
        while True:
            self._poll_once()
            time.sleep(self.poll_seconds)

    def _poll_once(self) -> None:
        with self._lock:
            self._state.last_poll_ts = time.time()

        try:
            if not self.sessions_json.exists():
                raise FileNotFoundError(f"missing sessions file: {self.sessions_json}")

            max_bytes = self.max_file_mb * 1024 * 1024
            if self.sessions_json.stat().st_size > max_bytes:
                raise ValueError(f"sessions.json exceeds MAX_FILE_MB={self.max_file_mb}")

            with self.sessions_json.open("r", encoding="utf-8") as fp:
                parsed = json.load(fp)

            new_state = self._parse_sessions(parsed)
            with self._lock:
                new_state.parse_errors_total = self._state.parse_errors_total
                new_state.last_poll_ts = self._state.last_poll_ts
                self._state = new_state
        except Exception:
            with self._lock:
                self._state.parse_errors_total += 1

    def _parse_sessions(self, parsed: Any) -> ExporterState:
        state = ExporterState()

        model_calls = Counter()
        provider_cost = Counter()
        tokens_input = 0.0
        tokens_output = 0.0
        session_context_bytes = 0.0
        cron_jobs_active = 0.0
        sessions_active = 0.0

        if isinstance(parsed, dict):
            if isinstance(parsed.get("sessions"), list):
                sessions_active = float(len(parsed.get("sessions", [])))
            elif isinstance(parsed.get("active_sessions"), (int, float)):
                sessions_active = float(parsed.get("active_sessions", 0))
        elif isinstance(parsed, list):
            sessions_active = float(len(parsed))

        for node in walk_json(parsed):
            if not isinstance(node, dict):
                continue

            model = normalize_label(node.get("model"), "unknown")
            provider = normalize_label(node.get("provider"), "unknown")

            if isinstance(node.get("api_calls"), (int, float)):
                model_calls[model] += float(node["api_calls"])
            elif isinstance(node.get("call_count"), (int, float)):
                model_calls[model] += float(node["call_count"])
            elif isinstance(node.get("requests"), (int, float)):
                model_calls[model] += float(node["requests"])

            if isinstance(node.get("input_tokens"), (int, float)):
                tokens_input += float(node["input_tokens"])
            elif isinstance(node.get("prompt_tokens"), (int, float)):
                tokens_input += float(node["prompt_tokens"])

            if isinstance(node.get("output_tokens"), (int, float)):
                tokens_output += float(node["output_tokens"])
            elif isinstance(node.get("completion_tokens"), (int, float)):
                tokens_output += float(node["completion_tokens"])

            if isinstance(node.get("cost"), (int, float)):
                provider_cost[provider] += float(node["cost"])
            elif isinstance(node.get("cost_dollars"), (int, float)):
                provider_cost[provider] += float(node["cost_dollars"])

            if isinstance(node.get("context_bytes"), (int, float)):
                session_context_bytes += float(node["context_bytes"])

            cron_value = node.get("cron_jobs_active")
            if isinstance(cron_value, bool):
                cron_jobs_active += 1.0 if cron_value else 0.0
            elif isinstance(cron_value, (int, float)):
                cron_jobs_active += float(cron_value)

        if not model_calls:
            model_calls["other"] = 0.0
        if not provider_cost:
            provider_cost["other"] = 0.0

        state.model_calls = self._cap_labels(model_calls, self.top_models)
        state.provider_cost = self._cap_labels(provider_cost, self.top_providers)
        state.tokens_input = tokens_input
        state.tokens_output = tokens_output
        state.session_context_bytes = session_context_bytes
        state.cron_jobs_active = cron_jobs_active
        state.sessions_active = sessions_active
        return state

    @staticmethod
    def _cap_labels(values: Counter, top_n: int) -> Dict[str, float]:
        ranked: List[Tuple[str, float]] = sorted(values.items(), key=lambda item: item[1], reverse=True)
        top = ranked[:top_n]
        overflow = sum(value for _, value in ranked[top_n:])
        capped = {label: float(value) for label, value in top}
        if overflow > 0:
            capped["other"] = capped.get("other", 0.0) + overflow
        return capped

    def collect(self):
        with self._lock:
            state = self._state

            model_counter = CounterMetricFamily(
                "openclaw_api_calls_total",
                "Total API calls grouped by capped model labels",
                labels=["model"],
            )
            for model, value in state.model_calls.items():
                model_counter.add_metric([model], value)

            provider_counter = CounterMetricFamily(
                "openclaw_cost_dollars_total",
                "Total cost in dollars grouped by capped provider labels",
                labels=["provider"],
            )
            for provider, value in state.provider_cost.items():
                provider_counter.add_metric([provider], value)

            tokens_input_counter = CounterMetricFamily(
                "openclaw_tokens_input_total",
                "Total input tokens",
            )
            tokens_input_counter.add_metric([], state.tokens_input)

            tokens_output_counter = CounterMetricFamily(
                "openclaw_tokens_output_total",
                "Total output tokens",
            )
            tokens_output_counter.add_metric([], state.tokens_output)

            context_gauge = GaugeMetricFamily(
                "openclaw_session_context_bytes",
                "Current aggregate session context bytes",
            )
            context_gauge.add_metric([], state.session_context_bytes)

            cron_gauge = GaugeMetricFamily(
                "openclaw_cron_jobs_active",
                "Current active cron jobs",
            )
            cron_gauge.add_metric([], state.cron_jobs_active)

            session_gauge = GaugeMetricFamily(
                "openclaw_sessions_active",
                "Current active sessions",
            )
            session_gauge.add_metric([], state.sessions_active)

            poll_gauge = GaugeMetricFamily(
                "openclaw_exporter_last_poll_timestamp_seconds",
                "Unix timestamp of the last poll attempt",
            )
            poll_gauge.add_metric([], state.last_poll_ts)

            parse_error_counter = CounterMetricFamily(
                "openclaw_exporter_parse_errors_total",
                "Total parse failures while polling sessions.json",
            )
            parse_error_counter.add_metric([], state.parse_errors_total)

        yield model_counter
        yield tokens_input_counter
        yield tokens_output_counter
        yield provider_counter
        yield context_gauge
        yield cron_gauge
        yield session_gauge
        yield poll_gauge
        yield parse_error_counter


def main() -> None:
    collector = OpenClawCollector()
    REGISTRY.register(collector)
    collector.start()
    start_http_server(9091)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
