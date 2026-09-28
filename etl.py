import pandas as pd


def clean_data(records):

    df = pd.DataFrame(records)

    # ------------------------------------------
    # CONVERT AMOUNT
    # ------------------------------------------

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    # ------------------------------------------
    # CONVERT DATE
    # ------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["Date"] = df["Date"].dt.strftime(
        "%Y-%m-%d"
    )

    # ------------------------------------------
    # DUPLICATE DETECTION
    # ------------------------------------------

    df["Duplicate"] = df.duplicated(
        subset=[
            "Merchant",
            "Date",
            "Amount"
        ],
        keep=False
    )

    # ------------------------------------------
    # DUPLICATE STATUS
    # ------------------------------------------

    df.loc[
        df["Duplicate"] == True,
        "Status"
    ] = "Duplicate"

    return df