"""BMI 집계·비율·사용자 조회."""

from shealth_constants import ALL_BMI_CATEGORIES, AgeGroupConfig, BmiCategory

from bmi_calculator import BmiCalculator


class BmiAnalytics:
    """나이대별·전체 BMI 통계와 정상 범위 사용자 목록."""

    def __init__(self, calculator: BmiCalculator | None = None) -> None:
        self._calculator = calculator or BmiCalculator()

    def age_group_distribution(
        self,
        ages: list[int],
        bmis: list[float],
        age_group: int,
        age_step: int = AgeGroupConfig.STEP,
    ) -> dict[int, float]:
        """특정 연령대의 BMI 4분류 비율(%)을 반환한다."""
        counts = self._count_categories_in_age_group(
            ages, bmis, age_group, age_step
        )
        return self._counts_to_percentages(counts)

    def overall_distribution(self, bmis: list[float]) -> dict[int, float]:
        """전체 사용자 대비 각 BMI 범주 비율(%)을 반환한다."""
        counts = {category: 0 for category in ALL_BMI_CATEGORIES}
        for bmi in bmis:
            counts[self._calculator.classify(bmi)] += 1
        return self._counts_to_percentages(counts)

    def normal_weight_user_ids(
        self,
        user_ids: list[int],
        bmis: list[float],
    ) -> list[int]:
        """BMI 정상 범위(18.5 초과 23 미만) 사용자 ID 목록."""
        return [
            user_id
            for user_id, bmi in zip(user_ids, bmis)
            if self._calculator.classify(bmi) == BmiCategory.NORMALWEIGHT
        ]

    def build_age_group_ratios(
        self,
        ages: list[int],
        bmis: list[float],
        age_start: int = AgeGroupConfig.START,
        age_stop: int = AgeGroupConfig.STOP,
        age_step: int = AgeGroupConfig.STEP,
    ) -> dict[tuple[int, int], float]:
        """나이대 × BMI 유형별 비율 맵 (기존 get_bmi_ratio용)."""
        ratios: dict[tuple[int, int], float] = {}
        for age_group in range(age_start, age_stop, age_step):
            distribution = self.age_group_distribution(
                ages, bmis, age_group, age_step
            )
            for bmi_type, percentage in distribution.items():
                if percentage > 0:
                    ratios[(age_group, bmi_type)] = percentage
        return ratios

    def _count_categories_in_age_group(
        self,
        ages: list[int],
        bmis: list[float],
        age_group: int,
        age_step: int,
    ) -> dict[int, int]:
        counts = {category: 0 for category in ALL_BMI_CATEGORIES}
        for age, bmi in zip(ages, bmis):
            if age_group <= age < age_group + age_step:
                counts[self._calculator.classify(bmi)] += 1
        return counts

    @staticmethod
    def _counts_to_percentages(counts: dict[int, int]) -> dict[int, float]:
        total = sum(counts.values())
        if total == 0:
            return {category: 0.0 for category in counts}
        return {
            category: count * 100.0 / total
            for category, count in counts.items()
        }
