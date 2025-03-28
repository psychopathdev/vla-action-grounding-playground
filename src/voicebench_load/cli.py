from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from rich.console import Console

from .audio.generate import generate_audio
from .audio.inspect import inspect_audio
from .config import AudioSourceConfig, ConfigError, load_config
from .reports import RunResult, render_report
from .runner import run_load_test
from .server.mock_api import run_mock_server

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="voicebench-load", description="语音/音频模型接口负载测试工具")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="写入一个示例配置")
    init.add_argument("path", nargs="?", default="voicebench.yaml")
    validate = sub.add_parser("validate", help="校验配置")
    validate.add_argument("config")
    run = sub.add_parser("run", help="执行负载测试")
    run.add_argument("config")
    gen = sub.add_parser("generate-audio", help="生成合成 WAV")
    gen.add_argument("output")
    gen.add_argument("--duration", type=float, default=1.0)
    gen.add_argument("--sample-rate", type=int, default=16000)
    gen.add_argument("--waveform", default="speech_like")
    inspect = sub.add_parser("inspect-audio", help="检查 WAV 信息")
    inspect.add_argument("path")
    report = sub.add_parser("report", help="从 results.json 重新生成简要输出")
    report.add_argument("results_json")
    mock = sub.add_parser("mock-server", help="启动本地 mock HTTP 服务")
    mock.add_argument("--host", default="127.0.0.1")
    mock.add_argument("--port", type=int, default=8765)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            return _cmd_init(args.path)
        if args.command == "validate":
            cfg = load_config(args.config)
            console.print(f"[green]配置有效[/green]: {cfg.run.name}")
            return 0
        if args.command == "run":
            cfg = load_config(args.config)
            result = run_load_test(cfg)
            paths = render_report(result, cfg.reports.formats, cfg.reports.output_dir)
            console.print(f"[green]完成[/green] 请求={result.summary.measured_requests} 错误率={result.summary.error_rate:.2%}")
            for path in paths:
                console.print(f"写入 {path}")
            return 0 if result.thresholds.passed else 1
        if args.command == "generate-audio":
            clip = generate_audio(AudioSourceConfig(waveform=args.waveform, duration_seconds=args.duration, sample_rate=args.sample_rate))
            Path(args.output).write_bytes(clip.data)
            console.print(f"写入 {args.output} ({clip.size_bytes} bytes)")
            return 0
        if args.command == "inspect-audio":
            console.print_json(json.dumps(asdict(inspect_audio(args.path)), ensure_ascii=False))
            return 0
        if args.command == "report":
            data = json.loads(Path(args.results_json).read_text(encoding="utf-8"))
            console.print_json(json.dumps(data.get("summary", data), ensure_ascii=False))
            return 0
        if args.command == "mock-server":
            run_mock_server(args.host, args.port)
            return 0
    except ConfigError as exc:
        console.print(f"[red]配置错误[/red]: {exc}")
        return 2
    except KeyboardInterrupt:
        console.print("\n[yellow]已中断[/yellow]")
        return 130
    return 2


def _cmd_init(path: str) -> int:
    src = Path(__file__).resolve().parents[2] / "examples" / "generic-json-base64.yaml"
    if src.exists():
        content = src.read_text(encoding="utf-8")
    else:
        content = "run:\n  name: demo\nscenarios:\n  - name: demo\n"
    Path(path).write_text(content, encoding="utf-8")
    console.print(f"写入示例配置 {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
