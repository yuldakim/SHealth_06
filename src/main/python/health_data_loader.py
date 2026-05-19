"""CSV 건강 데이터 로딩."""

import csv
from pathlib import Path

from health_record import HealthRecord


class HealthDataLoader:
    """shealth.dat 형식 CSV를 HealthRecord 목록으로 읽는다."""

    def load(self, filename: str) -> list[HealthRecord]:
        path = Path(filename)
        records: list[HealthRecord] = []

        with path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                if not row:
                    continue
                records.append(
                    HealthRecord(
                        user_id=int(row[0]),
                        age=int(row[1]),
                        weight=float(row[2]),
                        height=float(row[3]),
                    )
                )

        return records
