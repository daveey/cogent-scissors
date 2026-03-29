# Coglet Framework Reference

Implementation reference for `src/coglet/`. For architecture design, see [coglet.md](coglet.md).

## Core: `coglet.py`

The `Coglet` base class implements both COG and LET interfaces.

### Decorators

```python
from coglet.coglet import Coglet, listen, enact

class MyCoglet(Coglet):
    @listen("observations")
    async def handle_obs(self, data):
        """Data plane: receive from a named channel."""
        await self.transmit("actions", self.decide(data))

    @enact("configure")
    async def handle_configure(self, config):
        """Control plane: receive command from supervising COG."""
        self.apply(config)
```

- `@listen(channel)` — sets `fn._listen_channel`, scanned by `__init_subclass__`
- `@enact(command_type)` — sets `fn._enact_command`, scanned by `__init_subclass__`
- Both work across the MRO (mixin decorators are found automatically)

### COG Methods

```python
handle = await self.create(CogBase(cls=ChildCoglet, kwargs={...}))
await self.guide(handle, Command(type="reload", data={...}))
async for data in self.observe(handle, "results"):
    process(data)
```

### Dispatch

`_dispatch_listen(channel, data)` and `_dispatch_enact(command)` look up the method name from `_listen_handlers` / `_enact_handlers` dicts (populated at class creation by `__init_subclass__`).

## Channel Bus: `channel.py`

Async pub/sub. `transmit()` pushes to all subscribers on a channel. `subscribe()` returns a `ChannelSubscription` with async iteration.

## Handle: `handle.py`

- `CogletHandle` — opaque reference to a child Coglet
- `CogBase` — bundle of assets for spawning (class + kwargs + restart policy)
- `Command` — type + data for the control plane

## Runtime: `runtime.py`

`CogletRuntime` boots and manages Coglet trees. `spawn()` instantiates a Coglet, calls `on_start()` (if LifeLet), and starts tickers (if TickLet).

## Mixins

### LifeLet (`lifelet.py`)

```python
class MyCoglet(Coglet, LifeLet):
    async def on_start(self):
        """Called when coglet process starts."""

    async def on_stop(self):
        """Called on shutdown."""
```

Both are no-ops by default. Raising in either aborts the transition.

### TickLet (`ticklet.py`)

```python
from coglet.ticklet import TickLet, every

class MyCoglet(Coglet, TickLet):
    @every(10, "s")       # every 10 seconds (asyncio task)
    async def heartbeat(self): ...

    @every(5, "m")        # every 5 minutes
    async def analyze(self): ...

    @every(100, "ticks")  # every 100 manual ticks
    async def adapt(self): ...
```

Time-based (`"s"`, `"m"`) creates asyncio tasks. Tick-based (`"ticks"`) requires calling `await self.tick()` manually.

### CodeLet (`codelet.py`)

```python
class MyPolicy(Coglet, CodeLet):
    # self.functions: dict[str, Callable] — populated at init

    @listen("obs")
    async def step(self, obs):
        action = self.functions["step"](obs)
        await self.transmit("action", action)
```

Functions are registered/replaced via `@enact("register")` (built-in). Where GitLet versions behavior as git commits, CodeLet keeps it in-memory as a mutable function table.

### GitLet (`gitlet.py`)

```python
class MyPlayer(Coglet, GitLet):
    # self.repo_path — defaults to cwd
    pass
```

Built-in enact handlers:
- `@enact("commit")` — applies a patch via `git apply --index` + `git commit`

Utility methods:
- `await self.revert(n)` — revert last N commits
- `await self.branch(name)` — create and checkout branch
- `await self.checkout(ref)` — checkout a ref

### LogLet (`loglet.py`)

Adds a log stream separate from transmit. The COG subscribes to it independently. Transmit carries results/actions; log carries traces/metrics.

### MulLet (`mullet.py`)

```python
class MyFleet(Coglet, MulLet):
    async def on_start(self):
        await self.create_mul(n=10, config=WorkerConfig())

    def map(self, event):
        """Route event to children. Default: broadcast."""
        return [(i, event) for i in range(len(self._mul_children))]

    def reduce(self, results):
        """Aggregate child outputs. Default: return list."""
        return results
```

Methods:
- `create_mul(n, config)` — spawn N identical children
- `guide_mapped(command)` — send command to all children
- `scatter(channel, event)` — distribute via `map()`
- `gather(channel)` — collect from all children, then `reduce()`
