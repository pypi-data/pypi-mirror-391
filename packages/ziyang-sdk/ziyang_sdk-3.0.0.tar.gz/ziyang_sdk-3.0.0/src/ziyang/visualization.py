"""性能可视化工具."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import matplotlib  # type: ignore[import-untyped]

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # type: ignore[import-untyped]  # noqa: E402


def plot_benchmark_metrics(result: Dict[str, Dict], output_path: str) -> Path:
    """根据综合基准结果绘制性能柱状图."""

    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    metrics = result.get("performance_metrics", {})
    names = []
    values = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            names.append(key)
            values.append(value)

    plt.figure(figsize=(6, 4))
    plt.bar(names, values, color="#5271ff")
    plt.ylabel("Value")
    plt.title("Ziyang SDK Performance Metrics")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


def dump_metrics_json(result: Dict[str, Dict], output_path: str) -> Path:
    """将性能结果写入 JSON 文件."""

    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
