from ziyang.core import ZiyangSDK
from ziyang.utils import format_result


def test_sdk_benchmark_results():
    sdk = ZiyangSDK()
    quantum = sdk.benchmark_quantum_convergence(10)
    assert quantum.metrics["iterations"] == 10
    assert quantum.metrics["operations_per_second"] > 0

    digital = sdk.benchmark_digital_root(20)
    assert digital.metrics["data_size"] == 20
    assert digital.metrics["max_digital_root"] <= 9

    cosmic = sdk.benchmark_cosmic_cycles(15)
    assert cosmic.metrics["cycles"] == 15


def test_format_result():
    assert format_result(10) == "计算结果：10"


def test_register_strategy_factory():
    sdk = ZiyangSDK()

    def factory():
        def strategy(data):
            return [value * 2 for value in data]

        return strategy

    sdk.optimizer.register_strategy_factory("custom_strategy", factory, override=True)
    assert "custom_strategy" in sdk.optimizer.available_strategies()

    result = sdk.optimizer.optimize_algorithm("custom_strategy", [1, 2, 3])
    assert result == [2, 4, 6]
