
import streamlit as st
import pandas as pd

st.title("Employee Data Analysis")

st.write("Upload a CSV file to analyse employee information.")

# Upload CSV file
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Display data
    st.subheader("1. Dataset Preview")
    st.dataframe(df)

    # Display number of rows and columns
    st.subheader("2. Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Rows", df.shape[0])

    with col2:
        st.metric("Total Columns", df.shape[1])

    # Missing values
    st.subheader("3. Missing Values")

    missing = df.isnull().sum()
    st.write(missing)

    # Statistical summary
    st.subheader("4. Statistical Summary")
    st.write(df.describe())

    # Department analysis
    if "Department" in df.columns:

        st.subheader("5. Department Analysis")

        st.write(df["Department"].value_counts())

    # Salary analysis
    if "Salary" in df.columns:

        st.subheader("6. Salary Analysis")

        st.metric(
            "Average Salary",
            f"{df['Salary'].mean():,.2f}"
        )

    st.success("Data analysis completed!")
