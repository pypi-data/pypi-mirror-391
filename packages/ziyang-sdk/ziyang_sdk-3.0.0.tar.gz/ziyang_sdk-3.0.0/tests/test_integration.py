import unittest

from ziyang.core import ZiyangSDK


class TestSDKIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.sdk = ZiyangSDK()

    def test_comprehensive_benchmark(self) -> None:
        result = self.sdk.comprehensive_benchmark()

        self.assertIn("quantum_convergence", result)
        self.assertIn("digital_root", result)
        self.assertIn("cosmic_cycles", result)

        self.assertIn("performance_metrics", result)
        metrics = result["performance_metrics"]
        self.assertIn("total_operations_per_second", metrics)
        self.assertIn("estimated_flops", metrics)
        self.assertGreater(metrics["total_operations_per_second"], 0)


if __name__ == "__main__":
    unittest.main()
