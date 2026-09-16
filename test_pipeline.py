import pandas as pd

from src.pipeline import run_app


def main():

    df = pd.read_csv(
        "data/apps.csv"
    )

    if df.empty:

        print(
            "No applications found."
        )

        return

    row = df.iloc[0]

    app_name = row["app_name"]
    website = row["website"]

    print(
        f"Processing: {app_name}"
    )

    print(
        f"Website: {website}"
    )

    result = run_app(
        app_name,
        website
    )

    if result is None:

        print(
            "\nPIPELINE FAILED"
        )

    else:

        print(
            "\nPIPELINE COMPLETED"
        )


if __name__ == "__main__":
    main()