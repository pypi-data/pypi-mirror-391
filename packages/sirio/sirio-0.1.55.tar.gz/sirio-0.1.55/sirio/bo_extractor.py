from dataclasses import dataclass
from typing import Callable, List, Tuple, Any

from sirio.business_object import BusinessObject

Result = Tuple[List[str], Any] | None

Extractor = Callable[[BusinessObject], Result]


class _Filtered:
    pass


_FILTERED = _Filtered()


@dataclass(frozen=True)
class Value:
    f: Callable[[Any], Any]

    def map(self, g: Callable[[Any], Any]) -> "Value":
        def map_function(x):
            value = self.f(x)
            if value is _FILTERED:
                return _FILTERED
            return g(value)

        return Value(map_function)

    def filter(self, p: Callable[[Any], bool]) -> "Value":
        def filtered_function(x):
            value = self.f(x)
            if value is _FILTERED:
                return _FILTERED
            return value if p(value) else _FILTERED

        return Value(filtered_function)

    def to(self, first: str, *others: str) -> Extractor:
        def extractor(x):
            value = self.f(x)
            return None if value is _FILTERED else (_merge_keys(first, others), value)

        return extractor


def extract_business_key() -> Value:
    return Value(lambda bo: bo.businessKey)


def extract_internal_business_key() -> Value:
    return Value(lambda bo: bo.internalBusinessKey)


def extract_bind_id(bind: str, id: str) -> Value:
    return Value(lambda bo: bo.getValue(bind, id))


def _merge_keys(first: str, others: Tuple[str, ...]) -> List[str]:
    return [first] + list(others)


def extract(bo: Any, *extractors: Extractor) -> dict:
    result = {}

    for extractor in extractors:
        r = extractor(bo)
        if r:
            keys, value = r
            _merge(result, keys, value)

    return result


def _merge(result: dict[str, Any], keys: List[str], value: Any) -> None:
    current = result
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
