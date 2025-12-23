import sys
import os
import json

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

METRICS_DIR = "metrics"
OUTPUT_FILE = "docs/metrics/dashboard_report.html"

def load_json(filename):
    path = os.path.join(METRICS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing metric file: {path}")
    with open(path) as f:
        return json.load(f)

def generate_dashboard():
    pert = load_json("pert.json")
    cocomo = load_json("cocomo.json")
    evm = load_json("evm.json")

    # CLI OUTPUT (Acceptance Criteria ✔)
    print("\n=== Combined Metrics Summary ===")
    print("CPI:", evm["cpi"])
    print("SPI:", evm["spi"])
    print("Expected Duration:", pert["expected_duration"])
    print("Effort Estimation:", cocomo["effort_estimation"])
    print("================================\n")

    html = f"""
    <html>
    <head>
        <title>Combined Metrics Dashboard</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 50%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Project Metrics Dashboard</h1>

        <h2>EVM Metrics</h2>
        <table>
            <tr><th>CPI</th><th>SPI</th></tr>
            <tr><td>{evm['cpi']}</td><td>{evm['spi']}</td></tr>
        </table>

        <h2>PERT</h2>
        <p>Expected Duration: <b>{pert['expected_duration']}</b></p>

        <h2>COCOMO</h2>
        <p>Effort Estimation: <b>{cocomo['effort_estimation']}</b></p>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print(f"✔ Dashboard generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dashboard()
