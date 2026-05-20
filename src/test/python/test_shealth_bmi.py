"""SHealth 파사드·통합 테스트 (public API 중심)."""

import pytest

from shealth import SHealth
from shealth_constants import BmiCategory


@pytest.fixture
def shealth() -> SHealth:
    return SHealth()


class TestCalculateBmiPublicApi:
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
        assert all(bmi >= 0 for bmi in shealth.bmis)

    def test_empty_data_rows_after_header(self, shealth: SHealth, tmp_path) -> None:
        data_file = tmp_path / "empty.dat"
        data_file.write_text("id,age,weight,height\n", encoding="utf-8")
        assert shealth.calculate_bmi(str(data_file)) == 0

    def test_malformed_csv_returns_zero_count(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "malformed.dat"
        data_file.write_text(
            "id,age,weight,height\n1,25,70.0\n",
            encoding="utf-8",
        )
        assert shealth.calculate_bmi(str(data_file)) == 0

    def test_all_zero_weight_in_age_group_no_division_error(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "all_zero_weight.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,0.0,170.0\n"
            "2,25,0.0,170.0\n",
            encoding="utf-8",
        )
        count = shealth.calculate_bmi(str(data_file))
        assert count == 2
        assert shealth.bmis == [0.0, 0.0]

    def test_all_zero_height_in_age_group_no_division_error(
        self, shealth: SHealth, tmp_path
    ) -> None:
        data_file = tmp_path / "all_zero_height.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,70.0,0.0\n"
            "2,25,70.0,0.0\n",
            encoding="utf-8",
        )
        count = shealth.calculate_bmi(str(data_file))
        assert count == 2
        assert shealth.bmis == [0.0, 0.0]


class TestShealthDatSmoke:
    """프로젝트 루트 shealth.dat 통합 스모크."""

    def test_loads_real_dataset(self, shealth: SHealth, shealth_dat) -> None:
        count = shealth.calculate_bmi("shealth.dat")
        assert count > 0
        assert len(shealth.bmis) == count
        assert len(shealth.get_overall_bmi_ratios()) == 4
        assert sum(shealth.get_overall_bmi_ratios().values()) == pytest.approx(
            100.0
        )

    def test_resolve_from_any_cwd(self, shealth: SHealth, shealth_dat) -> None:
        assert shealth_dat.name == "shealth.dat"
        count = shealth.calculate_bmi(str(shealth_dat))
        assert count > 0


class TestBmiRatios:
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
                BmiCategory.UNDERWEIGHT,
                BmiCategory.NORMALWEIGHT,
                BmiCategory.OVERWEIGHT,
                BmiCategory.OBESITY,
            )
        )
        assert total == pytest.approx(100.0)

    def test_unknown_age_group_returns_zero(self, shealth: SHealth) -> None:
        assert shealth.get_bmi_ratio(99, BmiCategory.NORMALWEIGHT) == 0.0


class TestAgeGroupBmiDistribution:
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
        assert distribution[BmiCategory.UNDERWEIGHT] == pytest.approx(
            shealth.get_bmi_ratio(20, BmiCategory.UNDERWEIGHT)
        )
        assert sum(distribution.values()) == pytest.approx(100.0)


class TestOverallBmiRatios:
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
        assert overall[BmiCategory.NORMALWEIGHT] == pytest.approx(25.0)


class TestNormalWeightUsers:
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
        assert shealth.get_normal_weight_user_ids() == [2]
