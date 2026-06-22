import streamlit as st
import pandas as pd

st.set_page_config(page_title="Competitor Price Monitor Bot")

st.title("Competitor Price Monitor Bot")

st.write("Upload a product dataset as an Excel file.")

st.write("The bot will:")
st.write("• Read product information")
st.write("• Compare product price ranges with competitor price ranges")
st.write("• Detect overpriced products")
st.write("• Detect underpriced products")
st.write("• Identify competitively priced products")
st.write("• Generate a summary report for Business Manager")

uploaded_file = st.file_uploader(
    "Upload Product Dataset",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Dataset")
        st.dataframe(df)

        levels = {
            "Budget": 1,
            "Mid-Range": 2,
            "Premium": 3
        }

        def check_price(row):

            our_price = levels.get(
                str(row["price_range"]).strip(),
                0
            )

            competitor_price = levels.get(
                str(row["competitor_price_range"]).strip(),
                0
            )

            if our_price > competitor_price:
                return "Overpriced"

            elif our_price < competitor_price:
                return "Underpriced"

            else:
                return "Competitive Price"

        df["Status"] = df.apply(check_price, axis=1)

        st.subheader("Price Comparison Results")
        st.dataframe(df)

        overpriced = len(df[df["Status"] == "Overpriced"])
        underpriced = len(df[df["Status"] == "Underpriced"])
        competitive = len(df[df["Status"] == "Competitive Price"])

        st.subheader("Business Manager Report")

        st.write(f"Overpriced Products: {overpriced}")
        st.write(f"Underpriced Products: {underpriced}")
        st.write(f"Competitive Products: {competitive}")

        report = df.to_csv(index=False)

        st.download_button(
            label="Download Report",
            data=report,
            file_name="competitor_price_report.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")