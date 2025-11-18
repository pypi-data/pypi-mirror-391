import unittest

from ziyang.math_core import CosmicMath


class TestCosmicMath(unittest.TestCase):
    def test_digital_root_calculation(self) -> None:
        test_cases = [
            (2025, 9),
            (1025, 8),
            (212121, 9),
            (121212, 9),
            (5201, 8),
            (5202, 9),
            (0, 0),
            (-18, 9),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = CosmicMath.digital_root(input_val)
                self.assertEqual(result, expected)

    def test_quantum_convergence(self) -> None:
        result = CosmicMath.quantum_convergence_path(7)
        self.assertEqual(result["final_unit"], 4)
        self.assertEqual(result["convergence_path"], "7×7→49→13→4")
        self.assertEqual(result["steps"], 3)

    def test_multi_state_compression(self) -> None:
        data = {"alpha": 1, "beta": [1, 2, 3]}
        compressed = CosmicMath.multi_state_compression(data)
        self.assertEqual(compressed["original_type"], "dict")
        self.assertGreater(compressed["compressed_length"], 0)
        self.assertEqual(len(compressed["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
