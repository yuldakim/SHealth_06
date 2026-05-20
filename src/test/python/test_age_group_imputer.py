"""AgeGroupImputer 모듈 단위 테스트."""

import pytest

from age_group_imputer import AgeGroupImputer
from bmi_calculator import BmiCalculator


@pytest.fixture
def imputer() -> AgeGroupImputer:
    return AgeGroupImputer()


class TestImputeWeights:
    def test_missing_weight_replaced_by_age_group_average(
        self, imputer: AgeGroupImputer
    ) -> None:
        ages = [25, 25, 25]
        weights = [60.0, 0.0, 80.0]
        imputer.impute_weights(ages, weights)
        assert weights[1] == pytest.approx(70.0)

    def test_zero_weight_excluded_from_average(self, imputer: AgeGroupImputer) -> None:
        ages = [25, 25, 25]
        weights = [50.0, 0.0, 0.0]
        imputer.impute_weights(ages, weights)
        assert weights[1] == pytest.approx(50.0)
        assert weights[2] == pytest.approx(50.0)

    def test_correction_only_within_same_age_group(
        self, imputer: AgeGroupImputer
    ) -> None:
        ages = [25, 35]
        weights = [60.0, 0.0]
        imputer.impute_weights(ages, weights)
        assert weights == [60.0, 0.0]

    def test_all_missing_in_group_leaves_zero(self, imputer: AgeGroupImputer) -> None:
        ages = [25, 25]
        weights = [0.0, 0.0]
        imputer.impute_weights(ages, weights)
        assert weights == [0.0, 0.0]


class TestImputeHeights:
    def test_missing_height_replaced_by_age_group_average(
        self, imputer: AgeGroupImputer
    ) -> None:
        ages = [25, 25, 25]
        heights = [160.0, 0.0, 180.0]
        imputer.impute_heights(ages, heights)
        assert heights[1] == pytest.approx(170.0)

    def test_all_missing_heights_in_group_leaves_zero(
        self, imputer: AgeGroupImputer
    ) -> None:
        ages = [25, 25]
        heights = [0.0, 0.0]
        imputer.impute_heights(ages, heights)
        assert heights == [0.0, 0.0]


class TestAllZeroImputationBmiGuard:
    """나이대 전원 0 보정 후 BMI 계산 시 ZeroDivisionError 없음."""

    def test_all_zero_weights_yield_zero_bmi(self) -> None:
        imputer = AgeGroupImputer()
        calculator = BmiCalculator()
        ages = [25, 25]
        weights = [0.0, 0.0]
        heights = [170.0, 170.0]
        imputer.impute_weights(ages, weights)
        bmis = calculator.calculate_many(weights, heights)
        assert bmis == [0.0, 0.0]

    def test_all_zero_heights_yield_zero_bmi(self) -> None:
        imputer = AgeGroupImputer()
        calculator = BmiCalculator()
        ages = [25, 25]
        weights = [70.0, 70.0]
        heights = [0.0, 0.0]
        imputer.impute_heights(ages, heights)
        bmis = calculator.calculate_many(weights, heights)
        assert bmis == [0.0, 0.0]
