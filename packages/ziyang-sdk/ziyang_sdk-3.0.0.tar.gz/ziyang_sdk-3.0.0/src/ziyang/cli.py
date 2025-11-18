"""命令行接口工具."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .core import ZiyangSDK
from .visualization import plot_benchmark_metrics


def _run_single_benchmark(sdk: ZiyangSDK, test: str, iterations: int) -> Dict[str, Any]:
    if test == "quantum":
        result = sdk.benchmark_quantum_convergence(iterations)
        return result.to_dict()
    if test == "digital":
        result = sdk.benchmark_digital_root(iterations)
        return result.to_dict()
    if test == "cosmic":
        result = sdk.benchmark_cosmic_cycles(iterations)
        return result.to_dict()
    return sdk.comprehensive_benchmark()


def run_benchmarks(sdk: ZiyangSDK, args: argparse.Namespace) -> Dict[str, Any]:
    """根据命令行参数运行基准测试."""

    return _run_single_benchmark(sdk, args.test, args.iterations)


def _append_metrics(lines: List[str], label: str, metrics: Dict[str, Any]) -> None:
    lines.append(f"[{label}]")
    for metric, metric_value in metrics.items():
        lines.append(f"  - {metric}: {metric_value}")


def _collect_metric_rows(label: str, metrics: Dict[str, Any]) -> Iterable[List[str]]:
    for metric, metric_value in metrics.items():
        yield [label, metric, str(metric_value)]


def _build_csv_rows(results: Dict[str, Any]) -> List[List[str]]:
    rows: List[List[str]] = [["benchmark", "metric", "value"]]
    if "metrics" in results:
        label = results.get("name", "benchmark")
        rows.extend(_collect_metric_rows(label, results["metrics"]))
    else:
        for key, value in results.items():
            if isinstance(value, dict) and "metrics" in value:
                rows.extend(_collect_metric_rows(key, value["metrics"]))
    return rows


def format_output(results: Dict[str, Any], output_format: str) -> str:
    """根据输出格式格式化结果."""

    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    if output_format == "text":
        lines = ["紫阳智库 v3 性能测试结果"]
        if "metrics" in results:
            label = results.get("name", "benchmark")
            _append_metrics(lines, label, results["metrics"])
        else:
            for key, value in results.items():
                if isinstance(value, dict) and "metrics" in value:
                    _append_metrics(lines, key, value["metrics"])
                else:
                    lines.append(f"{key}: {value}")
        return "\n".join(lines)
    if output_format == "csv":
        rows = _build_csv_rows(results)
        return "\n".join(",".join(row) for row in rows)

    raise ValueError(f"不支持的输出格式：{output_format}")


def _save_output(content: str, path: str) -> Path:
    output_path = Path(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="紫阳智库v3算力测试工具")
    parser.add_argument(
        "--test",
        choices=["quantum", "digital", "cosmic", "all"],
        default="all",
        help="选择测试类型",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="测试迭代次数",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text", "csv"],
        default="text",
        help="输出格式",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="指定文件路径保存输出结果",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="执行后打印性能报告",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="生成性能指标可视化图表",
    )
    parser.add_argument(
        "--visualize-path",
        type=str,
        default="performance_metrics.png",
        help="可视化图表输出路径（默认：performance_metrics.png）",
    )
    args = parser.parse_args()

    print(f"正在执行 {args.test} 基准测试（迭代：{args.iterations}）...")
    sdk = ZiyangSDK()
    results = run_benchmarks(sdk, args)
    formatted = format_output(results, args.output)
    print(formatted)

    if args.save:
        output_path = _save_output(formatted, args.save)
        print(f"结果已保存至 {output_path.resolve()}")

    if args.report:
        print("\n性能报告：")
        print(sdk.performance_tracker.generate_report())

    if args.visualize:
        target = args.visualize_path
        payload = results
        if "performance_metrics" not in payload and "metrics" in payload:
            payload = {
                "performance_metrics": {
                    "operations_per_second": payload["metrics"].get(
                        "operations_per_second", 0
                    ),
                    "total_time_sec": payload["metrics"].get("total_time_sec", 0),
                }
            }
        figure_path = plot_benchmark_metrics(payload, target)
        print(f"可视化图表已保存至 {figure_path.resolve()}")


if __name__ == "__main__":
    main()
