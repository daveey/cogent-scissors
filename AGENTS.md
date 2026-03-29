# AGENTS.md

Documentation for AI agents working with the coglet codebase.

## Framework Overview

Coglet is a framework for fractal asynchronous control of distributed agent systems.
Every Coglet is simultaneously a **COG** (supervisor) and a **LET** (executor),
forming a recursive temporal hierarchy with the same protocol at every level.

## Source Layout

```
src/coglet/
├── __init__.py        # Package exports (all public types)
├── coglet.py          # Base Coglet class + @listen/@enact decorators
├── channel.py         # Channel, ChannelSubscription, ChannelBus (async pub/sub)
├���─ handle.py          # Command, CogBase, CogletHandle (child references)
├── runtime.py         # CogletRuntime (spawn, shutdown, tree, restart, tracing)
├── lifelet.py         # LifeLet mixin (on_start/on_stop lifecycle hooks)
├── ticklet.py         # TickLet mixin + @every decorator (periodic execution)
├── proglet.py         # ProgLet mixin (unified program table with pluggable executors)
├── llm_executor.py   # LLMExecutor (multi-turn LLM conversations with tool use)
├── gitlet.py          # GitLet mixin (repo-as-policy, git patches)
├── loglet.py          # LogLet mixin (separate log channel with levels)
├── mullet.py          # MulLet mixin (fan-out N children, scatter/gather)
├── suppresslet.py     # SuppressLet mixin (gate channels/commands)
├── weblet.py          # WebLet mixin + CogWebRegistry (graph visualization)
└── trace.py           # CogletTrace (jsonl event recording)

src/cogweb/            # CogWeb graph visualization UI
├── __init__.py
└── ui/
    ├── __init__.py
    ├── server.py      # CogWebUI (FastAPI + WebSocket server)
    └── static/
        └── index.html # Interactive SVG graph frontend

cogames/               # CvC player: Coach, PlayerCoglet, PolicyCoglet
tests/                 # 200 tests across unit + integration
docs/                  # Architecture and design docs
```

## Component Reference

### coglet.py — Base Coglet Class

The universal primitive. Every coglet has two interfaces:

**LET interface** (receiving and producing data):
- `@listen(channel)` — decorator, registers a method as data-plane handler
- `@enact(command_type)` — decorator, registers a method as control-plane handler
- `transmit(channel, data)` — async, pushes data to all channel subscribers
- `transmit_sync(channel, data)` — non-async variant

**COG interface** (managing children):
- `create(base) -> CogletHandle` — spawn a child coglet from a CogBase
- `observe(handle, channel)` — async iterator over child's channel output
- `guide(handle, command)` — fire-and-forget command to child's @enact handlers

**Supervision**:
- `on_child_error(handle, error) -> str` — returns "restart", "stop", or "escalate"

Handler discovery uses `__init_subclass__` to scan the MRO for decorated methods.
Both sync and async handlers are supported (checked via `hasattr(result, "__await__")`).

### channel.py — Async Pub/Sub

- `Channel` — single async queue, supports `put`/`get`/`async for`
- `ChannelSubscription` — independent subscriber with its own queue
- `ChannelBus` — per-coglet registry. `transmit()` pushes to all subscribers on a
  channel. Each `subscribe()` creates an independent queue (no message loss from
  slow consumers). Channels are created on demand via `_ensure_channel()`.

**Important**: subscribers must be created *before* transmit to receive data.
There is no replay/history — missed messages are gone.

### handle.py — Child References

- `Command(type, data)` — control-plane message sent via `guide()`
- `CogBase(cls, kwargs, restart, max_restarts, backoff_s)` — bundle of assets for
  creating a Coglet. `restart` can be `"never"` (default), `"on_error"`, or `"always"`.

- `CogletHandle` — opaque reference to a running child. Exposes `observe(channel)`
  and `guide(command)`. The parent never accesses the child directly.

### runtime.py — Lifecycle Management

`CogletRuntime` manages the coglet tree:

