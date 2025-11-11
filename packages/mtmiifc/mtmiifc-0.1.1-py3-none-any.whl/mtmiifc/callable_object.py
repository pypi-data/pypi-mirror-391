import importlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

# 基于配置，加载模块类或类构造函数，构建实例对象


def get_object_from_module(
    module: str, object: str, package: str | None = None
) -> object:
    """低级 API, 从模块中获取类或者函数等对象"""
    try:
        return getattr(importlib.import_module(module, package=package), object)
    except Exception as exc:  # noqa: BLE001
        text = (
            f"Invalid Module Name or Invalid Callable Object Name {module}.{object}"
        )
        if package:
            text += f" {package}!"
        else:
            text += "!"
        raise ValueError(text) from exc


def is_callable_object_config(value: Mapping[str, Any]) -> bool:
    required_keys = {"module", "object"}
    return required_keys.issubset(value.keys())


def convert_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        if is_callable_object_config(value):
            return CallableObject.from_config(value)
        return {key: convert_value(val) for key, val in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [convert_value(item) for item in value]
    return value



@dataclass
class CallableObject:
    module: str | None = None
    object: str | None = None
    package: str | None = None
    params: dict | None = None
    _object: Any = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.module or not self.object:
            msg = "CallableObject 需要提供有效的 module 与 object"
            raise ValueError(msg)
        self._object = get_object_from_module(
            self.module,
            self.object,
            self.package,
        )

    def build(self, params: dict | None = None) -> Any:
        params = params or {}
        config_params = self.params.copy() if self.params else {}
        merged_params = {**config_params, **params}
        return self._object(**merged_params)

    def __call__(self, **params: Any) -> Any:
        return self.build(params=params)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "CallableObject":
        if not isinstance(config, Mapping):
            msg = "CallableObject.from_config 需要 dict / Mapping 类型的配置"
            raise TypeError(msg)
        params = config.get("params")
        if params is not None and not isinstance(params, Mapping):
            msg = "CallableObject 配置中的 params 必须为 dict / Mapping 类型"
            raise TypeError(msg)
        return cls(
            module=config.get("module"),
            object=config.get("object"),
            package=config.get("package"),
            params=dict[Any, Any](params) if isinstance(params, Mapping) else params,
        )

def build_callable_object_tree(config: Mapping[str, Any]) -> CallableObject | dict[str, Any]:
    if not isinstance(config, Mapping):
        raise ValueError(f"build_callable_object_tree 需要传入 Mapping 类型的数据, 但传入的是 {type(config)} 类型的数据")
    if is_callable_object_config(config):
        return CallableObject.from_config(config)
    else:
        return {key: (build_callable_object_tree(value) if isinstance(value, Mapping) else value) 
            for key, value in config.items()
        }
