"""紫阳智库 v3 数学核心库实现."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


class CosmicMath:
    """宇宙编码数学核心库."""

    @staticmethod
    def digital_root(n: int) -> int:
        """O(1) 数字根算法实现."""

        if not isinstance(n, int):
            raise TypeError("digital_root 仅接受整数输入")
        if n < 0:
            n = abs(n)

        if n == 0:
            return 0
        return 1 + ((n - 1) % 9)

    @staticmethod
    def quantum_convergence_path(base: int) -> Dict[str, Any]:
        """量子收敛路径计算."""

        if not isinstance(base, int):
            raise TypeError("quantum_convergence_path 仅接受整数输入")
        if base <= 0:
            raise ValueError("base 必须为正整数")

        segments: List[str] = [f"{base}×{base}"]
        value = base * base
        segments.append(str(value))

        while value >= 10:
            value = sum(int(digit) for digit in str(value))
            segments.append(str(value))

        return {
            "base": base,
            "final_unit": value,
            "convergence_path": "→".join(segments),
            "steps": len(segments) - 1,
        }

    @staticmethod
    def multi_state_compression(data: Any) -> Dict[str, Any]:
        """多态压缩算法（序列化摘要实现）."""

        try:
            serialized = json.dumps(
                data,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("data 无法序列化为 JSON") from exc

        digest = hashlib.sha256(serialized).hexdigest()
        return {
            "original_type": type(data).__name__,
            "compressed_length": len(serialized),
            "digest": digest,
        }