- `spawn(base, parent)` — instantiate from CogBase, call on_start, start tickers, return handle
- `run(base)` — spawn a root coglet (no parent)
- `shutdown()` — stop all coglets in reverse spawn order (LIFO)
- `tree()` — ASCII visualization of the live supervision hierarchy
- `handle_child_error(handle, error)` — consult parent's on_child_error, apply restart policy

**Tracing**: pass `CogletRuntime(trace=CogletTrace("path.jsonl"))` to record all
transmit/enact events. The runtime wraps each coglet's methods transparently.

**Restart**: on child error, the runtime asks the parent, then applies exponential
backoff (`backoff_s * 2^attempt`). The CogletHandle is preserved — it points to the
new instance after restart.

### Mixins

All mixins use cooperative multiple inheritance (`super().__init__(**kwargs)`).
Order in the class definition matters (MRO). Mixins that override Coglet methods
(like SuppressLet) must appear before Coglet in the MRO.

#### lifelet.py — Lifecycle Hooks
- `on_start()` — called by runtime after spawn. Raising aborts.
- `on_stop()` — called by runtime during shutdown.

#### ticklet.py — Periodic Execution
- `@every(interval, unit)` — decorator. Units: `"s"`, `"m"`, `"ticks"`
- Time-based tickers run as asyncio tasks. Tick-based require manual `self.tick()`.
- `on_ticker_error(method_name, error)` — called when a ticker raises. Override to
  customize. Default: log via LogLet if available. `CancelledError` is re-raised.

#### proglet.py — Unified Program Table
- `self.programs: dict[str, Program]` — named programs with pluggable executors
- `Program(executor, fn, system, tools, parser, config)` — unit of computation
- `Executor` protocol — pluggable backend (`CodeExecutor`, `LLMExecutor`)
- `@enact("register")` — register/replace programs at runtime via `guide()`
- `@enact("executor")` — register custom executors at runtime
- `await self.invoke(name, context)` — run a program by name

#### llm_executor.py — LLM Conversations
- `LLMExecutor(client)` — executor for multi-turn LLM conversations
- Supports tool use — programs can invoke other programs as LLM tools
- Supports callable system prompts — `system(context)` for dynamic prompts
- Configurable via `Program.config`: model, temperature, max_tokens, max_turns

#### gitlet.py — Repo-as-Policy
- `repo_path` — defaults to cwd
- `_git(*args)` — async subprocess wrapper
- `@enact("commit")` — apply a git patch as a commit
- `revert(n)`, `branch(name)`, `checkout(ref)` — git operations

#### loglet.py — Log Stream
- `log(level, data)` — transmits on `"log"` channel if level passes filter
- `@enact("log_level")` — change verbosity at runtime via `guide()`
- Levels: `debug`, `info`, `warn`, `error`

#### mullet.py — Fan-Out N Children
- `create_mul(n, config)` — spawn N identical children
- `map(event)` — route event to children (default: broadcast). Override for custom routing.
- `reduce(results)` — aggregate outputs (default: list). Override for custom aggregation.
- `scatter(channel, event)` — distribute via map()
- `gather(channel)` — collect one result from each child, then reduce()
- `guide_mapped(command)` — send same command to all children

#### suppresslet.py — Output Gating
- `@enact("suppress")` — suppress channels and/or commands: `{"channels": [...], "commands": [...]}`
- `@enact("unsuppress")` — restore suppressed channels/commands
- Overrides `transmit()` and `_dispatch_enact()` to gate output
- Meta-commands (suppress/unsuppress) always pass through
- Must appear before Coglet in MRO: `class MyLET(SuppressLet, Coglet): ...`

#### weblet.py — CogWeb UI Registration
- `WebLet` mixin — registers coglet with a `CogWebRegistry` for graph visualization
- `CogWebRegistry` — holds live coglet references, builds snapshots on demand
- `CogWebNode` — dataclass for one node's metadata (class, mixins, channels, children, config, status)
- `CogWebSnapshot` — full graph (nodes + edges), serializable via `to_dict()`
- `@enact("cogweb_status")` — lets COG or UI set node status ("running", "error", "stopped")
- **Inert without registry** — if `cogweb` kwarg is not passed, the mixin is a no-op
- **Live references** — registry stores coglet instances, not snapshots. `snapshot()` always
  reflects current state (children, channels, etc.)
