import os
import json
import subprocess
from pathlib import Path

KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

print("Username:", KAGGLE_USERNAME)

# create kaggle auth file
kaggle_dir = Path.home() / ".kaggle"
kaggle_dir.mkdir(exist_ok=True)

with open(kaggle_dir / "kaggle.json", "w") as f:
    json.dump({
        "username": KAGGLE_USERNAME,
        "key": KAGGLE_KEY
    }, f)

os.chmod(kaggle_dir / "kaggle.json", 0o600)

print("Kaggle auth file created")

# check kaggle CLI
print("\nRunning kaggle version")
subprocess.run(["kaggle", "--version"], check=True)

print("\nListing kernels")
subprocess.run(["kaggle", "kernels", "list", "-m"], check=True)

print("\nSUCCESS: Kaggle API working")
