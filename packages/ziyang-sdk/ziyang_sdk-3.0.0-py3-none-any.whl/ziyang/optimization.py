"""性能优化模块."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

import numpy as np

Strategy = Callable[[Any], Any]
StrategyFactory = Callable[[], Strategy]


class PerformanceOptimizer:
    """性能优化策略集合."""

    def __init__(self) -> None:
        self._strategies: Dict[str, Strategy] = {
            "digital_root": self._optimize_digital_root,
            "quantum_convergence": self._optimize_quantum,
            "memory_usage": self._optimize_memory,
        }
        self._factories: Dict[str, StrategyFactory] = {}

    @property
    def optimization_strategies(self) -> Dict[str, Strategy]:
        """返回当前策略映射，用于向后兼容."""

        return self._strategies

    def register_strategy(
        self, name: str, strategy: Strategy, *, override: bool = False
    ) -> None:
        """注册自定义优化策略."""

        if name in self._strategies and not override:
            raise ValueError(f"策略 {name} 已存在，若需覆盖请设置 override=True")
        self._strategies[name] = strategy

    def register_strategy_factory(
        self, name: str, factory: StrategyFactory, *, override: bool = False
    ) -> None:
        """注册延迟创建的策略工厂."""

        if name in self._factories and not override:
            raise ValueError(f"策略工厂 {name} 已存在，若需覆盖请设置 override=True")
        self._factories[name] = factory
        self._strategies.pop(name, None)

    def _ensure_strategy(self, name: str) -> Optional[Strategy]:
        strategy = self._strategies.get(name)
        if strategy:
            return strategy
        factory = self._factories.get(name)
        if not factory:
            return None
        strategy = factory()
        self._strategies[name] = strategy
        return strategy

    def unregister_strategy(self, name: str) -> None:
        """移除指定策略."""

        self._strategies.pop(name, None)
        self._factories.pop(name, None)

    def has_strategy(self, name: str) -> bool:
        """判断策略是否存在."""

        return name in self._strategies or name in self._factories

    def available_strategies(self) -> List[str]:
        """返回所有可用策略名称."""

        keys = set(self._strategies.keys())
        keys.update(self._factories.keys())
        return sorted(keys)

    def optimize_algorithm(self, algorithm_name: str, data: Any) -> Optional[Any]:
        """优化指定算法性能."""

        strategy = self._ensure_strategy(algorithm_name)
        if not strategy:
            return None
        return strategy(data)

    def _optimize_digital_root(self, numbers: Iterable[int]) -> np.ndarray:
        """优化数字根计算性能."""

        numbers_array = np.array(list(numbers))
        safe_numbers = np.abs(numbers_array)
        roots = np.where(
            safe_numbers == 0,
            0,
            1 + (np.mod(safe_numbers - 1, 9)),
        )
        return roots

    def _optimize_quantum(self, numbers: Iterable[int]) -> List[int]:
        """示例量子收敛优化策略."""

        return [int(number) % 9 or 9 for number in numbers]

    def _optimize_memory(self, data: Any) -> Any:
        """内存优化占位实现."""

        return data
