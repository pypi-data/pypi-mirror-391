紫阳智库 v3 SDK
================

概述
----
紫阳智库 v3 SDK 提供量子收敛、数字根、宇宙循环等算力基准测试能力，内置性能框架、数学工具与命令行接口，可用于快速评估算法性能并生成报告。

主要特性
--------
- `ZiyangSDK` 核心类：量子收敛、数字根、宇宙循环测试及综合性能汇总。
- `CosmicMath` 数学库：数字根 O(1) 计算、量子收敛路径、多态压缩摘要。
- `BenchmarkResult`/`PerformanceTracker`：支持指标记录、报告生成与 JSON 导出。
- CLI 工具：支持 JSON/TEXT/CSV 输出、保存结果、打印性能报告。
- `PerformanceOptimizer`：支持内置与自定义优化策略、缓存开关控制。
- 支持注册自定义策略及工厂，便于扩展批量优化逻辑。
- 文档与示例：安装指南、快速上手、故障排除、性能总结及多种示例脚本。

快速开始
--------
1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
2. 运行测试与质量检查：
   ```
   python -m flake8 src scripts examples tests
   python -m mypy src
   pytest
   ```
3. 命令行体验：
   ```
   python -m ziyang --test all --output text --report
   python -m ziyang --test quantum --iterations 256 --output csv --save results.csv
   python -m ziyang --test all --visualize --visualize-path figures/summary.png
   ```

示例脚本
--------
- `examples/basic_usage.py`：基础能力演示
- `examples/advanced_usage.py`：自定义配置与结果保存
- `examples/performance_report.py`：批量运行并打印性能报告
- `examples/custom_optimizer.py`：注册自定义量子收敛优化策略（含工厂示例）
- `examples/performance_report.py`：批量运行并打印性能报告
- `examples/visualize_performance.py`：生成性能指标图表

文档
----
- 安装指南：`docs/installation.md`
- 快速上手：`docs/getting_started.md`
- API 参考：`docs/api_reference.md`
- 故障排除：`docs/troubleshooting.md`
- 性能总结：`docs/performance_summary.md`
- 发布流程：`docs/release_plan.md`
- 后续规划：`docs/roadmap_next.md`
- 优化策略扩展：`docs/optimizer_guide.md`

打包与发布
----------
```
python -m build
```
生成的 `dist/` 目录包含 `sdist` 与 `wheel`，可用于发布至 PyPI 或内部仓库。发布前请更新 `CHANGELOG.md` 与版本号。

最终验证
--------
```
python scripts/final_validation.py
type validation_report.json
```
该脚本涵盖功能、性能、兼容性及稳定性检查，CI 会自动运行并展示结果。

