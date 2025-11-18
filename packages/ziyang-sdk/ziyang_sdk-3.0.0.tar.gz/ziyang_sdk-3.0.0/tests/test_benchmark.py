from ziyang.benchmark import BenchmarkResult, PerformanceTracker


def test_benchmark_result_to_dict_and_json():
    result = BenchmarkResult(
        name="test",
        metrics={"value": 1},
        metadata={"note": "sample"},
    )
    data = result.to_dict()
    assert data["name"] == "test"
    assert data["metrics"]["value"] == 1

    json_payload = result.to_json()
    assert '"value": 1' in json_payload


def test_performance_tracker_report():
    tracker = PerformanceTracker()
    tracker.add_result(BenchmarkResult(name="alpha", metrics={"foo": 1, "bar": 2}))
    report = tracker.generate_report()
    assert "alpha" in report
    assert "foo" in report
