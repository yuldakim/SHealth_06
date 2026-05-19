"""나이대 평균으로 결측 체중·키 보정."""

from shealth_constants import MISSING_VALUE, AgeGroupConfig


class AgeGroupImputer:
    """동일 나이대 평균으로 0(누락) 값을 대체한다."""

    def __init__(
        self,
        age_start: int = AgeGroupConfig.START,
        age_stop: int = AgeGroupConfig.STOP,
        age_step: int = AgeGroupConfig.STEP,
        missing_value: float = MISSING_VALUE,
    ) -> None:
        self._age_start = age_start
        self._age_stop = age_stop
        self._age_step = age_step
        self._missing_value = missing_value

    def impute_weights(self, ages: list[int], weights: list[float]) -> None:
        self._impute(ages, weights)

    def impute_heights(self, ages: list[int], heights: list[float]) -> None:
        self._impute(ages, heights)

    def _impute(self, ages: list[int], values: list[float]) -> None:
        for age_group in self._age_groups():
            average = self._average_for_age_group(ages, values, age_group)
            if average == self._missing_value:
                continue

            for index, age in enumerate(ages):
                if (
                    self._is_in_age_group(age, age_group)
                    and values[index] == self._missing_value
                ):
                    values[index] = average

    def _age_groups(self):
        return range(self._age_start, self._age_stop, self._age_step)

    def _is_in_age_group(self, age: int, age_group: int) -> bool:
        return age_group <= age < age_group + self._age_step

    def _average_for_age_group(
        self,
        ages: list[int],
        values: list[float],
        age_group: int,
    ) -> float:
        known = [
            value
            for age, value in zip(ages, values)
            if self._is_in_age_group(age, age_group)
            and value != self._missing_value
        ]

        if not known:
            return self._missing_value

        return sum(known) / len(known)
