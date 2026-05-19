from shealth import SHealth


def main():
    shealth = SHealth()
    shealth.calculate_bmi("shealth.dat")

    for age in range(
        shealth.AGE_GROUP_START,
        shealth.AGE_GROUP_STOP,
        shealth.AGE_GROUP_STEP,
    ):
        print(
            f"{age} - underweight = "
            f"{shealth.get_bmi_ratio(age, shealth.UNDERWEIGHT):.6f}, "
            f"normal = {shealth.get_bmi_ratio(age, shealth.NORMALWEIGHT):.6f}, "
            f"overweight = {shealth.get_bmi_ratio(age, shealth.OVERWEIGHT):.6f}, "
            f"obesity = {shealth.get_bmi_ratio(age, shealth.OBESITY):.6f}"
        )


if __name__ == "__main__":
    main()
