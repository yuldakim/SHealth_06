from shealth import SHealth


def main():
    shealth = SHealth()
    record_count = shealth.calculate_bmi("shealth.dat")
    print(f"Loaded {record_count} records\n")

    print("=== Age group BMI distribution (%) ===")
    for age in range(
        shealth.AGE_GROUP_START,
        shealth.AGE_GROUP_STOP,
        shealth.AGE_GROUP_STEP,
    ):
        distribution = shealth.get_age_group_bmi_distribution(age)
        print(
            f"{age}s - underweight = {distribution.get(shealth.UNDERWEIGHT, 0):.6f}, "
            f"normal = {distribution.get(shealth.NORMALWEIGHT, 0):.6f}, "
            f"overweight = {distribution.get(shealth.OVERWEIGHT, 0):.6f}, "
            f"obesity = {distribution.get(shealth.OBESITY, 0):.6f}"
        )

    print("\n=== Overall BMI category ratios (%) ===")
    overall = shealth.get_overall_bmi_ratios()
    for label, bmi_type in (
        ("underweight", shealth.UNDERWEIGHT),
        ("normal", shealth.NORMALWEIGHT),
        ("overweight", shealth.OVERWEIGHT),
        ("obesity", shealth.OBESITY),
    ):
        print(f"{label} = {overall.get(bmi_type, 0):.6f}")

    normal_ids = shealth.get_normal_weight_user_ids()
    preview = normal_ids[:10]
    suffix = "..." if len(normal_ids) > 10 else ""
    print(f"\n=== Normal-weight users ({len(normal_ids)} total) ===")
    print(f"IDs (first 10): {preview}{suffix}")


if __name__ == "__main__":
    main()
