from __future__ import annotations

import asyncio
import time
from uuid import uuid4

from .audio.corpus import load_corpus
from .audio.generate import AudioClip, generate_audio
from .config import RunConfig
from .metrics import RequestSample, summarize
from .providers.base import ProviderAdapter, RequestContext
from .providers.generic_http import GenericHTTPAdapter
from .providers.messages_http import MessagesHTTPAdapter
from .providers.mock import MockProviderAdapter
from .reports import RunResult
from .scenario import ScenarioPicker
from .thresholds import evaluate_thresholds
from .validation import validate_response


def make_provider(config: RunConfig) -> ProviderAdapter:
    if config.provider.type == "mock":
        return MockProviderAdapter(config.provider, seed=config.run.seed)
    if config.provider.type == "generic_http":
        return GenericHTTPAdapter(config.provider)
    if config.provider.type == "messages_http":
        return MessagesHTTPAdapter(config.provider)
    raise ValueError(f"Unsupported provider type: {config.provider.type}")


async def run_load_test_async(config: RunConfig) -> RunResult:
    """Run a load test asynchronously."""
    provider = make_provider(config)
    picker = ScenarioPicker(config.scenarios, config.run.seed)
    samples: list[RequestSample] = []
    start = time.perf_counter()
    stop_at = start + config.run.duration_seconds
    sem = asyncio.Semaphore(config.load.concurrency)
    tasks: set[asyncio.Task[None]] = set()

    async def one_request(index: int) -> None:
        async with sem:
            scenario = picker.pick()
            audio = _audio_for_scenario(config, scenario.audio, index)
            measured = (time.perf_counter() - start) >= config.run.warmup_seconds
            context = RequestContext(str(uuid4()), scenario.name, audio, scenario.metadata)
            response = await provider.send(context)
            validation_errors = validate_response(response, config.validation)
            ok = response.ok and not validation_errors
            error = response.error or ("; ".join(validation_errors) if validation_errors else None)
            samples.append(RequestSample(context.request_id, scenario.name, response.elapsed_ms, response.status_code, ok, error, measured, response.bytes_sent, response.bytes_received))

    index = 0
    while time.perf_counter() < stop_at:
        task = asyncio.create_task(one_request(index))
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        index += 1
        if config.load.mode == "arrival_rate":
            await asyncio.sleep(1.0 / max(config.load.rate_per_second, 0.001))
        else:
            await asyncio.sleep(0)
            if len(tasks) >= config.load.concurrency:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    if tasks:
        await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start
    summary = summarize(samples, duration_seconds=max(0.001, elapsed - config.run.warmup_seconds))
    thresholds = evaluate_thresholds(summary, config.thresholds)
    return RunResult(summary, samples, thresholds, {"name": config.run.name, "duration_seconds": elapsed})


def run_load_test(config: RunConfig) -> RunResult:
    return asyncio.run(run_load_test_async(config))


def _audio_for_scenario(config: RunConfig, audio_config, index: int) -> AudioClip:
    if audio_config.kind == "corpus":
        clips = load_corpus(audio_config)
        return clips[index % len(clips)]
    return generate_audio(audio_config, seed=config.run.seed + index)
