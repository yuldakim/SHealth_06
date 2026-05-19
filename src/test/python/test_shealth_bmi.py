"""SHealth BMI 단위 테스트 (Activities 3단계)."""

import pytest

from shealth import SHealth


@pytest.fixture
def shealth() -> SHealth:
    return SHealth()


class TestCalculateBmi:
    """BMI 계산 로직 (kg, cm → BMI)."""

    def test_standard_height_and_weight(self, shealth: SHealth) -> None:
        bmi = shealth._calculate_bmi(70.0, 170.0)
        assert bmi == pytest.approx(70.0 / (1.7**2))

    def test_taller_person_lower_bmi_for_same_weight(self, shealth: SHealth) -> None:
        bmi_170 = shealth._calculate_bmi(60.0, 170.0)
        bmi_180 = shealth._calculate_bmi(60.0, 180.0)
        assert bmi_170 > bmi_180

    def test_heavier_person_higher_bmi(self, shealth: SHealth) -> None:
        bmi_light = shealth._calculate_bmi(50.0, 170.0)
        bmi_heavy = shealth._calculate_bmi(80.0, 170.0)
        assert bmi_heavy > bmi_light


class TestReplaceMissingWeights:
    """나이대 평균 체중 보정 (weight == 0)."""

    def test_missing_weight_replaced_by_age_group_average(self, shealth: SHealth) -> None:
        shealth.ages = [25, 25, 25]
        shealth.weights = [60.0, 0.0, 80.0]
        shealth.heights = [170.0, 170.0, 170.0]

        shealth._replace_missing_weights()

        assert shealth.weights[1] == pytest.approx(70.0)

    def test_zero_weight_excluded_from_average(self, shealth: SHealth) -> None:
        shealth.ages = [25, 25, 25]
        shealth.weights = [50.0, 0.0, 0.0]
        shealth.heights = [170.0, 170.0, 170.0]

        shealth._replace_missing_weights()

        assert shealth.weights[1] == pytest.approx(50.0)
        assert shealth.weights[2] == pytest.approx(50.0)

    def test_correction_only_within_same_age_group(self, shealth: SHealth) -> None:
        shealth.ages = [25, 35]
        shealth.weights = [60.0, 0.0]
        shealth.heights = [170.0, 170.0]

        shealth._replace_missing_weights()

        assert shealth.weights[0] == 60.0
        assert shealth.weights[1] == 0.0

    def test_all_missing_in_group_leaves_zero(self, shealth: SHealth) -> None:
        shealth.ages = [25, 25]
        shealth.weights = [0.0, 0.0]
        shealth.heights = [170.0, 170.0]

        shealth._replace_missing_weights()

        assert shealth.weights == [0.0, 0.0]


class TestClassifyBmi:
    """저체중 / 정상 / 과체중 / 비만 분류 (경계값 포함)."""

    @pytest.mark.parametrize(
        ("bmi", "expected"),
        [
            (17.0, SHealth.UNDERWEIGHT),
            (18.5, SHealth.UNDERWEIGHT),
            (18.51, SHealth.NORMALWEIGHT),
            (22.9, SHealth.NORMALWEIGHT),
            (23.0, SHealth.OVERWEIGHT),
            (24.9, SHealth.OVERWEIGHT),
            (25.0, SHealth.OBESITY),
            (30.0, SHealth.OBESITY),
        ],
    )
    def test_bmi_category_boundaries(
        self, shealth: SHealth, bmi: float, expected: int
    ) -> None:
        assert shealth._classify_bmi(bmi) == expected


