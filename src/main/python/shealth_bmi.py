from health_data_loader import resolve_data_path
from shealth import SHealth
from shealth_constants import AgeGroupConfig, BmiCategory


def main() -> None:
    shealth = SHealth()
    data_path = resolve_data_path("shealth.dat")
    record_count = shealth.calculate_bmi(str(data_path))
    print(f"Loaded {record_count} records from {data_path}\n")

    print("=== Age group BMI distribution (%) ===")
    for age in range(
        AgeGroupConfig.START,
        AgeGroupConfig.STOP,
        AgeGroupConfig.STEP,
    ):
        distribution = shealth.get_age_group_bmi_distribution(age)
        print(
            f"{age}s - underweight = {distribution.get(BmiCategory.UNDERWEIGHT, 0):.6f}, "
            f"normal = {distribution.get(BmiCategory.NORMALWEIGHT, 0):.6f}, "
            f"overweight = {distribution.get(BmiCategory.OVERWEIGHT, 0):.6f}, "
            f"obesity = {distribution.get(BmiCategory.OBESITY, 0):.6f}"
        )

    print("\n=== Overall BMI category ratios (%) ===")
    overall = shealth.get_overall_bmi_ratios()
    for label, bmi_type in (
        ("underweight", BmiCategory.UNDERWEIGHT),
        ("normal", BmiCategory.NORMALWEIGHT),
        ("overweight", BmiCategory.OVERWEIGHT),
        ("obesity", BmiCategory.OBESITY),
    ):
        print(f"{label} = {overall.get(bmi_type, 0):.6f}")

    normal_ids = shealth.get_normal_weight_user_ids()
    preview = normal_ids[:10]
    suffix = "..." if len(normal_ids) > 10 else ""
    print(f"\n=== Normal-weight users ({len(normal_ids)} total) ===")
    print(f"IDs (first 10): {preview}{suffix}")


if __name__ == "__main__":
    main()
