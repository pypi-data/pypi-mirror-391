import torch.nn as nn
import inspect
from typing import Optional, Dict, Any, Callable, TypeVar, List


BUILTIN_BLOCKS = {"nn." + module: getattr(nn.modules, module) for module in nn.modules.__all__}
M = TypeVar("M", bound=nn.Module)


def register_block(name: Optional[str] = None) -> Callable[[Callable[..., M]], Callable[..., M]]:
    def wrapper(fn: Callable[..., M]) -> Callable[..., M]:
        key = name if name is not None else fn.__name__
        if key in BUILTIN_BLOCKS:
            raise ValueError(f"An entry is already registered under the name '{key}'.")
        BUILTIN_BLOCKS[key] = fn
        return fn

    return wrapper


def get_block_builder(name: str) -> Callable[..., nn.Module]:
    """
    Gets the model name and returns the model builder method.

    Args:
        name (str): The name under which the model is registered.

    Returns:
        fn (Callable): The model builder method.
    """
    try:
        fn = BUILTIN_BLOCKS[name]
    except KeyError:
        raise ValueError(f"Unknown model {name}")
    return fn


def get_block(name: str, **config: Any) -> nn.Module:
    """
    Gets the model name and configuration and returns an instantiated model.

    Args:
        name (str): The name under which the block is registered.
        **config (Any): parameters passed to the block builder method.

    Returns:
        model (nn.Module): The initialized block.
    """
    fn = get_block_builder(name)
    return fn(**config)


from dataclasses import dataclass, asdict

@dataclass
class BaseBlockConfig:
    """基础块配置类 - 定义基础块的配置"""
    block_type: str
    cin: Optional[int] = None
    cout: Optional[int] = None
    repeat: int = 1
    name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    def copy(self) -> "BaseBlockConfig":
        return BaseBlockConfig(**asdict(self))

@dataclass
class AtomBlockConfig(BaseBlockConfig):
    """原子块配置类 - 定义原子块的配置, 不可再拆分"""
    def __post_init__(self):
        self.repeat = 1

@dataclass
class SequentialBlockConfig:
    """序列块配置类 - 定义序列块的配置"""
    blocks: List[BaseBlockConfig] 
    cin: Optional[int] = None
    cout: Optional[int] = None

    def __post_init__(self):
        if self.cin is not None:
            self.blocks[0].cin = self.cin
        if self.cout is not None:
            self.blocks[-1].cout = self.cout
        if self.cin is None and len(self.blocks) > 0 and hasattr(self.blocks[0], "cin"):
            self.cin = self.blocks[0].cin
        if self.cout is None and len(self.blocks) > 0 and hasattr(self.blocks[-1], "cout"):
            self.cout = self.blocks[-1].cout

    def copy(self) -> "SequentialBlockConfig":
        return SequentialBlockConfig(blocks=[_config.copy() for _config in self.blocks], cin=self.cin, cout=self.cout)

@dataclass
class UniformBlockConfig:
    """同类型块配置类 - 定义同类型块的配置, 可重复"""
    block_type: str
    cin: Optional[int] = None
    cout: Optional[int] = None
    repeat: int = 1
    name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    def decompose(self) -> AtomBlockConfig | SequentialBlockConfig:
        if self.repeat == 1:
            return AtomBlockConfig(block_type=self.block_type, cin=self.cin, cout=self.cout, name=self.name, params=self.params)
        else:
            blocks = [AtomBlockConfig(block_type=self.block_type, cin=self.cout, cout=self.cout, name=self.name, params=self.params) for _ in range(self.repeat)]
            return SequentialBlockConfig(blocks=blocks, cin=self.cin, cout=self.cout)

 

def filter_params(func: Callable, params: dict) -> dict:
    params = params.copy() if params is not None else {}

    sig = inspect.signature(func)

    # 检查是否有可变关键字参数(**kwargs)
    has_var_keyword = any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())

    # 如果有**kwargs，传递所有参数；否则只传递匹配的参数
    if has_var_keyword:
        filtered_params = params
    else:
        param_names = set[str](sig.parameters.keys())
        filtered_params = {k: v for k, v in (params or {}).items() if k in param_names}
    return filtered_params

def map_params(func: Callable, params: dict, mapping: dict) -> dict:
    params = params.copy() or {}
    sig = inspect.signature(func)
    param_names = sig.parameters.keys()
    for org_k, targets_k in mapping.items():
        if params.get(org_k) is not None:
            continue
        for target_k in targets_k:
            if target_k in param_names:
                params[target_k] = params.pop(org_k)
                break
    return params
  

class BlockBuilder:
    @staticmethod
    def recursive_load(config: dict | list, cin: int = None, cout: int = None) -> UniformBlockConfig | SequentialBlockConfig:
        """从字典或列表 递归加载 同类型块或序列块配置"""
        config = config.copy()
        if isinstance(config, dict):
            if cin is not None:
                config["cin"] = cin
            if cout is not None:
                config["cout"] = cout
            return UniformBlockConfig(**config).decompose()
        if isinstance(config, list):
            block_configs = config.copy()
            if cin is not None:
                block_configs[0]["cin"] = cin
            if cout is not None:
                block_configs[-1]["cout"] = cout
            return SequentialBlockConfig(blocks=[BlockBuilder.recursive_load(_config) for _config in block_configs])
        raise ValueError(f"Invalid block config: {config}")

    @staticmethod
    def recursive_build(config: AtomBlockConfig | SequentialBlockConfig) -> nn.Module | nn.Sequential:
        """递归构建原子块或序列块"""
        if isinstance(config, AtomBlockConfig):
            return BlockBuilder.build_atom_block(config)
        if isinstance(config, SequentialBlockConfig):
            block_list = []
            for _config in config.blocks:
                _module = BlockBuilder.recursive_build(_config)
                block_list.append(_module)
            return nn.Sequential(*block_list)
        raise ValueError(f"Invalid block config: {config}")

    @staticmethod
    def build_atom_block(config: AtomBlockConfig) -> nn.Module:
        """构建单个块"""
        if config.repeat > 1:
            raise ValueError("AtomBlockConfig repeat must be 1")
        config = config.copy()
        block_class = get_block_builder(config.block_type)
        _params = config.params.copy() if config.params is not None else {}
        _params.update({"cin": config.cin, "cout": config.cout})
        mapping = {"cin": ["in_channels", "in_features"], "cout": ["out_channels", "out_features"]}
        _mapped_params = map_params(block_class, _params, mapping)
        _filted_params = filter_params(block_class, _mapped_params)
        return block_class(**_filted_params)


    @staticmethod
    def build(config: dict | list, cin: int = None, cout: int = None) -> tuple[BaseBlockConfig | SequentialBlockConfig, nn.Module | nn.Sequential]:
        block_config = BlockBuilder.recursive_load(config, cin, cout)
        module = BlockBuilder.recursive_build(block_config)
        return block_config, module