class TestExceptionsAndFileIo:
    """예외·파일 I/O."""

    def test_missing_file_returns_zero_count(self, shealth: SHealth) -> None:
        assert shealth.calculate_bmi("nonexistent.dat") == 0

    def test_valid_csv_loads_and_returns_count(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "sample.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,70.0,170.0\n"
            "2,26,0.0,165.0\n"
            "3,27,80.0,175.0\n",
            encoding="utf-8",
        )

        count = shealth.calculate_bmi(str(data_file))

        assert count == 3
        assert len(shealth.bmis) == 3
        assert all(bmi > 0 for bmi in shealth.bmis)

    def test_empty_data_rows_after_header(self, shealth: SHealth, tmp_path) -> None:
        data_file = tmp_path / "empty.dat"
        data_file.write_text("id,age,weight,height\n", encoding="utf-8")

        assert shealth.calculate_bmi(str(data_file)) == 0


class TestBmiRatios:
    """나이대별 BMI 비율 집계."""

    def test_ratios_sum_to_one_hundred_per_age_group(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "ratios.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,45.0,170.0\n"
            "2,25,70.0,170.0\n"
            "3,25,85.0,170.0\n",
            encoding="utf-8",
        )
        shealth.calculate_bmi(str(data_file))

        total = sum(
            shealth.get_bmi_ratio(20, bmi_type)
            for bmi_type in (
                SHealth.UNDERWEIGHT,
                SHealth.NORMALWEIGHT,
                SHealth.OVERWEIGHT,
                SHealth.OBESITY,
            )
        )
        assert total == pytest.approx(100.0)

    def test_unknown_age_group_returns_zero(self, shealth: SHealth) -> None:
        assert shealth.get_bmi_ratio(99, SHealth.NORMALWEIGHT) == 0.0


class TestReplaceMissingHeights:
    """나이대 평균 키 보정 (height == 0)."""

    def test_missing_height_replaced_by_age_group_average(self, shealth: SHealth) -> None:
        shealth.ages = [25, 25, 25]
        shealth.heights = [160.0, 0.0, 180.0]
        shealth.weights = [70.0, 70.0, 70.0]

        shealth._replace_missing_heights()

        assert shealth.heights[1] == pytest.approx(170.0)

    def test_zero_height_excluded_from_average(self, shealth: SHealth) -> None:
        shealth.ages = [25, 25, 25]
        shealth.heights = [150.0, 0.0, 0.0]
        shealth.weights = [70.0, 70.0, 70.0]

        shealth._replace_missing_heights()

        assert shealth.heights[1] == pytest.approx(150.0)
        assert shealth.heights[2] == pytest.approx(150.0)


class TestAgeGroupBmiDistribution:
    """특정 연령대 BMI 분포 비율."""

    def test_distribution_matches_get_bmi_ratio(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "age_group.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,45.0,170.0\n"
            "2,25,70.0,170.0\n"
            "3,25,85.0,170.0\n",
            encoding="utf-8",
        )
        shealth.calculate_bmi(str(data_file))

        distribution = shealth.get_age_group_bmi_distribution(20)

        assert distribution[SHealth.UNDERWEIGHT] == pytest.approx(
            shealth.get_bmi_ratio(20, SHealth.UNDERWEIGHT)
        )
        assert sum(distribution.values()) == pytest.approx(100.0)


class TestOverallBmiRatios:
    """전체 사용자 BMI 범주 비율."""

    def test_overall_ratios_sum_to_one_hundred(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "overall.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,45.0,170.0\n"
            "2,35,65.0,170.0\n"
            "3,45,68.0,170.0\n"
            "4,55,90.0,170.0\n",
            encoding="utf-8",
        )
        shealth.calculate_bmi(str(data_file))

        overall = shealth.get_overall_bmi_ratios()
        assert sum(overall.values()) == pytest.approx(100.0)
        assert overall[SHealth.NORMALWEIGHT] == pytest.approx(25.0)


class TestNormalWeightUsers:
    """BMI 정상 범위 사용자 목록."""

    def test_returns_only_normal_category_ids(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "normal.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,45.0,170.0\n"
            "2,25,65.0,170.0\n"
            "3,25,85.0,170.0\n",
            encoding="utf-8",
        )
        shealth.calculate_bmi(str(data_file))

        normal_ids = shealth.get_normal_weight_user_ids()

        assert normal_ids == [2]
