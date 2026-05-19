# Stage 04 Report — 기능 개선

- **Completed**: 2026-05-20
- **Transcript**: `Prompt/stage04-feature-improvement.md`

## 목표

README Activities 4단계 요구를 순차적으로 수행한다.

- SRP에 따른 책임 분리 리팩토링
- 특정 연령대의 BMI 분포 비율 계산 기능 추가
- Height가 0인 경우에 대한 평균치 보정 로직 추가
- BMI 정상 범위 사용자 목록 조회 기능 추가
- 전체 사용자 대비 각 BMI 범주 비율 계산 기능 추가

## 수행 내용

### 1. SRP 책임 분리

`SHealth` 단일 클래스에 모이던 역할을 모듈별로 분리하고, `SHealth`는 파사드로 조율만 담당한다.

| 모듈 | 책임 |
|------|------|
| `shealth_constants.py` | BMI·나이대 상수 |
| `health_record.py` | 사용자 1건 모델 |
| `health_data_loader.py` | CSV 로딩 |
| `age_group_imputer.py` | 체중·키 결측(0) 나이대 평균 보정 |
| `bmi_calculator.py` | BMI 계산·4분류 |
| `bmi_analytics.py` | 연령대/전체 비율·정상 사용자 조회 |
| `shealth.py` | 파이프라인 조율·기존 public API 유지 |

### 2. 연령대 BMI 분포

- `get_age_group_bmi_distribution(age_group)` — 해당 연령대 4분류 비율(%) dict 반환
- 기존 `get_bmi_ratio()`와 동일 집계를 `BmiAnalytics`에서 일원화

### 3. 키(height) 0 보정

- `AgeGroupImputer.impute_heights()` — 체중 보정과 동일한 나이대 평균 로직
- `calculate_bmi()` 파이프라인: 체중 보정 → **키 보정** → BMI 계산

### 4. 정상 범위 사용자 목록

- `get_normal_weight_user_ids()` — BMI 정상(18.5 초과 23 미만) 사용자 ID 목록

### 5. 전체 BMI 범주 비율

- `get_overall_bmi_ratios()` — 전체 사용자 기준 4분류 비율(%)

### 6. 진입점·테스트

- `shealth_bmi.py` — 연령대 분포, 전체 비율, 정상 사용자 미리보기 출력
- `test_shealth_bmi.py` — 키 보정·분포·전체 비율·정상 사용자 TC 5건 추가 (총 25건)

## 결과 및 산출물

| 파일 | 설명 |
|------|------|
| `src/main/python/shealth_constants.py` | 상수 |
| `src/main/python/health_record.py` | HealthRecord |
| `src/main/python/health_data_loader.py` | CSV 로더 |
| `src/main/python/age_group_imputer.py` | 체중·키 보정 |
| `src/main/python/bmi_calculator.py` | BMI 계산·분류 |
| `src/main/python/bmi_analytics.py` | 통계·조회 |
| `src/main/python/shealth.py` | 파사드 |
| `src/main/python/shealth_bmi.py` | main 출력 확장 |
| `src/test/python/test_shealth_bmi.py` | pytest 25건 |

검증:

```bash
python -m pytest src/test/python/test_shealth_bmi.py -v
```

- **25 passed**

## 이슈 및 해결

- 정상 BMI TC 초기 데이터(70 kg / 170 cm)는 BMI ≈ 24.2로 **과체중**에 해당해 실패했다. 경계에 맞게 65 kg 등으로 조정해 4분류·정상 사용자 검증을 안정화했다.
- 3단계에서 쓰던 `_calculate_bmi`, `_replace_missing_weights`, `_classify_bmi` 등은 파사드에 유지해 기존 테스트 호환성을 확보했다.

## 다음 단계

5단계(회고 및 발표): Before/After, AI 활용, TC 영향, 클린코드 소감을 정리한다.
