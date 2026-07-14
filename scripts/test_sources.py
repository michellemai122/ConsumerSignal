from pathlib import Path
import pandas as pd

# Build path relative to this script file
base_dir = Path(__file__).resolve().parent.parent
csv_path = base_dir / "data" / "startups.csv"

print("Looking for file at:", csv_path)

startups = pd.read_csv(csv_path)

print("Startups loaded:")
print(startups.head())

print("\nCategories:")
print(startups["category"].value_counts())