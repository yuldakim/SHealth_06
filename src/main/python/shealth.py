import csv


class SHealth:
    """S-Health BMI 계산 클래스"""

    UNDERWEIGHT = 100
    NORMALWEIGHT = 200
    OVERWEIGHT = 300
    OBESITY = 400

    AGE_GROUP_START = 20
    AGE_GROUP_STOP = 80
    AGE_GROUP_STEP = 10

    MISSING_WEIGHT = 0.0
    CENTIMETERS_PER_METER = 100.0

    UNDERWEIGHT_MAX_BMI = 18.5
    NORMAL_MAX_BMI = 23.0
    OVERWEIGHT_MAX_BMI = 25.0

    def __init__(self):
        self._reset_data()

    def _reset_data(self) -> None:
        self.count = 0
        self.ages = []
        self.heights = []
        self.weights = []
        self.bmis = []
        self._bmi_ratios = {}

    def calculate_bmi(self, filename: str) -> int:
        """파일에서 데이터를 읽어 BMI를 계산한다."""
        self._reset_data()

        if not self._load_records(filename):
            return 0

        self._replace_missing_weights()
        self._calculate_bmis()
        self._calculate_bmi_ratios()

        return self.count

    def get_bmi_ratio(self, age_class: int, bmi_type: int) -> float:
        """나이대와 BMI 유형에 따른 비율을 반환한다."""
        return self._bmi_ratios.get((age_class, bmi_type), 0.0)

    def _load_records(self, filename: str) -> bool:
        try:
            with open(filename, "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                next(reader)
                for row in reader:
                    if not row:
                        continue
                    self.ages.append(int(row[1]))
                    self.weights.append(float(row[2]))
                    self.heights.append(float(row[3]))
        except FileNotFoundError:
            print(f"Failed to open file: {filename}")
            return False

        self.count = len(self.ages)
        return True

    def _age_groups(self):
        return range(
            self.AGE_GROUP_START,
            self.AGE_GROUP_STOP,
            self.AGE_GROUP_STEP,
        )

    def _is_in_age_group(self, age: int, age_group: int) -> bool:
        return age_group <= age < age_group + self.AGE_GROUP_STEP

    def _replace_missing_weights(self) -> None:
        for age_group in self._age_groups():
            average_weight = self._average_weight_for_age_group(age_group)
            if average_weight == self.MISSING_WEIGHT:
                continue

            for index, age in enumerate(self.ages):
                if (
                    self._is_in_age_group(age, age_group)
                    and self.weights[index] == self.MISSING_WEIGHT
                ):
                    self.weights[index] = average_weight

    def _average_weight_for_age_group(self, age_group: int) -> float:
        known_weights = [
            weight
            for age, weight in zip(self.ages, self.weights)
            if self._is_in_age_group(age, age_group)
            and weight != self.MISSING_WEIGHT
        ]

        if not known_weights:
            return self.MISSING_WEIGHT

        return sum(known_weights) / len(known_weights)

    def _calculate_bmis(self) -> None:
        self.bmis = [
            self._calculate_bmi(weight, height)
            for weight, height in zip(self.weights, self.heights)
        ]

    def _calculate_bmi(self, weight: float, height: float) -> float:
        height_in_meters = height / self.CENTIMETERS_PER_METER
        return weight / (height_in_meters**2)

    def _calculate_bmi_ratios(self) -> None:
        for age_group in self._age_groups():
            category_counts = self._count_bmi_categories(age_group)
            total_count = sum(category_counts.values())
            if total_count == 0:
                continue

            for bmi_type, category_count in category_counts.items():
                self._bmi_ratios[(age_group, bmi_type)] = (
                    category_count * 100 / total_count
                )

    def _count_bmi_categories(self, age_group: int) -> dict:
        category_counts = {
            self.UNDERWEIGHT: 0,
            self.NORMALWEIGHT: 0,
            self.OVERWEIGHT: 0,
            self.OBESITY: 0,
        }

        for age, bmi in zip(self.ages, self.bmis):
            if self._is_in_age_group(age, age_group):
                category_counts[self._classify_bmi(bmi)] += 1

        return category_counts

    def _classify_bmi(self, bmi: float) -> int:
        if bmi <= self.UNDERWEIGHT_MAX_BMI:
            return self.UNDERWEIGHT
        if bmi < self.NORMAL_MAX_BMI:
            return self.NORMALWEIGHT
        if bmi < self.OVERWEIGHT_MAX_BMI:
            return self.OVERWEIGHT
        return self.OBESITY
