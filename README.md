
fsm is a simple and easy to use finite state machine implement.

# Usage

```python
from fsm import FSM
from fsm import StateEnter, StateLeave

State1 = 'State1'
State2 = 'State2'

def state2move(input, fsm):
    print(f'Got input "{input}"')
    fsm.transit_to(State1)

test_fsm = FSM(State1)
test_fsm.on(State1, 'move', transition=State2)
test_fsm.on(State2, StateEnter, action=lambda prev_state, next_state: print('Enter State2'))
test_fsm.on(State2, StateLeave, action=lambda prev_state, next_state: print('Leave State2'))
test_fsm.on(State2, 'move', action=state2move)
print(test_fsm.state) # State1

test_fsm.command('move')
print(test_fsm.state) # State2

test_fsm.command('move', args=('Hello FSM!', test_fsm)) # got input Hello FSM!
print(test_fsm.state) # State1
```


# Exampe

![](DoorFSM.png)

```python
import enum
import fsm

class DoorState(enum.Enum):
    OPEN = 1
    CLOSED = 2
    LOCKED = 3
    BROKEN = 4

class Door(object):
    def __init__(self):
        self.door_fsm = fsm.FSM(DoorState.OPEN)
        self.fix_count = 0

        self.door_fsm.on(DoorState.OPEN, 'close', transition=DoorState.CLOSED)
        self.door_fsm.on(DoorState.CLOSED, 'open', transition=DoorState.OPEN)
        self.door_fsm.on(DoorState.CLOSED, 'lock', transition=DoorState.LOCKED)
        self.door_fsm.on(DoorState.LOCKED, 'unlock', transition=DoorState.CLOSED)
        self.door_fsm.on(DoorState.LOCKED, 'break', transition=DoorState.BROKEN)
        self.door_fsm.on(DoorState.BROKEN, 'fix', action=self._fix_door)

    def _fix_door(self):
        self.fix_count += 1
        if self.fix_count > 3:
            return

        self.door_fsm.transit_to(DoorState.OPEN)

    def state(self):
        return self.door_fsm.state

    def open(self):
        self.door_fsm.command('open')
        return self

    def close(self):
        self.door_fsm.command('close')
        return self

    def lock(self):
        self.door_fsm.command('lock')
        return self

    def unlock(self):
        self.door_fsm.command('unlock')
        return self

    def break_door(self):
        self.door_fsm.command('break')
        return self

    def fix(self):
        self.door_fsm.command('fix')
        return self
        
if __name__ == '__main__':
    door = Door()
    print(door.state()) # DoorState.OPEN

    door.close()
    print(door.state()) # DoorState.CLOSED

    door.lock()
    print(door.state()) # DoorState.LOCKED

    door.open()
    print(door.state()) # DoorState.LOCKED

    door.unlock().open().lock().close().lock()
    print(door.state()) # DoorState.LOCKED

    door.break_door()
    print(door.state()) # DoorState.BROKEN

    door.fix()
    print(door.state()) # DoorState.OPEN

    for _ in range(3):
        door.close().lock().break_door().fix()

    print(door.state()) # DoorState.BROKEN
```