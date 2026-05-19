# Stage 05 Report — 회고 및 발표

- **Completed**: 2026-05-20
- **Transcript**: `Prompt/stage05-retrospective.md`

## 목표

README Activities 5단계: 6시간 실습 전체를 돌아보며 목표 달성도, 코드 품질 변화, 생성형 AI·테스트·클린코드 관점의 회고를 정리한다.

- 실습 목표와 달성도
- 코드 품질 Before & After
- AI 활용 방식(도움·한계)
- TC 추가가 개선에 미친 영향, TC 작성 팁
- 클린코드·리팩토링 소감

## 수행 내용

### 1. 실습 목표와 달성도

| 목표 (README) | 달성 | 비고 |
|---------------|------|------|
| 문제 코드 분석·코드 스멜 식별 | ✅ | God method, BMI=25 미분류, 경로/CWD 이슈 등 문서화 |
| 1차 리팩토링(네이밍·상수·함수 추출·중복 제거) | ✅ | `calculate_bmi` 단계별 private 메서드 분리 |
| UnitTest (BMI·보정·분류·예외) | ✅ | pytest 20건 → 4단계 후 **25건** |
| 기능 개선(SRP·연령대 분포·키 보정·정상 사용자·전체 비율) | ✅ | 7개 모듈 + 파사드 구조 |
| 회고 및 발표 | ✅ | 본 Report |

**도메인 요구사항**: 체중 0 나이대 평균 보정, BMI 4분류, `shealth.dat` 기반 통계 — 모두 구현·테스트로 검증됨. 4단계에서 **키(height) 0 보정**까지 스펙을 보완했다.

### 2. 코드 품질 Before & After

#### Before (1단계 초기)

- 단일 `SHealth` 클래스에 I/O·보정·계산·통계가 한 메서드에 집중
- 병렬 리스트(`ages`, `weights`, …)로 레코드 무결성을 호출부가 관리
- BMI 경계 `> 25`로 **BMI=25 미분류** 버그
- 나이대 `range(20, 80, 10)`·BMI 리터럴 **3회 이상 반복**
- `get_bmi_ratio(age, 100|200|…)` 매직 넘버
- 실행 경로에 따라 `shealth.dat`를 찾지 못하는 CWD 의존
- unittest 3건 수준(비율 0~100, 파일 없음만)

#### After (4단계 완료 시점)

```
shealth_constants.py   — 도메인 상수
health_record.py       — 1건 모델
health_data_loader.py  — CSV 로딩
age_group_imputer.py   — 체중·키 결측 보정
bmi_calculator.py      — BMI 계산·분류
bmi_analytics.py       — 연령대/전체 비율·정상 사용자
shealth.py             — 파이프라인 파사드
shealth_bmi.py         — CLI 출력
test_shealth_bmi.py    — pytest 25건
```

- **SRP**: 역할별 모듈, `SHealth`는 조율만
- **테스트 가능성**: 인메모리·`tmp_path`로 파일 전체에 의존하지 않음
- **버그 수정**: BMI ≥25 비만, 빈 행 처리, 경계 parametrize
- **공개 API 유지**: `calculate_bmi`, `get_bmi_ratio`로 하위 호환

검증: `python -m pytest src/test/python/test_shealth_bmi.py -v` → **25 passed**

### 3. 생성형 AI 활용 — 도움이 된 순간과 한계

**도움이 된 순간**

- **1단계**: 대량 코드·README·`.cursorrules`를 한 번에 읽고 스멜·스펙 불일치를 표로 정리 — 사람이 놓치기 쉬운 BMI=25, 빈 줄 `break` 등을 빠르게 목록화
- **2~3단계**: 리팩토링 후 깨질 수 있는 public API를 유지한 채 함수 추출·pytest 전환·경계값 TC 초안을 제안
- **4단계**: SRP 분리 시 모듈 경계(로더 / imputer / calculator / analytics) 제안과 신규 API(`get_age_group_bmi_distribution` 등) 구현 가속
- **단계 마감**: `@activities-stage-delivery`로 Report·Prompt·README·Git을 동일 규칙으로 반복 — 산출물 누락 감소

**한계**

