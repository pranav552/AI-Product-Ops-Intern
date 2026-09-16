import argparse
from pathlib import Path

import pandas as pd

from src.pipeline import run_app


RESULTS_DIR = Path("data/results")


def already_done(app_name: str) -> bool:
    file_path = RESULTS_DIR / (app_name.lower().replace(" ", "_") + ".json")
    return file_path.exists()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--app", action="append", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv("data/apps.csv")

    if args.app:
        df = df[df["app_name"].isin(args.app)]

    if args.limit:
        df = df.head(args.limit)

    completed, failed, skipped = [], [], []

    for _, row in df.iterrows():

        app_name = row["app_name"]
        website = row["website"]

        if not args.force and already_done(app_name):
            print(f"SKIP (checkpoint exists): {app_name}")
            skipped.append(app_name)
            continue

        try:
            result = run_app(app_name, website)
            if result is None:
                failed.append(app_name)
            else:
                completed.append(app_name)

        except Exception as e:
            print(f"\nUNCAUGHT ERROR on {app_name}: {e}")
            failed.append(app_name)
            continue

    print("\n" + "=" * 60)
    print(f"DONE. Completed: {len(completed)} | Skipped: {len(skipped)} | Failed: {len(failed)}")
    if failed:
        print("Failed apps:", failed)
    print("=" * 60)


if __name__ == "__main__":
    main()