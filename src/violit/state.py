from typing import Any, Dict, Set, Callable, List
from cachetools import TTLCache
from .context import session_ctx, rendering_ctx, app_instance_ref
from .theme import Theme


class ReactiveExpr:
    """
    Reactive Expression - lambda 대신 사용할 수 있는 반응형 표현식
    
    사용 예:
        count = app.state(0)
        app.text(count * 2)           # ReactiveExpr
        app.text("Count: " + count)   # ReactiveExpr
        app.text(count + " items")    # ReactiveExpr
    """
    def __init__(self, fn: Callable, states: List['State'] = None):
        self._fn = fn
        self._states = states or []
    
    def __call__(self):
        """평가하고 값 반환"""
        return self._fn()
    
    def __str__(self):
        return str(self._fn())
    
    def __repr__(self):
        return f"ReactiveExpr({self._fn()})"
    
    # ReactiveExpr끼리 연산도 지원
    def __add__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() + other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() + other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() + other, self._states)
    
    def __radd__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: other._fn() + self._fn(), other._states + self._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: other.value + self._fn(), [other] + self._states)
        else:
            return ReactiveExpr(lambda: other + self._fn(), self._states)
    
    def __mul__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() * other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() * other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() * other, self._states)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __sub__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() - other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() - other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() - other, self._states)
    
    def __rsub__(self, other):
        return ReactiveExpr(lambda: other - self._fn(), self._states)
    
    def __truediv__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() / other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() / other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() / other, self._states)
    
    def __floordiv__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() // other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() // other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() // other, self._states)
    
    def __mod__(self, other):
        if isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self._fn() % other._fn(), self._states + other._states)
        elif isinstance(other, State):
            return ReactiveExpr(lambda: self._fn() % other.value, self._states + [other])
        else:
            return ReactiveExpr(lambda: self._fn() % other, self._states)


class DependencyTracker:
    def __init__(self):
        self.subscribers: Dict[str, Set[str]] = {}
    
    def register_dependency(self, state_name: str, component_id: str):
        if state_name not in self.subscribers:
            self.subscribers[state_name] = set()
        self.subscribers[state_name].add(component_id)

    def get_dirty_components(self, state_name: str) -> Set[str]:
        return self.subscribers.get(state_name, set())

GLOBAL_STORE = TTLCache(maxsize=1000, ttl=1800)

def get_session_store():
    sid = session_ctx.get()
    if sid not in GLOBAL_STORE:
        initial_theme = 'light'
        if app_instance_ref[0]:
            initial_theme = app_instance_ref[0].theme_manager.preset_name
            
        GLOBAL_STORE[sid] = {
            'states': {}, 
            'tracker': DependencyTracker(),
            'builders': {},
            'actions': {},
            'component_count': 0,
            'fragment_components': {},
            'order': [],
            'sidebar_order': [],
            'theme': Theme(initial_theme)
        }
    return GLOBAL_STORE[sid]

class State:
    def __init__(self, name: str, default_value: Any):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'default_value', default_value)

    @property
    def value(self):
        store = get_session_store()
        current_comp_id = rendering_ctx.get()
        if current_comp_id:
            store['tracker'].register_dependency(self.name, current_comp_id)
        return store['states'].get(self.name, self.default_value)
    
    @value.setter
    def value(self, new_value: Any):
        self.set(new_value)

    def set(self, new_value: Any):
        store = get_session_store()
        store['states'][self.name] = new_value
        if 'dirty_states' not in store: store['dirty_states'] = set()
        store['dirty_states'].add(self.name)
    
    def __setattr__(self, attr: str, val: Any):
        if attr == 'value':
            self.set(val)
        else:
            object.__setattr__(self, attr, val)

    def __str__(self):
        return str(self.value)
    
    def __call__(self):
        return self.value
    
    def __repr__(self):
        return f"State({self.name}, {self.value})"
    
    # ========== 연산자 오버로딩 (ReactiveExpr 반환) ==========
    # 이제 lambda 대신 count * 2, "Hello " + name 등 사용 가능!
    
    def __add__(self, other):
        """count + 1, count + other_state"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value + other.value, [self, other])
        elif isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self.value + other._fn(), [self] + other._states)
        else:
            return ReactiveExpr(lambda: self.value + other, [self])
    
    def __radd__(self, other):
        """"Hello " + name"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: other.value + self.value, [other, self])
        elif isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: other._fn() + self.value, other._states + [self])
        else:
            return ReactiveExpr(lambda: other + self.value, [self])
    
    def __sub__(self, other):
        """count - 1"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value - other.value, [self, other])
        elif isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self.value - other._fn(), [self] + other._states)
        else:
            return ReactiveExpr(lambda: self.value - other, [self])
    
    def __rsub__(self, other):
        """10 - count"""
        return ReactiveExpr(lambda: other - self.value, [self])
    
    def __mul__(self, other):
        """count * 2"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value * other.value, [self, other])
        elif isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self.value * other._fn(), [self] + other._states)
        else:
            return ReactiveExpr(lambda: self.value * other, [self])
    
    def __rmul__(self, other):
        """2 * count"""
        return self.__mul__(other)
    
    def __truediv__(self, other):
        """count / 2"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value / other.value, [self, other])
        elif isinstance(other, ReactiveExpr):
            return ReactiveExpr(lambda: self.value / other._fn(), [self] + other._states)
        else:
            return ReactiveExpr(lambda: self.value / other, [self])
    
    def __rtruediv__(self, other):
        """10 / count"""
        return ReactiveExpr(lambda: other / self.value, [self])
    
    def __floordiv__(self, other):
        """count // 2"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value // other.value, [self, other])
        else:
            return ReactiveExpr(lambda: self.value // other, [self])
    
    def __mod__(self, other):
        """count % 2"""
        if isinstance(other, State):
            return ReactiveExpr(lambda: self.value % other.value, [self, other])
        else:
            return ReactiveExpr(lambda: self.value % other, [self])
    
    def __neg__(self):
        """-count"""
        return ReactiveExpr(lambda: -self.value, [self])
    
    def __pos__(self):
        """+count"""
        return ReactiveExpr(lambda: +self.value, [self])