- 실행 경로·데이터 파일 위치는 **실제 실행 결과** 없이는 확신하기 어려움 → 루트/`src/main/python` 양쪽 확인 필요
- TC 데이터(예: 70 kg / 170 cm)가 스펙 경계와 어긋나 **과체중으로 분류**되는 경우 — AI 제안만 믿지 않고 BMI 수치를 직접 계산해 검증해야 함
- 대화 transcript export는 jsonl에 `[REDACTED]`가 많을 수 있어, 중요한 결정은 Report에 반드시 남겨야 함

### 4. TC가 개선에 미친 영향 · TC 작성 팁

**영향**

- BMI **경계값 parametrize**(18.5, 23, 25)가 `>= 25` 수정의 **회귀 방지 장치**가 됨
- 체중·키 보정 TC가 4단계 `impute_heights` 추가 후에도 동일 패턴으로 확장 가능했음
- 정상 사용자 목록 TC 작성 중 “정상” 샘플 데이터가 실제로는 과체중임을 발견 → 테스트·도메인 이해 동시 개선
- `shealth.dat` 전체 의존을 줄여 **CI·로컬 속도**(25건 ≈ 0.12s)와 실패 원인 분리에 유리

**작성 팁**

1. **경계값을 표로 정리한 뒤** `@pytest.mark.parametrize`로 한 번에 고정
2. 결측 보정은 “대상 나이대만 바뀌는지”, “전원 0이면 0 유지”처럼 **부정 케이스**를 짝으로 작성
3. 통합 TC(실제 `shealth.dat`)는 소수만 두고, 나머지는 **합성 레코드·tmp_path**
4. 리팩토링 단계마다 **기존 public API TC를 먼저 통과**시킨 다음 내부 구조 변경

### 5. 클린코드·리팩토링 — 장점과 어려운 점

**장점**

- 작은 함수·모듈 단위로 읽기 쉬워지고, AI·동료에게 “어디를 고칠지” 맥락 전달이 쉬움
- 상수·`BmiCategory`로 의도가 드러나 `100|200` 매직 넘버 제거
- 테스트가 리팩토링 **안전망**이 되어 4단계 대규모 분리도 단계적으로 진행 가능

**어려운 점**

- 병렬 리스트 → `HealthRecord` 전환은 **범위가 커져** 한 번에 하기보다 파사드 뒤에 점진적 분리가 현실적
- 파사드에 legacy private 메서드(`_calculate_bmi` 등)가 남아 **중복 느낌** — 호환성과 정리 사이 트레이드오프
- README 실행 경로와 데이터 위치 불일치는 **문서·코드 양쪽**을 맞춰야 하며, 코드만으로는 해결되지 않음

## 결과 및 산출물

| 산출물 | 경로 |
|--------|------|
| 회고 Report | `Report/stage05-retrospective.md` |
| 대화 Transcript | `Prompt/stage05-retrospective.md` |
| README 5단계 체크 | `[x]` 갱신 |
| Git | `docs(stage05): 회고 및 발표 — Report 및 Prompt transcript 추가` |

**전체 Activities 산출물 요약**

| Stage | Report / Prompt |
|-------|-----------------|
| 1 | `stage01-code-analysis.md` |
| 2 | `stage02-first-refactoring.md` |
| 3 | `stage03-unit-test.md` |
| 4 | `stage04-feature-improvement.md` |
| 5 | `stage05-retrospective.md` |

## 이슈 및 해결

| 이슈 | 해결 |
|------|------|
| 1~4단계는 이미 코드·Report 완료, 5단계만 미체크 | 회고 Report 작성 후 `finalize_stage.py --stage 5`로 Prompt·README·Git 일괄 처리 |
| 회고 시 “Before” 기억 희석 | `Report/stage01~04` 및 git history(`faca2bd` ~ `834d387`)를 기준으로 Before/After 정리 |

## 다음 단계

- (선택) `Refactoring` 브랜치에 `feature` 변경사항 merge 및 팀 발표 자료(슬라이드)로 본 Report 요약 이식
- (선택) 병렬 리스트를 `list[HealthRecord]` 중심으로 바꾸는 추가 리팩토링
- (선택) `shealth_bmi.py` 실행 시 프로젝트 루트 기준 `shealth.dat` 경로를 `pathlib`로 고정해 README와 실행 경로 일치
