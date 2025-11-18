"""通用工具函数."""

from __future__ import annotations

import json
from typing import Any, Dict

from .benchmark import BenchmarkResult


def format_result(result: Any, prefix: str = "计算结果：") -> str:
    """格式化普通结果输出."""

    return f"{prefix}{result}"


def format_benchmark_result(result: BenchmarkResult) -> str:
    """格式化性能测试结果."""

    payload: Dict[str, Any] = result.to_dict()
    return json.dumps(payload, ensure_ascii=False, indent=2)
