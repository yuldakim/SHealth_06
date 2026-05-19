"""단일 사용자 건강 기록 모델."""

from dataclasses import dataclass


@dataclass
class HealthRecord:
    user_id: int
    age: int
    weight: float
    height: float
