import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evm.metrics import cpi, spi
from src.metrics_engine import calculate_pert, calculate_cocomo_I

OUTPUT_DIR = "metrics"


def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_pert():
    optimistic = 10
    likely = 15
    pessimistic = 20

    expected_duration = calculate_pert(optimistic, likely, pessimistic)

    with open(f"{OUTPUT_DIR}/pert.json", "w") as f:
        json.dump(
            {"expected_duration": expected_duration},
            f,
            indent=4
        )

    print("pert.json created")


def export_cocomo():
    size_kloc = 10

    result = calculate_cocomo_I(size_kloc)

    with open(f"{OUTPUT_DIR}/cocomo.json", "w") as f:
        json.dump(
            {"effort_estimation": result["effort"]},
            f,
            indent=4
        )

    print("cocomo.json created")


def export_evm():
    print("Running export_evm()")

    try:
        EV = 90
        AC = 100
        PV = 95

        cpi_value = cpi(EV, AC)
        spi_value = spi(EV, PV)

        with open(f"{OUTPUT_DIR}/evm.json", "w") as f:
            json.dump(
                {"cpi": cpi_value, "spi": spi_value},
                f,
                indent=4
            )

        print("evm.json created")

    except Exception as e:
        print("export_evm failed:", e)


def export_all_metrics():
    ensure_dir()
    export_pert()
    export_cocomo()
    export_evm()


if __name__ == "__main__":
    export_all_metrics()
    print("All metrics export completed")
