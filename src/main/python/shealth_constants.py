"""BMI·나이대 관련 상수 (SRP: 설정 값만 담당)."""


class BmiCategory:
    UNDERWEIGHT = 100
    NORMALWEIGHT = 200
    OVERWEIGHT = 300
    OBESITY = 400


class AgeGroupConfig:
    START = 20
    STOP = 80
    STEP = 10


class BmiThresholds:
    UNDERWEIGHT_MAX = 18.5
    NORMAL_MAX = 23.0
    OVERWEIGHT_MAX = 25.0


MISSING_VALUE = 0.0
CENTIMETERS_PER_METER = 100.0

ALL_BMI_CATEGORIES = (
    BmiCategory.UNDERWEIGHT,
    BmiCategory.NORMALWEIGHT,
    BmiCategory.OVERWEIGHT,
    BmiCategory.OBESITY,
)
