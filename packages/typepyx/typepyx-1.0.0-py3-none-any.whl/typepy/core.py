class Any:
    pass

class NType:
    base_types = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict
    }

    def __init__(self, value=None, dType="any", const=False):
        self.const = const
        self._value = value
        self.type_tree = self._parse_type(dType.strip().lower())
        self._validate(value, self.type_tree)

    def _parse_type(self, t):
        t = t.replace("{", "[").replace("}", "]")
        if "|" in t:
            return ["union", [self._parse_type(x.strip()) for x in t.split("|")]]
        if t.startswith("dict["):
            inner = t[5:-1]
            k, v = [s.strip() for s in inner.split(",", 1)]
            return ["dict", self._parse_type(k), self._parse_type(v)]
        if t.startswith("list["):
            inner = t[5:-1]
            return ["list", self._parse_type(inner)]
        if t.endswith("[]"):
            return ["list", self._parse_type(t[:-2])]
        if t == "any":
            return ["any"]
        return ["base", self.base_types.get(t, Any)]

    def _validate(self, val, t):
        kind = t[0]
        if kind == "any":
            return
        if kind == "base":
            typ = t[1]
            if typ != Any and not isinstance(val, typ):
                raise TypeError(f"{type(val).__name__} is not {typ.__name__}")
        elif kind == "list":
            if not isinstance(val, list):
                raise TypeError("Expected list")
            for item in val:
                self._validate(item, t[1])
        elif kind == "dict":
            if not isinstance(val, dict):
                raise TypeError("Expected dict")
            for k, v in val.items():
                self._validate(k, t[1])
                self._validate(v, t[2])
        elif kind == "union":
            if not any(self._is_valid(val, u) for u in t[1]):
                raise TypeError(f"Invalid type for union: {type(val).__name__}")
        else:
            raise TypeError("Unknown type definition")

    def _is_valid(self, val, t):
        try:
            self._validate(val, t)
            return True
        except TypeError:
            return False

    def _operate(self, other, op):
        val = other._value if isinstance(other, NType) else other
        if not isinstance(self._value, (int, float, str, list)):
            raise TypeError(f"Operation not supported on type {type(self._value).__name__}")
        return op(self._value, val)

    # arithmetic
    def __add__(self, other): return self._operate(other, lambda a, b: a + b)
    def __sub__(self, other): return self._operate(other, lambda a, b: a - b)
    def __mul__(self, other): return self._operate(other, lambda a, b: a * b)
    def __truediv__(self, other): return self._operate(other, lambda a, b: a / b)
    def __floordiv__(self, other): return self._operate(other, lambda a, b: a // b)
    def __mod__(self, other): return self._operate(other, lambda a, b: a % b)
    def __pow__(self, other): return self._operate(other, lambda a, b: a ** b)

    # comparison
    def __eq__(self, other): return self._operate(other, lambda a, b: a == b)
    def __ne__(self, other): return self._operate(other, lambda a, b: a != b)
    def __lt__(self, other): return self._operate(other, lambda a, b: a < b)
    def __le__(self, other): return self._operate(other, lambda a, b: a <= b)
    def __gt__(self, other): return self._operate(other, lambda a, b: a > b)
    def __ge__(self, other): return self._operate(other, lambda a, b: a >= b)

    # string/list/dict length
    def __len__(self):
        if isinstance(self._value, (list, str, dict)):
            return len(self._value)
        raise TypeError("len() only valid for list, str, or dict")

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if self.const:
            raise AttributeError("Const value")
        self._validate(v, self.type_tree)
        self._value = v


def setType(value=None, dtype="any", const=False):
    return NType(value, dtype, const)