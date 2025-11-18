"""紫阳智库 v3 SDK 核心功能实现."""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .benchmark import BenchmarkResult, PerformanceTracker
from .math_core import CosmicMath
from .optimization import PerformanceOptimizer


@dataclass
class _CacheEntry:
    """内部缓存结构，用于记录运行结果与执行时间。"""

    result: BenchmarkResult
    duration: float


class ZiyangSDK:
    """紫阳智库 v3 算力测试引擎."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.version = "3.0.0"
        self.config = config or self._default_config()
        self.performance_cache: Dict[Tuple[str, int], _CacheEntry] = {}
        self.cache_enabled: bool = bool(self.config.get("enable_cache", True))
        self.performance_tracker = PerformanceTracker()
        self.optimizer = PerformanceOptimizer()

    # --------------------------------------------------------------------- #
    # 公共方法
    # --------------------------------------------------------------------- #
    def benchmark_quantum_convergence(
        self, iterations: Optional[int] = None
    ) -> BenchmarkResult:
        """量子收敛性能基准测试."""

        iterations = iterations or self.config["quantum_iterations"]
        cache_key = ("quantum_convergence", iterations)
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        start = time.perf_counter()
        convergence_units = []
        path_examples = []
        for base in range(1, iterations + 1):
            data = CosmicMath.quantum_convergence_path(base)
            convergence_units.append(data["final_unit"])
            if base <= 5:
                path_examples.append(data["convergence_path"])

        duration = time.perf_counter() - start
        ops_per_sec = iterations / duration if duration else float("inf")

        result = BenchmarkResult(
            name="quantum_convergence",
            metrics={
                "iterations": iterations,
                "average_final_unit": statistics.mean(convergence_units),
                "operations_per_second": ops_per_sec,
                "unique_final_units": len(set(convergence_units)),
            },
            metadata={
                "path_examples": path_examples,
                "version": self.version,
            },
        )
        result.metrics["total_time_sec"] = duration

        self._store_cache(cache_key, result, duration)
        self.performance_tracker.add_result(result)
        return result

    def benchmark_digital_root(
        self, data_size: Optional[int] = None
    ) -> BenchmarkResult:
        """数字根计算性能测试."""

        data_size = data_size or self.config["digital_root_samples"]
        cache_key = ("digital_root", data_size)
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        sample_data = list(range(1, data_size + 1))
        start = time.perf_counter()
        optimized = self.optimizer.optimize_algorithm("digital_root", sample_data)
        if optimized is not None:
            supports_list = hasattr(optimized, "tolist")
            results = optimized.tolist() if supports_list else optimized
        else:
            results = [CosmicMath.digital_root(item) for item in sample_data]

        duration = time.perf_counter() - start
        ops_per_sec = data_size / duration if duration else float("inf")

        result = BenchmarkResult(
            name="digital_root",
            metrics={
                "data_size": data_size,
                "operations_per_second": ops_per_sec,
                "max_digital_root": max(results),
                "min_digital_root": min(results),
                "std_dev": statistics.pstdev(results),
            },
            metadata={"version": self.version},
        )
        result.metrics["total_time_sec"] = duration

        self._store_cache(cache_key, result, duration)
        self.performance_tracker.add_result(result)
        return result

    def benchmark_cosmic_cycles(self, cycles: Optional[int] = None) -> BenchmarkResult:
        """宇宙循环性能测试."""

        cycles = cycles or self.config["cosmic_cycles"]
        cache_key = ("cosmic_cycles", cycles)
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        start = time.perf_counter()
        sequence_state = 0
        history = []
        for step in range(1, cycles + 1):
            sequence_state = (sequence_state + step * 3) % 97
            history.append(sequence_state)
        duration = time.perf_counter() - start
        ops_per_sec = cycles / duration if duration else float("inf")

        result = BenchmarkResult(
            name="cosmic_cycles",
            metrics={
                "cycles": cycles,
                "operations_per_second": ops_per_sec,
                "peak_state": max(history),
                "stability_index": statistics.mean(history) / (max(history) or 1),
            },
            metadata={"version": self.version},
        )
        result.metrics["total_time_sec"] = duration

        self._store_cache(cache_key, result, duration)
        self.performance_tracker.add_result(result)
        return result

    def comprehensive_benchmark(self) -> Dict[str, Any]:
        """执行综合性能测试，汇总所有指标."""

        quantum = self.benchmark_quantum_convergence()
        digital = self.benchmark_digital_root()
        cosmic = self.benchmark_cosmic_cycles()

        aggregate_ops = sum(
            item.metrics.get("operations_per_second", 0.0)
            for item in (quantum, digital, cosmic)
        )
        estimated_flops = aggregate_ops * self.config["flops_multiplier"]

        return {
            "quantum_convergence": quantum.to_dict(),
            "digital_root": digital.to_dict(),
            "cosmic_cycles": cosmic.to_dict(),
            "performance_metrics": {
                "total_operations_per_second": aggregate_ops,
                "estimated_flops": estimated_flops,
            },
        }

    # ------------------------------------------------------------------ #
    # 内部方法
    # ------------------------------------------------------------------ #
    def enable_cache(self) -> None:
        """启用缓存."""

        self.cache_enabled = True

    def disable_cache(self) -> None:
        """禁用缓存并清空已有结果."""

        self.cache_enabled = False
        self.clear_cache()

    def clear_cache(self) -> None:
        """清空缓存."""

        self.performance_cache.clear()

    def cache_stats(self) -> Dict[str, Any]:
        """返回当前缓存状态."""

        keys = list(self.performance_cache.keys())
        return {
            "enabled": self.cache_enabled,
            "size": len(keys),
            "entries": keys,
        }

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """生成默认配置."""

        return {
            "quantum_iterations": 128,
            "digital_root_samples": 1024,
            "cosmic_cycles": 256,
            "flops_multiplier": 1.5,
            "enable_cache": True,
        }

    def _get_cached_result(self, key: Tuple[str, int]) -> Optional[BenchmarkResult]:
        if not self.cache_enabled:
            return None
        cached = self.performance_cache.get(key)
        if cached:
            return cached.result
        return None

    def _store_cache(
        self, key: Tuple[str, int], result: BenchmarkResult, duration: float
    ) -> None:
        if not self.cache_enabled:
            return
        self.performance_cache[key] = _CacheEntry(result, duration)
