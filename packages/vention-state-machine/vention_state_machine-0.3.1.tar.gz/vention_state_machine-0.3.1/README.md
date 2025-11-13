# vention-state-machine

A lightweight wrapper around `transitions` for building async-safe, recoverable hierarchical state machines with minimal boilerplate.

## Table of Contents

- [✨ Features](#-features)
- [🧠 Concepts & Overview](#-concepts--overview)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🚀 Quickstart Tutorial](#-quickstart-tutorial)
- [🛠 How-to Guides](#-how-to-guides)
- [📖 API Reference](#-api-reference)
- [🔍 Troubleshooting & FAQ](#-troubleshooting--faq)

## ✨ Features

- Built-in `ready` / `fault` states
- Global transitions: `to_fault`, `reset`
- Optional state recovery (`recover__state`)
- Async task spawning and cancellation
- Timeouts and auto-fault handling
- Transition history recording with timestamps + durations
- Guard conditions for blocking transitions
- Global state change callbacks for logging/MQTT
- Optional FastAPI router for HTTP access and visualization

## 🧠 Concepts & Overview

This library uses a **declarative domain-specific language (DSL)** to define state machines in a readable, strongly typed way.

- **State** → A leaf node in the state machine
- **StateGroup** → Groups related states, creating hierarchical namespaces
- **Trigger** → Named events that initiate transitions

Example:

```python
class MyStates(StateGroup):
    idle: State = State()
    working: State = State()

class Triggers:
    begin = Trigger("begin")
    finish = Trigger("finish")

TRANSITIONS = [
    Triggers.finish.transition(MyStates.working, MyStates.idle),
]
```


### Base States and Triggers

All machines include:

**States:**
- `ready` (initial)
- `fault` (global error)

**Triggers:**
- `start`, `to_fault`, `reset`

```python
from state_machine.core import BaseStates, BaseTriggers

state_machine.trigger(BaseTriggers.RESET.value)
assert state_machine.state == BaseStates.READY.value
```

## ⚙️ Installation & Setup

```bash
pip install vention-state-machine
```

**Optional dependencies:**
- Graphviz (required for diagram generation)
- FastAPI (for HTTP exposure of state machine)

**Install optional tools:**

MacOS:
```bash
brew install graphviz
pip install fastapi
```

Linux (Debian/Ubuntu)
```bash
sudo apt-get install graphviz
pip install fastapi
```


## 🚀 Quickstart Tutorial

### 1. Define States and Triggers

```python
from state_machine.defs import StateGroup, State, Trigger

class Running(StateGroup):
    picking: State = State()
    placing: State = State()
    homing: State = State()

class States:
    running = Running()

class Triggers:
    start = Trigger("start")
    finished_picking = Trigger("finished_picking")
    finished_placing = Trigger("finished_placing")
    finished_homing = Trigger("finished_homing")
    to_fault = Trigger("to_fault")
    reset = Trigger("reset")
```

### 2. Define Transitions

```python
TRANSITIONS = [
    Triggers.start.transition("ready", States.running.picking),
    Triggers.finished_picking.transition(States.running.picking, States.running.placing),
    Triggers.finished_placing.transition(States.running.placing, States.running.homing),
    Triggers.finished_homing.transition(States.running.homing, States.running.picking),
]
```

### 3. Implement Your State Machine

```python
from state_machine.core import StateMachine
from state_machine.decorators import on_enter_state, auto_timeout, guard, on_state_change

class CustomMachine(StateMachine):
    def __init__(self):
        super().__init__(states=States, transitions=TRANSITIONS)

    @on_enter_state(States.running.picking)
    @auto_timeout(5.0, Triggers.to_fault)
    def enter_picking(self, _):
        print("🔹 Entering picking")

    @on_enter_state(States.running.placing)
    def enter_placing(self, _):
        print("🔸 Entering placing")

    @on_enter_state(States.running.homing)
    def enter_homing(self, _):
        print("🔺 Entering homing")

    @guard(Triggers.reset)
    def check_safety_conditions(self) -> bool:
        return not self.estop_pressed

    @on_state_change
    def publish_state_to_mqtt(self, old_state: str, new_state: str, trigger: str):
        mqtt_client.publish("machine/state", {
            "old_state": old_state,
            "new_state": new_state,
            "trigger": trigger
        })
```

### 4. Start It

```python
state_machine = StateMachine()
state_machine.start()
```

## 🛠 How-to Guides

### Expose Over HTTP with FastAPI

```python
from fastapi import FastAPI
from state_machine.router import build_router
from state_machine.core import StateMachine

state_machine = StateMachine(...)
state_machine.start()

app = FastAPI()
app.include_router(build_router(state_machine))
```

**Endpoints:**
- `GET /state` → Current state
- `GET /history` → Transition history
- `POST /<trigger>` → Trigger a transition
- `GET /diagram.svg` → Graphviz diagram

### Timeout Example

```python
@auto_timeout(5.0, Triggers.to_fault)
def enter_state(self, _):
    ...
```

### Recovery Example

```python
state_machine = StateMachine(enable_last_state_recovery=True)
state_machine.start()  # will attempt recover__{last_state}
```

### Triggering state transitions via I/O

Here's an example of hooking up state transitions to I/O events via MQTT

```python
import asyncio
import paho.mqtt.client as mqtt
from state_machine.core import StateMachine
from state_machine.defs import State, StateGroup, Trigger
from state_machine.decorators import on_enter_state

class MachineStates(StateGroup):
    idle: State = State()
    running: State = State()

class States:
    machine = MachineStates()

class Triggers:
    start_button = Trigger("start_button")
    box_missing = Trigger("box_missing")

TRANSITIONS = [
    Triggers.start_button.transition(States.machine.idle, States.machine.running),
    Triggers.box_missing.transition(States.machine.running, States.machine.idle),
]

class MachineController(StateMachine):
    def __init__(self):
        super().__init__(states=States, transitions=TRANSITIONS)
        self.mqtt_client = mqtt.Client()
        self.setup_mqtt()

    def setup_mqtt(self):
        """Configure MQTT client to listen for I/O signals."""
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect("localhost", 1883, 60)
        
        # Start MQTT loop in background
        self.spawn(self.mqtt_loop())

    async def mqtt_loop(self):
        """Background task to handle MQTT messages."""
        self.mqtt_client.loop_start()
        while True:
            await asyncio.sleep(0.1)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Subscribe to I/O topics when connected."""
        client.subscribe("machine/io/start_button")
        client.subscribe("machine/sensors/box_sensor")

    def on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages and trigger state transitions."""
        topic = msg.topic
        payload = msg.payload.decode()
        
        # Map MQTT topics to state machine triggers
        if topic == "machine/io/start_button" and payload == "pressed":
            self.trigger(Triggers.start_button.value)
        elif topic == "machine/sensors/box_sensor" and payload == "0":
            self.trigger(Triggers.box_missing.value)

    @on_enter_state(States.machine.running)
    def enter_running(self, _):
        print("🔧 Machine started - processing parts")
        self.mqtt_client.publish("machine/status", "running")

    @on_enter_state(States.machine.idle)
    def enter_idle(self, _):
        print("⏸️ Machine idle - ready for start")
        self.mqtt_client.publish("machine/status", "idle")
```

## 📖 API Reference

### StateMachine

```python
class StateMachine(HierarchicalGraphMachine):
    def __init__(
        self,
        states: Union[object, list[dict[str, Any]], None],
        *,
        transitions: Optional[list[dict[str, str]]] = None,
        history_size: Optional[int] = None,
        enable_last_state_recovery: bool = True,
        **kw: Any,
    )
```

**Parameters:**
- `states`: Either a container of StateGroups or a list of state dicts.
- `transitions`: List of transition dictionaries, or `[]`.
- `history_size`: Max number of entries in transition history (default 1000).
- `enable_last_state_recovery`: If True, machine can resume from last recorded state.

### Methods

**`spawn(coro: Coroutine) -> asyncio.Task`**
Start a background coroutine and track it. Auto-cancelled on fault/reset.

**`cancel_tasks() -> None`**
Cancel all tracked tasks and timeouts.

**`set_timeout(state_name: str, seconds: float, trigger_fn: Callable[[], str]) -> None`**
Schedule a trigger if state_name stays active too long.

**`record_last_state() -> None`**
Save current state for recovery.

**`get_last_state() -> Optional[str]`**
Return most recently recorded state.

**`start() -> None`**
Enter machine (recover__... if applicable, else start).

### Properties

**`history -> list[dict[str, Any]]`**
Full transition history with timestamps/durations.

**`get_last_history_entries(n: int) -> list[dict[str, Any]]`**
Return last n transitions.

### Decorators

**`@on_enter_state(state: State)`**
Bind function to run on entry.

**`@on_exit_state(state: State)`**
Bind function to run on exit.

**`@auto_timeout(seconds: float, trigger: Trigger)`**
Auto-trigger if timeout expires.

**`@guard(*triggers: Trigger)`**
Guard transition; blocks if function returns False.

**`@on_state_change`**
Global callback `(old_state, new_state, trigger)` fired after each transition.

### Router

```python
def build_router(
    machine: StateMachine,
    triggers: Optional[list[Trigger]] = None
) -> fastapi.APIRouter
```

Exposes endpoints:
- `GET /state`
- `GET /history`
- `POST /<trigger>`
- `GET /diagram.svg`

## 🔍 Troubleshooting & FAQ

- **Diagram endpoint returns 503** → Graphviz not installed.
- **Transitions blocked unexpectedly** → Check guard conditions.
- **Callbacks not firing** → Only successful transitions trigger them.
- **State not restored after restart** → Ensure `enable_last_state_recovery=True`.