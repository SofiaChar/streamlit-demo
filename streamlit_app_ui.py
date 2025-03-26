# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import os

VALOHAI_API_URL = "https://app.valohai.com/api/v0"
PROJECT_OWNER = "your-org"
PROJECT_NAME = "your-project"
STEP_NAME = "inference"
TOKEN = os.environ.get("VALOHAI_TOKEN")

headers = {"Authorization": f"Token {TOKEN}"}


def get_executions():
    url = f"{VALOHAI_API_URL}/projects/{PROJECT_OWNER}/{PROJECT_NAME}/executions/"
    resp = requests.get(url, headers=headers)
    return resp.json()["results"]


def launch_execution(file_url, params):
    url = f"{VALOHAI_API_URL}/projects/{PROJECT_OWNER}/{PROJECT_NAME}/executions/"
    payload = {
        "step": STEP_NAME,
        "commit": "main",
        "inputs": {"input": file_url},
        "parameters": params
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()


st.title("🧪 Valohai + Streamlit Inference UI")

# Inference Form
with st.form("run_job"):
    st.subheader("🚀 Run Inference Job")
    file_url = st.text_input("Input file URL")
    param_x = st.text_input("Parameter: x", "default_value")
    submitted = st.form_submit_button("Submit Job")

    if submitted:
        res = launch_execution(file_url, {"x": param_x})
        st.success(f"Execution triggered! ID: {res.get('id')}")

# Executions Table
st.subheader("📊 Executions")
executions = get_executions()
df = pd.DataFrame([
    {
        "Name": ex["name"],
        "Created": ex["created_at"],
        "Status": ex["status"],
        "x": ex["parameters"].get("x"),
        "Output": ex["outputs"][0]["url"] if ex["outputs"] else "N/A"
    }
    for ex in executions
])
st.dataframe(df)