- Cooperates with `LifeLet`: auto-registers in `on_start()`, deregisters in `on_stop()`
- Records parent→child control edges when both parent and child have WebLet

```python
from coglet import Coglet, CogletConfig, CogletRuntime, LifeLet
from coglet.weblet import CogWebRegistry, WebLet

class MyNode(Coglet, WebLet, LifeLet):
    async def on_start(self):
        await super().on_start()
        await self.create(CogletConfig(cls=Worker, kwargs={"cogweb": self._cogweb}))

registry = CogWebRegistry()
rt = CogletRuntime()
await rt.spawn(CogletConfig(cls=MyNode, kwargs={"cogweb": registry}))
snap = registry.snapshot()
snap.to_dict()  # {"nodes": {...}, "edges": [...]}
```

### CogWeb UI — Graph Visualization Server

`CogWebUI` wraps a `CogWebRegistry` with an HTTP/WebSocket server:

```python
from cogweb.ui import CogWebUI

ui = CogWebUI(registry, host="0.0.0.0", port=8787)
await ui.start()   # non-blocking background server
# Open http://localhost:8787
await ui.stop()
```

**Endpoints**:
- `GET /` — serves the interactive graph UI (single-page SVG app)
- `GET /api/graph` — JSON snapshot of the current graph
- `WS /ws` — live WebSocket updates (pushes snapshots when graph changes)

**WebSocket protocol**:
- Server → client: `{"type": "snapshot", "data": {...}}` — full graph state
- Client → server: `{"type": "refresh"}` — request immediate snapshot
- Client → server: `{"type": "ping"}` → server responds `{"type": "pong"}`

**UI features**:
- Hierarchical auto-layout (COGs above, LETs below)
- Pan/zoom with mouse wheel, drag nodes to reposition
- Click nodes to inspect (class, mixins, handlers, channels, children, config)
- Color-coded edges: blue solid = data, red dashed = control
- Minimap for navigation in large graphs
- Auto-reconnecting WebSocket with REST fallback

### trace.py — Event Recording

- `CogletTrace(path)` — open a jsonl file for writing
- `record(coglet_type, op, target, data)` — append one event
- `close()` — flush and close
- `CogletTrace.load(path)` — static, load trace for inspection

Each line: `{"t": <seconds_since_start>, "coglet": "ClassName", "op": "transmit"|"enact", "target": "<channel_or_command>", "data": ...}`

## Testing

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

200 tests, organized by component:
- `test_channel.py` — Channel, ChannelSubscription, ChannelBus
- `test_coglet.py` — Coglet base, decorators, dispatch, COG interface
- `test_handle.py` — Command, CogBase, CogletHandle
- `test_runtime.py` — spawn, shutdown, tree, trace, restart
- `test_mixins.py` — LifeLet, TickLet, ProgLet, GitLet, LogLet, MulLet
- `test_improvements.py` — SuppressLet, tree, trace, ticker errors, restart, on_child_error
- `test_integration.py` — multi-layer hierarchies, cross-mixin interactions
- `test_weblet.py` — WebLet mixin, CogWebRegistry, live snapshots, edges
- `test_cogweb_ui.py` — CogWebUI server (REST, WebSocket, runtime integration)

## Key Patterns

**Subscribe before transmit**: Channel subscribers must exist before `transmit()` is
called. There is no replay buffer. In tests, create subscriptions before triggering
actions that transmit.

**MRO matters**: when mixing SuppressLet with Coglet, SuppressLet must come first
so its `transmit()` override intercepts before Coglet's.

**Fire-and-forget**: `guide()` has no return value. The COG learns only by observing
subsequent transmissions from the child.

**Recursive protocol**: the same COG/LET protocol works at every level. A 3-level
tree (Root → Mid → Leaf) uses the exact same create/observe/guide/listen/enact/transmit
primitives throughout.
