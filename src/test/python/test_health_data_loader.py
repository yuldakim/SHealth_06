"""HealthDataLoader 모듈 단위 테스트."""

from pathlib import Path

import pytest

from health_data_loader import HealthDataLoader, resolve_data_path


@pytest.fixture
def loader() -> HealthDataLoader:
    return HealthDataLoader()


class TestResolveDataPath:
    def test_resolves_relative_path_in_cwd(self, tmp_path) -> None:
        data_file = tmp_path / "sample.dat"
        data_file.write_text("id,age,weight,height\n", encoding="utf-8")
        resolved = resolve_data_path(str(data_file))
        assert resolved == data_file.resolve()

    def test_falls_back_to_repo_root(self, repo_root: Path) -> None:
        resolved = resolve_data_path("shealth.dat")
        assert resolved == (repo_root / "shealth.dat").resolve()


class TestHealthDataLoaderLoad:
    def test_parses_valid_rows(self, loader: HealthDataLoader, tmp_path) -> None:
        data_file = tmp_path / "valid.dat"
        data_file.write_text(
            "id,age,weight,height\n"
            "1,25,70.0,170.0\n"
            "2,26,65.0,165.0\n",
            encoding="utf-8",
        )
        records = loader.load(str(data_file))
        assert len(records) == 2
        assert records[0].user_id == 1
        assert records[1].weight == 65.0

    def test_skips_empty_lines(self, loader: HealthDataLoader, tmp_path) -> None:
        data_file = tmp_path / "sparse.dat"
        data_file.write_text(
            "id,age,weight,height\n\n1,25,70.0,170.0\n",
            encoding="utf-8",
        )
        assert len(loader.load(str(data_file))) == 1

    def test_invalid_row_raises_value_error(
        self, loader: HealthDataLoader, tmp_path
    ) -> None:
        data_file = tmp_path / "bad.dat"
        data_file.write_text(
            "id,age,weight,height\n1,25,70.0\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Invalid CSV row"):
            loader.load(str(data_file))

    def test_non_numeric_raises_value_error(
        self, loader: HealthDataLoader, tmp_path
    ) -> None:
        data_file = tmp_path / "nan.dat"
        data_file.write_text(
            "id,age,weight,height\nx,25,70.0,170.0\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            loader.load(str(data_file))
