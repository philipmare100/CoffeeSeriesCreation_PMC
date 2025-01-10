import streamlit as st
import pandas as pd
import sys
sys.path.append('/opt/anaconda3/envs/myenvtest/lib/python3.10/site-packages')
from coffee.client import JsonApiClient
from coffee.workflows import SeriesWorkflow


def process_csv(uploaded_file):
    """
    Step 1: Process the uploaded CSV file using the SeriesWorkflow for bulk_create_series.
    """
    try:
        with JsonApiClient() as client:
            series_workflow = SeriesWorkflow(client)
            # Save the uploaded file to a temporary location
            temp_file_path = "/tmp/uploaded_series.csv"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())

            # Use the workflow to process the CSV
            series_workflow.bulk_create_series(temp_file_path)
            st.success("Series created successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def trim_and_link_csv(uploaded_file):
    """
    Step 2: Trim the same CSV to keep only 'name' and 'process' columns,
    then use SeriesWorkflow to bulk_link_series_to_component.
    """
    try:
        # Load the uploaded CSV file
        df = pd.read_csv(uploaded_file)

        # Keep only the 'name' and 'process' columns
        if 'name' in df.columns and 'process' in df.columns:
            trimmed_df = df[['name', 'process']]
        else:
            st.error("The CSV must contain 'name' and 'process' columns.")
            return

        # Save the trimmed data to a temporary file
        trimmed_file_path = "/tmp/trimmed_series.csv"
        trimmed_df.to_csv(trimmed_file_path, index=False)

        # Preview the trimmed data
        st.write("Trimmed CSV Preview:")
        st.dataframe(trimmed_df)

        # Process the trimmed file using SeriesWorkflow's bulk_link_series_to_component
        with JsonApiClient() as client:
            series_workflow = SeriesWorkflow(client)
            series_workflow.bulk_link_series_to_component(trimmed_file_path)
            st.success("Series successfully linked to components!")
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Streamlit app layout
st.title("Series Workflow Tool")

# Step 1: Upload CSV and create series
st.header("Step 1: Create Series")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="step1")

if uploaded_file is not None:
    st.write("Uploaded file:", uploaded_file.name)
    if st.button("Process CSV for Series Creation", key="step1_btn"):
        process_csv(uploaded_file)

# Step 2: Trim the same file and link series to components
st.header("Step 2: Trim CSV and Link Series to Components")
if uploaded_file is not None:
    if st.button("Trim CSV and Link Series to Components", key="step2_btn"):
        trim_and_link_csv(uploaded_file)
