"""CSV 건강 데이터 로딩."""

import csv
from pathlib import Path

from health_record import HealthRecord

_REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_data_path(filename: str) -> Path:
    """CWD 또는 프로젝트 루트에서 데이터 파일 경로를 찾는다."""
    path = Path(filename)
    if path.is_file():
        return path.resolve()
    root_candidate = _REPO_ROOT / path.name
    if root_candidate.is_file():
        return root_candidate.resolve()
    return path.resolve()


class HealthDataLoader:
    """shealth.dat 형식 CSV를 HealthRecord 목록으로 읽는다."""

    def load(self, filename: str) -> list[HealthRecord]:
        path = resolve_data_path(filename)
        records: list[HealthRecord] = []

        with path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                if not row:
                    continue
                if len(row) < 4:
                    raise ValueError(f"Invalid CSV row (expected 4 columns): {row!r}")
                records.append(
                    HealthRecord(
                        user_id=int(float(row[0])),
                        age=int(float(row[1])),
                        weight=float(row[2]),
                        height=float(row[3]),
                    )
                )

        return records
