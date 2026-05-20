# Stage 06 Report — 남은 단점 및 개선

- **Completed**: 2026-05-20
- **Transcript**: `Prompt/stage06-remaining-improvements.md`

## 목표

README Activities 6단계: 5단계 회고에서 남긴 기술 부채를 해소하고, 테스트·문서·실행 경로를 실무 수준으로 마무리한다.

## 수행 내용

### 1. `shealth.dat` 경로·CWD 정합 (`pathlib`)

- `health_data_loader.resolve_data_path()`: CWD 상대 경로 우선, 없으면 **프로젝트 루트**(`src/main/python` 기준 `parents[3]`)에서 동일 파일명 탐색
- `shealth_bmi.py`는 `resolve_data_path("shealth.dat")`로 로드 — 루트·`src/main/python` 어디서 실행해도 동작

### 2. 나이대 전원 0 → BMI 0 나누기 가드·TC

- `BmiCalculator.calculate()`: `weight <= 0` 또는 `height_cm <= 0`이면 `0.0` 반환 (ZeroDivisionError 방지)
- `test_age_group_imputer.py` / `test_shealth_bmi.py`에 전원 0 보정 후 BMI 0 검증 TC 추가

### 3. `shealth.py` 정리

- 미사용 private 래퍼 제거: `_calculate_bmi`, `_classify_bmi`, `_age_groups`, `_is_in_age_group`, `_average_weight_for_age_group`
- `AgeGroupImputer._average_for_age_group` private 우회 제거
- `BmiCategory`·상수 **이중 노출** 제거 → `shealth_constants.BmiCategory` / `AgeGroupConfig` 단일 출처
- CSV 파싱 오류 시 `ValueError` catch 후 count 0 반환

### 4. 모듈·public API 테스트 보강

| 파일 | 역할 |
|------|------|
| `test_bmi_calculator.py` | 계산·분류·0 가드 (14건) |
| `test_age_group_imputer.py` | 체중·키 보정·전원 0 (8건) |
| `test_health_data_loader.py` | 경로 해석·CSV·비정상 행 (6건) |
| `test_shealth_bmi.py` | 파사드 public API·스모크·극단 케이스 (13건) |

- 실제 `shealth.dat` **통합 스모크** 2건 (`1e+05` 과학적 표기 ID 행 포함 → `int(float())` 파싱 보완)

### 5. `pytest-cov`·README 동기화

- `pip install pytest pytest-cov` 안내
- 전체 테스트·커버리지 명령 추가
- 프로젝트 구조를 7개 모듈 + 4개 테스트 파일로 갱신

### 6. `activities-stage-delivery` 6단계 지원

- `stages.json` stage 6 (`remaining-improvements`) 추가
- `finalize_stage.py`: `--stage` 1~6, README 6단계 체크박스 마킹

## 결과 및 산출물

| 항목 | 결과 |
|------|------|
| 테스트 | **41 passed** (이전 25건 → +16건) |
| 커버리지 | **89%** (`shealth_bmi.py` CLI 미실행 0% 제외 시 핵심 모듈 96~100%) |
| 수정 모듈 | `health_data_loader`, `bmi_calculator`, `shealth`, `shealth_bmi` |
| 신규 테스트 | `test_bmi_calculator`, `test_age_group_imputer`, `test_health_data_loader` |

```bash
python -m pytest src/test/python -v
python -m pytest src/test/python --cov=src/main/python --cov-report=term-missing
```

## 이슈 및 해결

| 이슈 | 해결 |
|------|------|
| `shealth.dat` 일부 ID가 `1e+05` 과학적 표기 | `int(float(row[0]))`로 파싱 — 스모크 TC에서 발견 |
| PowerShell `&&` 미지원 | `;` 구분자로 명령 실행 |
| `finalize_stage`가 5단계까지만 지원 | `stages.json`·`choices=range(1,7)` 확장 |

## 다음 단계

- Activities 1~6 전체 완료 — (선택) `shealth_bmi.py` CLI용 소수 스모크 TC로 커버리지 90%+ 달성
- (선택) `list[HealthRecord]` 중심 내부 모델로 병렬 리스트 제거
