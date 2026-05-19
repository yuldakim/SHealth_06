# Stage 01 Report — 문제 코드 분석 및 코드 스멜 찾기

- **Completed**: 2026-05-19
- **Transcript**: `Prompt/stage01-code-analysis.md`

## 목표

README Activities 1단계: 기존 SHealth BMI 코드의 **구조·도메인 로직(BMI·나이대·결측 보정)** 을 이해하고, 리팩토링·테스트·기능 개선의 기반이 될 **코드 스멜·결함 후보**를 식별한다.

## 수행 내용

### 1. 코드 구조 및 실행 흐름

| 파일 | 역할 |
|------|------|
| `src/main/python/shealth.py` | `SHealth` 클래스 — CSV 로드, 체중 결측 보정, BMI 계산, 나이대별 BMI 비율 저장 |
| `src/main/python/shealth_bmi.py` | `main()` — `calculate_bmi("shealth.dat")` 호출 후 20~70대 비율 출력 |
| `src/test/python/test_shealth_bmi.py` | unittest — 레코드 수, 비율 범위, 잘못된 파일 |
| `shealth.dat` | 약 4,800행 CSV (`id,age,weight,height`) |

**처리 순서 (`calculate_bmi`)**

1. CSV 읽기 → `ages`, `weights`, `heights` 병렬 리스트에 적재  
2. 나이대 `20, 30, …, 70` (`range(20, 80, 10)`)마다 유효 체중(≠0) 평균 산출 → `weight == 0` 보정  
3. `BMI = weight / (height_cm/100)²`  
4. 동일 나이대 구간별 저체중/정상/과체중/비만 인원 비율(%)을 `_bmi_ratios`에 저장  

**실행 경로 이슈**: README는 `cd src/main/python` 후 실행을 안내하나, `shealth.dat`는 **프로젝트 루트**에 있어 해당 경로에서는 `FileNotFoundError` → 0건 처리·전부 0% 출력. 루트에서 실행 시 정상(예: 20대 비만 약 60.86%).

### 2. 도메인 로직 정리 (README·`.cursorrules` 기준)

| 항목 | 스펙 |
|------|------|
| 결측 | `weight == 0` → 동일 나이대(`a ≤ age < a+10`) 유효 체중 평균으로 대체 |
| BMI | `kg / (m)²`, `m = cm / 100` |
| 분류 | ≤18.5 저체중, 18.5&lt;BMI&lt;23 정상, 23≤BMI&lt;25 과체중, **BMI≥25 비만** |

데이터: `shealth.dat`에 `weight=0` 레코드 **1건** (예: id 93730, age 57).

### 3. 코드 스멜 및 결함 후보

#### 구조·책임 (SRP / God Method)

- **`calculate_bmi`가 파일 I/O, 파싱, 결측 보정, BMI 계산, 통계까지 전부 수행** — 단일 책임 위반, 테스트·재사용 어려움 (4단계 SRP 분리 대상).
- **병렬 리스트** (`ages`, `heights`, `weights`, `bmis`) — 레코드 단위 모델 없음, 인덱스 동기화 부담.

#### 중복·하드코딩

- 나이대 루프 `for a in range(20, 80, 10)` **3회 반복** (보정·통계·main 출력).
- BMI 경계 `18.5`, `23`, `25` **리터럴 반복** — 상수/테이블화 필요.
- `shealth_bmi.py`에서 `get_bmi_ratio(age, 100|200|300|400)` — 클래스 상수(`UNDERWEIGHT` 등) 미사용 **매직 넘버**.

#### 로직·정확성

| 이슈 | 코드/현상 | 영향 |
|------|-----------|------|
| **BMI=25 미분류** | `elif self.bmis[i] > 25:` (85행) | 스펙은 **≥25 비만**인데 25.0은 어느 범주에도 포함 안 됨 |
| 빈 행 처리 | `if not row: break` (37–38행) | 빈 줄 이후 데이터 **전부 무시** (`continue`가 적절) |
| 키 0 미처리 | height=0 시 `(h/100)²` 분모 0 | 4단계 요구사항; 현재 예외·Inf 가능 |
| 20대 미만·80세 이상 | 나이대 루프 밖 연령 | 보정·비율 통계 **제외** (의도 확인 필요) |

#### 오류 처리·경로

- `FileNotFoundError` 시 `print` 후 `return 0` — 호출자가 실패와 빈 데이터 구분 어려움.
- 데이터 파일 경로 **상대 경로 고정** — CWD에 의존 (실행 위치 버그).

#### 네이밍·가독성

- `UNDERWEIGHT = 100` 등 — BMI **카테고리 코드**이지 비율(%)이 아님, 이름과 값이 혼동됨.
- `count` vs `len(ages)` — `count`와 리스트 길이 이중 관리.

#### 성능 (현 단계 참고)

- 나이대×전체 인덱스 **중첩 이중·삼중 루프** — 데이터 규모에서는 허용 가능하나 동일 패턴 반복.

#### 테스트

- `shealth.dat` **경로·CWD 의존** — README 실행 경로와 불일치 시 실패 가능.
- BMI 경계값·결측 보정·분류별 건수 **미검증** (3단계 TC 대상).
- 비율 0~100만 검사 — 분류 누락(BMI=25) 감지 불가.

## 결과 및 산출물

- 본 Report 및 대화 Transcript (`Prompt/stage01-code-analysis.md`)
- **코드 변경 없음** (분석 단계만 수행)
- 실행 검증: 프로젝트 루트에서 `python src\main\python\shealth_bmi.py` → 6개 나이대 비율 출력 정상

### 리팩토링 우선순위 (2단계 이후 참고)

1. BMI 경계 `>= 25` 및 빈 행 `continue` 수정 (동작 버그)  
2. 데이터 경로(`pathlib` / 루트 기준) 정리  
3. `calculate_bmi` 분해 — 로드 / 보정 / BMI / 통계  
4. 매직 넘버·나이대 구간 상수화  
5. 레코드 구조 도입 및 중복 루프 제거  

## 이슈 및 해결

| 이슈 | 해결 |
|------|------|
| README 실행 경로와 `shealth.dat` 위치 불일치 | 루트에서 실행해 동작 확인; 2단계에서 경로 처리 개선 예정 |
| 스펙 vs 구현 (BMI=25) | 코드 정적 분석으로 불일치 식별; 2~3단계에서 수정·TC로 고정 |

## 다음 단계

**Activities 2단계 — 1차 리팩토링**: 네이밍 개선, 하드코드·전역 상태 제거, 함수 추출, 반복/중복 제거. 위 우선순위 1~2는 가능하면 2단계 초반에 반영.
