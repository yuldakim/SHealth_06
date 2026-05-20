"""S-Health BMI 파사드: 로딩·보정·계산·통계를 조율한다."""

from age_group_imputer import AgeGroupImputer
from bmi_analytics import BmiAnalytics
from bmi_calculator import BmiCalculator
from health_data_loader import HealthDataLoader
from shealth_constants import AgeGroupConfig


class SHealth:
    """S-Health BMI 계산·통계 파사드 (Activities 4단계 SRP 분리)."""

    def __init__(self) -> None:
        self._loader = HealthDataLoader()
        self._imputer = AgeGroupImputer()
        self._calculator = BmiCalculator()
        self._analytics = BmiAnalytics(self._calculator)
        self._reset_data()

    def _reset_data(self) -> None:
        self.count = 0
        self.user_ids: list[int] = []
        self.ages: list[int] = []
        self.heights: list[float] = []
        self.weights: list[float] = []
        self.bmis: list[float] = []
        self._bmi_ratios: dict[tuple[int, int], float] = {}
        self._overall_bmi_ratios: dict[int, float] = {}

    def calculate_bmi(self, filename: str) -> int:
        """파일에서 데이터를 읽어 BMI를 계산한다."""
        self._reset_data()

        if not self._load_records(filename):
            return 0

        self._replace_missing_weights()
        self._replace_missing_heights()
        self._calculate_bmis()
        self._calculate_bmi_ratios()
        self._overall_bmi_ratios = self._analytics.overall_distribution(
            self.bmis
        )

        return self.count

    def get_bmi_ratio(self, age_class: int, bmi_type: int) -> float:
        """나이대와 BMI 유형에 따른 비율을 반환한다."""
        return self._bmi_ratios.get((age_class, bmi_type), 0.0)

    def get_age_group_bmi_distribution(self, age_group: int) -> dict[int, float]:
        """특정 연령대의 BMI 4분류 비율(%)을 반환한다."""
        return self._analytics.age_group_distribution(
            self.ages, self.bmis, age_group, AgeGroupConfig.STEP
        )

    def get_overall_bmi_ratios(self) -> dict[int, float]:
        """전체 사용자 대비 각 BMI 범주 비율(%)을 반환한다."""
        return dict(self._overall_bmi_ratios)

    def get_normal_weight_user_ids(self) -> list[int]:
        """BMI 정상 범위 사용자 ID 목록."""
        return self._analytics.normal_weight_user_ids(self.user_ids, self.bmis)

    def _load_records(self, filename: str) -> bool:
        try:
            records = self._loader.load(filename)
        except FileNotFoundError:
            print(f"Failed to open file: {filename}")
            return False
        except ValueError as exc:
            print(f"Failed to parse file: {filename} — {exc}")
            return False

        self.user_ids = [record.user_id for record in records]
        self.ages = [record.age for record in records]
        self.weights = [record.weight for record in records]
        self.heights = [record.height for record in records]
        self.count = len(self.ages)
        return True

    def _replace_missing_weights(self) -> None:
        self._imputer.impute_weights(self.ages, self.weights)

    def _replace_missing_heights(self) -> None:
        self._imputer.impute_heights(self.ages, self.heights)

    def _calculate_bmis(self) -> None:
        self.bmis = self._calculator.calculate_many(self.weights, self.heights)

    def _calculate_bmi_ratios(self) -> None:
        self._bmi_ratios = self._analytics.build_age_group_ratios(
            self.ages,
            self.bmis,
            AgeGroupConfig.START,
            AgeGroupConfig.STOP,
            AgeGroupConfig.STEP,
        )
