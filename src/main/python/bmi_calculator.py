"""BMI 수치 계산 및 4분류."""

from shealth_constants import (
    BmiCategory,
    BmiThresholds,
    CENTIMETERS_PER_METER,
)


class BmiCalculator:
    """체중·키(cm)로 BMI를 계산하고 범주로 분류한다."""

    def calculate(self, weight: float, height_cm: float) -> float:
        height_m = height_cm / CENTIMETERS_PER_METER
        return weight / (height_m**2)

    def calculate_many(
        self, weights: list[float], heights: list[float]
    ) -> list[float]:
        return [
            self.calculate(weight, height)
            for weight, height in zip(weights, heights)
        ]

    def classify(self, bmi: float) -> int:
        if bmi <= BmiThresholds.UNDERWEIGHT_MAX:
            return BmiCategory.UNDERWEIGHT
        if bmi < BmiThresholds.NORMAL_MAX:
            return BmiCategory.NORMALWEIGHT
        if bmi < BmiThresholds.OVERWEIGHT_MAX:
            return BmiCategory.OVERWEIGHT
        return BmiCategory.OBESITY
