# Stage 03 Report — UnitTest 작성

- **Completed**: 2026-05-20
- **Transcript**: `Prompt/stage03-unit-test.md`

## 목표

README Activities 3단계 요구에 따라 리팩토링된 `SHealth` 로직에 대한 단위 테스트를 작성한다.

- BMI 계산 로직 TC
- Age(나이대) 평균치 보정 로직 TC
- 정상/저체중/과체중/비만 분류 TC
- 예외상황 TC

## 수행 내용

- `unittest` 기반 테스트를 **pytest**로 전환하고 `conftest.py`로 import 경로를 정리했다.
- **BMI 계산** (`_calculate_bmi`): 표준 키·몸무게, 동일 체중·키 변화 시 BMI 크기 비교.
- **체중 결측 보정** (`_replace_missing_weights`): 나이대 평균 대체, 0 제외, 타 나이대 미보정, 전원 결측 시 0 유지.
- **BMI 4분류** (`_classify_bmi`): 경계값 18.5, 23, 25를 `@pytest.mark.parametrize`로 검증.
- **예외·I/O**: 파일 없음(0 반환), `tmp_path` CSV 정상 로드, 헤더만 있는 빈 파일.
- **비율 집계**: 한 나이대 내 4분류 비율 합 100%, 미존재 나이대 0 반환.
- 단위 테스트는 `shealth.dat` 전체에 의존하지 않고 인메모리·임시 CSV만 사용한다.

## 결과 및 산출물

| 파일 | 설명 |
|------|------|
| `src/test/python/test_shealth_bmi.py` | pytest 단위 테스트 20건 |
| `src/test/python/conftest.py` | `src/main/python` import 경로 설정 |
| `Report/stage03-unit-test.md` | 본 보고서 |
| `Prompt/stage03-unit-test.md` | 대화 transcript |

검증:

```bash
python -m pytest src/test/python/test_shealth_bmi.py -v
```

- **20 passed** (약 0.09s)

## 이슈 및 해결

- 환경에 `pytest`가 없어 `pip install pytest` 후 실행했다.
- 2단계에서 분리한 private 메서드를 직접 검증해, 리팩토링 단위를 작게 유지하면서 README 요구 TC를 충족했다.

## 다음 단계

4단계(기능 개선): SRP 책임 분리, 연령대 BMI 분포, `height == 0` 보정, 정상 범위 사용자 조회, 전체 BMI 범주 비율 등을 TDD로 확장한다.
