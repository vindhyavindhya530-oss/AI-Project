import pandas as pd
import os


def save_excel(df, failed_df):

    os.makedirs("output", exist_ok=True)

    file_path = "output/reimbursement_report.xlsx"

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        # Main reimbursement report
        df.to_excel(
            writer,
            sheet_name="Reimbursement Report",
            index=False
        )

        # Failed / manual review receipts
        failed_df.to_excel(
            writer,
            sheet_name="Manual Review",
            index=False
        )

    return file_path