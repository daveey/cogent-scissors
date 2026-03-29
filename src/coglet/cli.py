"""coglet CLI — run a .cog directory.

Usage:
    coglet path/to/app.cog

A .cog directory contains:
    manifest.toml   — declares the root coglet class and config
    *.py            — Python modules importable by the coglet

manifest.toml format:
    [coglet]
    class = "my_module.MyCoglet"   # dotted path to class within the .cog dir

    [coglet.kwargs]                # optional constructor kwargs
    name = "hello"

    [config]                       # optional CogBase fields
    restart = "on_error"
    max_restarts = 3
    backoff_s = 1.0
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import signal
import sys
import tomllib
from pathlib import Path
from typing import Any

from coglet.handle import CogBase
from coglet.runtime import CogletRuntime
from coglet.trace import CogletTrace


def load_manifest(cog_dir: Path) -> dict[str, Any]:
    """Read and validate manifest.toml from a .cog directory."""
    manifest_path = cog_dir / "manifest.toml"
    if not manifest_path.exists():
        sys.exit(f"error: {manifest_path} not found")

    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    if "coglet" not in manifest or "class" not in manifest["coglet"]:
        sys.exit("error: manifest.toml must have [coglet] with 'class' key")

    return manifest


def resolve_class(dotted: str, cog_dir: Path) -> type:
    """Import a class from a dotted path, with cog_dir on sys.path."""
    parts = dotted.rsplit(".", 1)
    if len(parts) != 2:
        sys.exit(f"error: class must be 'module.ClassName', got '{dotted}'")

    module_name, class_name = parts

    # Add cog_dir to front of sys.path so its modules are importable
    cog_str = str(cog_dir.resolve())
    if cog_str not in sys.path:
        sys.path.insert(0, cog_str)

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        sys.exit(f"error: cannot import module '{module_name}': {e}")

    cls = getattr(module, class_name, None)
    if cls is None:
        sys.exit(f"error: class '{class_name}' not found in '{module_name}'")

    return cls


def build_config(manifest: dict[str, Any], cls: type) -> CogBase:
    """Build a CogBase from manifest data."""
    kwargs = dict(manifest["coglet"].get("kwargs", {}))
    config_section = manifest.get("config", {})

    return CogBase(
        cls=cls,
        kwargs=kwargs,
        restart=config_section.get("restart", "never"),
        max_restarts=config_section.get("max_restarts", 3),
        backoff_s=config_section.get("backoff_s", 1.0),
    )


async def run(cog_dir: Path, trace_path: str | None = None) -> None:
    """Load manifest, create runtime, spawn root coglet, wait for shutdown."""
    manifest = load_manifest(cog_dir)
    cls = resolve_class(manifest["coglet"]["class"], cog_dir)
    config = build_config(manifest, cls)

    trace = CogletTrace(trace_path) if trace_path else None
    runtime = CogletRuntime(trace=trace)

    stop = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    handle = await runtime.run(config)
    print(runtime.tree())

    await stop.wait()

    print("\nshutting down...")
    await runtime.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="coglet",
        description="Run a .cog directory as a coglet tree.",
    )
    parser.add_argument(
        "cog_dir",
        type=Path,
        help="path to a .cog directory containing manifest.toml",
    )
    parser.add_argument(
        "--trace",
        type=str,
        default=None,
        help="path to write jsonl trace output",
    )
    args = parser.parse_args()

    cog_dir = args.cog_dir
    if not cog_dir.is_dir():
        sys.exit(f"error: '{cog_dir}' is not a directory")

    asyncio.run(run(cog_dir, trace_path=args.trace))


if __name__ == "__main__":
    main()
