"""BmiCalculator 모듈 단위 테스트."""

import pytest

from bmi_calculator import BmiCalculator
from shealth_constants import BmiCategory


@pytest.fixture
def calculator() -> BmiCalculator:
    return BmiCalculator()


class TestBmiCalculatorCalculate:
    def test_standard_height_and_weight(self, calculator: BmiCalculator) -> None:
        bmi = calculator.calculate(70.0, 170.0)
        assert bmi == pytest.approx(70.0 / (1.7**2))

    def test_taller_person_lower_bmi_for_same_weight(
        self, calculator: BmiCalculator
    ) -> None:
        assert calculator.calculate(60.0, 170.0) > calculator.calculate(60.0, 180.0)

    def test_heavier_person_higher_bmi(self, calculator: BmiCalculator) -> None:
        assert calculator.calculate(80.0, 170.0) > calculator.calculate(50.0, 170.0)

    def test_zero_height_returns_zero_without_error(
        self, calculator: BmiCalculator
    ) -> None:
        assert calculator.calculate(70.0, 0.0) == 0.0

    def test_zero_weight_returns_zero_without_error(
        self, calculator: BmiCalculator
    ) -> None:
        assert calculator.calculate(0.0, 170.0) == 0.0

    def test_calculate_many(self, calculator: BmiCalculator) -> None:
        bmis = calculator.calculate_many([70.0, 0.0], [170.0, 180.0])
        assert len(bmis) == 2
        assert bmis[0] == pytest.approx(70.0 / (1.7**2))
        assert bmis[1] == 0.0


class TestBmiCalculatorClassify:
    @pytest.mark.parametrize(
        ("bmi", "expected"),
        [
            (17.0, BmiCategory.UNDERWEIGHT),
            (18.5, BmiCategory.UNDERWEIGHT),
            (18.51, BmiCategory.NORMALWEIGHT),
            (22.9, BmiCategory.NORMALWEIGHT),
            (23.0, BmiCategory.OVERWEIGHT),
            (24.9, BmiCategory.OVERWEIGHT),
            (25.0, BmiCategory.OBESITY),
            (30.0, BmiCategory.OBESITY),
        ],
    )
    def test_bmi_category_boundaries(
        self, calculator: BmiCalculator, bmi: float, expected: int
    ) -> None:
        assert calculator.classify(bmi) == expected
