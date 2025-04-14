import streamlit as st
import requests
import pandas as pd
import os

VALOHAI_API_URL = "https://app.valohai.com/api/v0"
TOKEN = os.environ.get("VALOHAI_TOKEN")

if not TOKEN:
    st.error("❌ VALOHAI_TOKEN environment variable not set!")
    st.stop()

HEADERS = {"Authorization": f"Token {TOKEN}"}

st.title("📊 Valohai Pipeline Explorer")

project_id = st.text_input("🔧 Enter Project ID", value="", help="Find it in Valohai URL or API")

if project_id:
    pipeline_url = f"{VALOHAI_API_URL}/pipelines/?project={project_id}"
    response = requests.get(pipeline_url, headers=HEADERS)

    if response.status_code == 200:
        pipelines = response.json()["results"]

        if not pipelines:
            st.info("No pipelines found.")
        else:
            for pipeline in pipelines:
                pipeline_id = pipeline["id"]
                title = pipeline["title"]
                status = pipeline["status"]
                created = pipeline["ctime"]

                with st.expander(f"🔁 {title} — {status} — {created}"):
                    st.write(f"**Pipeline ID:** `{pipeline_id}`")
                    st.write(f"🔗 [Open in Valohai]({pipeline['urls']['display']})")

                    if st.button(f"🔍 View Details", key=pipeline_id):
                        detail_url = f"{VALOHAI_API_URL}/pipelines/{pipeline_id}/"
                        detail_response = requests.get(detail_url, headers=HEADERS)

                        if detail_response.status_code == 200:
                            pipeline_data = detail_response.json()
                            st.markdown(f"**Project:** `{pipeline_data['project']['name']}`")
                            st.markdown(f"**Pipeline Status:** `{pipeline_data['status']}`")

                            node_data = pipeline_data.get("nodes", [])
                            if not node_data:
                                st.warning("No nodes found in this pipeline.")
                            else:
                                rows = []
                                for node in node_data:
                                    exec = node.get("execution", {})
                                    metrics = exec.get("cumulative_metadata", {})

                                    st.markdown(f"### 🔹 Node: `{node['name']}`")
                                    st.write(f"**Step:** `{exec.get('step', '-')}`")
                                    st.write(f"**Status:** `{node['status']}`")
                                    st.write(f"**Duration:** `{round(exec.get('duration', 0), 2)} seconds`")
                                    if exec.get("urls", {}).get("display"):
                                        st.markdown(f"🔗 [View Execution in Valohai]({exec['urls']['display']})")

                                    if metrics:
                                        st.markdown("#### 📈 Metrics")
                                        for key, value in metrics.items():
                                            st.write(f"• `{key}`: {value}")
                                    else:
                                        st.info("No metrics available for this node.")

                                    st.divider()

                                df = pd.DataFrame(rows)
                                st.dataframe(df)
                        else:
                            st.error("Could not fetch pipeline details.")
    else:
        st.error(f"❌ Failed to fetch pipelines (HTTP {response.status_code})")
