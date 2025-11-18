"""性能测试框架."""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _collect_environment() -> Dict[str, Any]:
    """收集运行环境信息."""

    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
    }


def _current_timestamp() -> datetime:
    """生成当前UTC时间戳."""

    return datetime.now(timezone.utc)


@dataclass
class BenchmarkResult:
    """性能测试结果数据结构."""

    name: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=_current_timestamp)
    environment: Dict[str, Any] = field(default_factory=_collect_environment)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""

        return {
            "name": self.name,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
            "environment": self.environment,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """转换为 JSON 格式."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class PerformanceTracker:
    """性能指标收集器."""

    def __init__(self) -> None:
        self.results: List[BenchmarkResult] = []

    def add_result(self, result: BenchmarkResult) -> None:
        """添加测试结果."""

        self.results.append(result)

    def generate_report(self) -> str:
        """生成性能报告."""

        if not self.results:
            return "暂无性能测试结果。"

        lines: List[str] = ["紫阳智库 v3 性能测试报告", "=" * 30]
        for result in self.results:
            lines.append(f"· {result.name}")
            for key, value in result.metrics.items():
                lines.append(f"    - {key}: {value}")
        return "\n".join(lines)
