import functools
import weakref
import enum
from typing import Mapping, List, Callable, Optional, Hashable
from collections import defaultdict

class HandlerNotFoundError(Exception):
    def __init__(self, event):
        self._trigger_event = event

    def __repr__(self):
        return f'HandlerNotFound for {self._trigger_event}'

class EventEmitter(object):
    def __init__(self):
        self._event_handlers = {}  # type: Dict[Hashable: Callable]

    def on(self, event: str, handler: Callable):
        if not isinstance(handler, Callable):
            raise TypeError(f'handler must be Callable, not a {type(handler).__name__}')

        self._event_handlers[event] = handler

    def cancel(self, event: str):
        if event in self._event_handlers:
            del self._event_handlers[event]

    def emit(self, event: str, args: Optional[tuple]=None, kwargs: Optional[Mapping]=None):
        event_handler = self._event_handlers.get(event, None)
        if event_handler is None:
            raise HandlerNotFoundError(event)

        args = args or tuple()
        kwargs = kwargs or dict()

        ret = event_handler(*args, **kwargs)
        return ret


StateEnter = 'StateEnter'
StateLeave = 'StateLeave'


class FSM(object):
    def __init__(self, initial: Optional[Hashable]=None):
        self._state_evt_emitters = defaultdict(EventEmitter)
        self.state = initial

    def set_state(self, state: Hashable):
        self.state = state

    def transit_to(self, next_state: Hashable):
        prev_state = self.state
        self.command(StateLeave, args=(prev_state, next_state))
        self.set_state(next_state)
        self.command(StateEnter, args=(prev_state, next_state))

    def _weak_ref_transit_to(self):
        self_ref = weakref.ref(self)
        def wrapper(state: Hashable):
            fsm_obj = self_ref()
            if fsm_obj is None:
                return

            fsm_obj.transit_to(state)

        return wrapper

    def on(self, state: Hashable, event: str, action: Optional[Callable]=None, transition: Optional[Hashable]=None):
        if transition is not None:
            action = functools.partial(self._weak_ref_transit_to(), transition)

        emitter = self._state_evt_emitters[state]
        emitter.on(event, action)

    def command(self, event: str, args: Optional[tuple]=None, kwargs: Optional[Mapping]=None):
        emitter = self._state_evt_emitters[self.state]
        try:
            emitter.emit(event, args, kwargs)
        
        except HandlerNotFoundError:
            pass

        return self