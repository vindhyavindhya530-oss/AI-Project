import streamlit as st
from PIL import Image
import tempfile
import pandas as pd
import os

from ocr import extract_text
from extractor import (
    extract_merchant,
    extract_date,
    extract_amount,
    get_category,
)
from report import save_excel


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Receipt Digitiser",
    page_icon="🧾",
    layout="wide"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🧾 Smart Receipt Digitiser")

st.write(
    "AI-assisted receipt processing and reimbursement automation"
)

st.divider()


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "Upload Receipt Images",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ],
    accept_multiple_files=True,
    help="Upload one or multiple receipt images"
)


# --------------------------------------------------
# PROCESS RECEIPTS
# --------------------------------------------------

if uploaded_files:

    st.info(
        f"📁 {len(uploaded_files)} receipt(s) selected"
    )

    results = []
    failed_results = []

    # Create output folder
    os.makedirs(
        "output",
        exist_ok=True
    )

    # Clear old processing log
    log_path = "output/processing_log.txt"

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as log:

        log.write(
            "SMART RECEIPT DIGITISER - PROCESSING LOG\n"
        )

        log.write(
            "=" * 60 + "\n\n"
        )

    # --------------------------------------------------
    # PROCESS EACH RECEIPT
    # --------------------------------------------------

    for index, uploaded_file in enumerate(
        uploaded_files,
        start=1
    ):

        st.divider()

        st.subheader(
            f"🧾 Receipt {index}: {uploaded_file.name}"
        )

        # --------------------------------------------------
        # OPEN IMAGE
        # --------------------------------------------------

        try:

            image = Image.open(
                uploaded_file
            )

            st.image(
                image,
                caption=uploaded_file.name,
                width=400
            )

        except Exception as error:

            st.error(
                f"❌ Could not open {uploaded_file.name}"
            )

            continue


        # --------------------------------------------------
        # SAVE TEMPORARY IMAGE
        # --------------------------------------------------

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png"
            ) as temp:

                image.save(
                    temp.name,
                    format="PNG"
                )

                temp_path = temp.name


            # --------------------------------------------------
            # OCR
            # --------------------------------------------------

            with st.spinner(
                f"🔍 Reading {uploaded_file.name}..."
            ):

                text, confidence = extract_text(
                    temp_path
                )


            # Remove temporary file

            try:

                os.remove(
                    temp_path
                )

            except:

                pass


            # --------------------------------------------------
            # DATA EXTRACTION
            # --------------------------------------------------

            merchant = extract_merchant(
                text
            )

            date = extract_date(
                text
            )

            amount = extract_amount(
                text
            )

            category = get_category(
                text
            )


            # --------------------------------------------------
            # VALIDATION
            # --------------------------------------------------

            if confidence < 60:

                status = "Needs Manual Review"

            elif merchant in [
                None,
                "",
                "Unknown"
            ]:

                status = "Needs Manual Review"

            elif date is None:

                status = "Needs Manual Review"

            elif amount is None:

                status = "Needs Manual Review"

            elif amount > 10000:

                status = "Needs Manager Approval"

            else:

                status = "Approved"


            # --------------------------------------------------
            # DISPLAY RESULT
            # --------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Merchant:** {merchant}"
                )

                st.write(
                    f"**Date:** {date}"
                )

            with col2:

                if amount is not None:

                    st.write(
                        f"**Amount:** ₹{amount:,.2f}"
                    )

                else:

                    st.write(
                        "**Amount:** Not detected"
                    )

                st.write(
                    f"**Category:** {category}"
                )

                st.write(
                    f"**OCR Confidence:** "
                    f"{confidence:.2f}%"
                )


            # --------------------------------------------------
            # STATUS DISPLAY
            # --------------------------------------------------

            if status == "Approved":

                st.success(
                    "✅ Approved"
                )

            elif status == "Needs Manager Approval":

                st.warning(
                    "⚠️ Needs Manager Approval"
                )

            else:

                st.error(
                    "🔴 Needs Manual Review"
                )


            # --------------------------------------------------
            # STORE RESULT
            # --------------------------------------------------

            result = {

                "Receipt_File":
                    uploaded_file.name,

                "Merchant":
                    merchant,

                "Date":
                    date,

                "Amount":
                    amount,

                "Category":
                    category,

                "Status":
                    status,

                "OCR_Confidence":
                    round(
                        confidence,
                        2
                    )
            }

            results.append(
                result
            )


            # --------------------------------------------------
            # FAILED / MANUAL REVIEW
            # --------------------------------------------------

            if status == "Needs Manual Review":

                failed_results.append(
                    result
                )


            # --------------------------------------------------
            # PROCESSING LOG
            # --------------------------------------------------

            with open(
                log_path,
                "a",
                encoding="utf-8"
            ) as log:

                log.write(
                    f"Receipt : "
                    f"{uploaded_file.name}\n"
                )

                log.write(
                    f"Merchant : "
                    f"{merchant}\n"
                )

                log.write(
                    f"Date : "
                    f"{date}\n"
                )

                log.write(
                    f"Amount : "
                    f"{amount}\n"
                )

                log.write(
                    f"Category : "
                    f"{category}\n"
                )

                log.write(
                    f"OCR Confidence : "
                    f"{confidence:.2f}%\n"
                )

                log.write(
                    f"Status : "
                    f"{status}\n"
                )

                log.write(
                    "-" * 50 + "\n"
                )


            # --------------------------------------------------
            # OCR TEXT
            # --------------------------------------------------

            with st.expander(
                "📄 View OCR Extracted Text"
            ):

                st.text(
                    text if text
                    else "No text detected."
                )


        except Exception as error:

            st.error(
                f"❌ Error processing "
                f"{uploaded_file.name}: {error}"
            )

            if temp_path:

                try:

                    os.remove(
                        temp_path
                    )

                except:

                    pass


    # ==================================================
    # FINAL REPORT
    # ==================================================

    if results:

        st.divider()

        st.header(
            "📊 Processing Summary"
        )


        # --------------------------------------------------
        # DATAFRAME
        # --------------------------------------------------

        df = pd.DataFrame(
            results
        )

        failed_df = pd.DataFrame(
            failed_results,
            columns=df.columns
        )


        # --------------------------------------------------
        # SUMMARY NUMBERS
        # --------------------------------------------------

        total_receipts = len(
            df
        )

        approved_count = len(
            df[
                df["Status"] == "Approved"
            ]
        )

        manager_count = len(
            df[
                df["Status"]
                == "Needs Manager Approval"
            ]
        )

        manual_count = len(
            df[
                df["Status"]
                == "Needs Manual Review"
            ]
        )


        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Receipts",
                total_receipts
            )

        with col2:

            st.metric(
                "Approved",
                approved_count
            )

        with col3:

            st.metric(
                "Manager Approval",
                manager_count
            )

        with col4:

            st.metric(
                "Manual Review",
                manual_count
            )


        # --------------------------------------------------
        # SHOW TABLE
        # --------------------------------------------------

        st.subheader(
            "📋 Receipt Processing Results"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # --------------------------------------------------
        # SAVE EXCEL
        # --------------------------------------------------

        save_excel(
            df,
            failed_df
        )


        st.success(
            "✅ Excel reimbursement report generated!"
        )


        # --------------------------------------------------
        # DOWNLOAD EXCEL
        # --------------------------------------------------

        with open(
            "output/reimbursement_report.xlsx",
            "rb"
        ) as file:

            st.download_button(

                label="📥 Download Reimbursement Report",

                data=file,

                file_name=
                "reimbursement_report.xlsx",

                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )


        st.success(
            "✅ Processing log updated!"
        )