# SHealth BMI (Python)

# Overview
- 삼성 헬스에서는 수집된 데이터를 활용하여 사용자들의 나이대(ex. 20대, 30대, 40대 등)별 저체중/정상체중/과체중/비만의 통계를 계산하고자 합니다.
- 수집 중 누락된 체중값이 있으며 같은 나이대(ex. 20대, 30대, 40대 등)의 평균을 적용합니다. 체중 0이 누락된 경우 입니다.
- 수집 데이터는 ID, 나이, 몸무게(kg), 키(cm)이며, BMI는 체중(kg) / 키(m)제곱 으로 계산합니다.
- BMI 기준으로 18.5이하 저체중, 18.5초과 23미만 정상체중, 23이상 25미만 과체중, 25이상 비만으로 판단합니다.
![BMI](./bmi.png)
- 제공된 코드에는 다양한 코드 품질 문제가 있습니다. 


## data sample
- 입력 데이터 (shealth.dat)
```
id,age,weight,height
93705,66,79.5,158.3
93708,66,53.5,150.2
93709,75,88.8,151.1
... (이하 생략)
```
- 각 라인별 ID, 나이, 체중(kg), 키(cm) 순서 입니다.


## 실행 환경

### 요구사항
- Python 3.8 이상

### 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 필요한 패키지 설치 (테스트·커버리지)
pip install pytest pytest-cov
```

### 실행
프로젝트 **루트** 또는 `src/main/python` 어디서든 실행 가능합니다. `shealth.dat`는 루트에 두고, 로더가 `pathlib`로 루트·CWD를 순서대로 탐색합니다.

```bash
# 프로젝트 루트에서 (권장)
python src/main/python/shealth_bmi.py

# 또는 모듈 디렉터리에서
cd src/main/python
python shealth_bmi.py
```

### 테스트 실행
```bash
# 전체 테스트
python -m pytest src/test/python -v

# 커버리지 (pytest-cov 필요)
python -m pytest src/test/python --cov=src/main/python --cov-report=term-missing
```

### 가상환경 비활성화
```bash
deactivate
```


## 프로젝트 구조
```
shealth.dat                 - 입력 데이터 (프로젝트 루트)
src/
  main/python/
    shealth_constants.py    - BMI·나이대 상수
    health_record.py        - 단일 사용자 레코드
    health_data_loader.py   - CSV 로딩·경로 해석
    age_group_imputer.py    - 체중·키 결측(0) 나이대 평균 보정
    bmi_calculator.py       - BMI 계산·4분류
    bmi_analytics.py        - 연령대/전체 비율·정상 사용자
    shealth.py              - 파사드 (파이프라인 조율)
    shealth_bmi.py          - CLI 진입점
  test/python/
    conftest.py             - sys.path·fixtures
    test_bmi_calculator.py
    test_age_group_imputer.py
    test_health_data_loader.py
    test_shealth_bmi.py     - SHealth public API·통합 스모크
```


# 생성형AI를 활용한 Activities (6 시간)
1. [x] 문제 코드 분석 및 코드 스멜 찾기 (1시간)
- [x] 기본 코드구조, BMI 로직 이해 
- [x] 코드 스멜 찾기 
2. [x] 1차 리펙토링 (클린코드 관점, 아래 내용을 순차적으로 수행) (1시간) 
- [x] 네이밍 개선
- [x] 하드코드 및 전역변수 제거 
- [x] 함수 추출
- [x] 반복/중복 제거
3. [x] UnitTest 작성 (1시간)
- [x] BMI 계산 로직 TC
- [x] Age 평균치 보정 로직 TC
- [x] 정상/저체중/과체중/비만 분류 TC
- [x] 예외상황 TC
4. [x] 기능 개선 (2시간)
- [x] SRP에 따른 책임 분리등 리팩토링 
- [x] 특정 연령대의 BMI 분포 비율 계산 기능 추가
- [x] Height가 0인 경우에 대한 평균치 보정 로직 추가 
- [x] BMI 정상 범위 사용자 목록 조회 기능 추가
- [x] 전체 사용자 대비 각 BMI 범주 비율 계산 기능 추가
5. [x] 회고 및 발표 (1시간) 
- [x] 실습 목표와 달성도 
- [x] 코드 품질 Before & After
- [x] AI를 어떻게 활용했나? 도움이 된 순간과 한계는? 
- [x] TC를 추가보면서 개선에 미친 영향, TC 작성 팁
- [x] 클린코드와 리팩토링에서 느낀 장점과 어려운점
6. [x] 남은 단점 및 개선
- [ ] `shealth.dat` CWD·루트 경로 일치 (`pathlib` 등)
- [ ] 나이대 내 체중·키 전원 0 → BMI 0 나누기 가드·TC
- [ ] `shealth.py` 미사용 메서드·`AgeGroupImputer` private 우회 제거
- [ ] 파사드 private 래퍼·`BmiCategory` 이중 노출 정리
- [ ] `BmiCalculator` / `AgeGroupImputer` / `HealthDataLoader` 모듈 단위 테스트
- [ ] `SHealth` public API 위주 TC 보강
- [ ] `pytest-cov` 실행·README에 커버리지 명령 반영
- [ ] 비정상 CSV·결측 전원 0 등 극단·예외 TC
- [ ] `shealth.dat` 통합 스모크 TC
- [ ] README 프로젝트 구조·실행·pytest 안내를 현재 코드와 동기화

## Activities 단계 완료 시 (Report / Prompt / Git)

각 단계(1~6)를 마치면 Cursor에서 **`@activities-stage-delivery N단계 완료`** 로 에이전트를 호출한다.

- `Report/stage0N-*.md` — 단계 보고서 (파일명 앞에 단계 번호 포함)
- `Prompt/stage0N-*.md` — 대화 Export Transcript (Report와 **동일 파일명**, Markdown)
- README 체크박스 `[x]` 갱신 후 Git commit · push

자세한 사용법: [AGENTS.md](AGENTS.md)


# 주의 사항
- 코드 품질을 높이기 위해 Python의 표준 라이브러리를 필요한 경우 사용하셔도 됩니다.
