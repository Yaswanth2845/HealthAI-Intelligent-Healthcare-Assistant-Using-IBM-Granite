import streamlit as st
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
import plotly.express as px

# --- IBM Watson Assistant Setup ---
API_KEY = st.secrets["IBM_API_KEY"]
ASSISTANT_ID = st.secrets["IBM_ASSISTANT_ID"]
URL = st.secrets["IBM_URL"]

authenticator = IAMAuthenticator(API_KEY)
assistant = AssistantV2(version='2023-08-01', authenticator=authenticator)
assistant.set_service_url(URL)

# --- Streamlit UI ---
st.set_page_config(page_title="HealthAI", page_icon="🩺")
st.title("🩺 HealthAI – Your Intelligent Healthcare Assistant")

option = st.sidebar.radio("Select a module", [
    "Patient Chat", "Disease Prediction", "Treatment Plan", "Health Analytics"
])

# --- 1. Patient Chat ---
if option == "Patient Chat":
    st.header("💬 Ask a Medical Question")
    question = st.text_input("Type your health-related question")
    if st.button("Ask AI"):
        response = assistant.message_stateless(
            assistant_id=ASSISTANT_ID,
            input={"message_type": "text", "text": question}
        ).get_result()
        answer = response["output"]["generic"][0]["text"]
        st.success(answer)

# --- 2. Disease Prediction ---
elif option == "Disease Prediction":
    st.header("🧪 Predict Disease from Symptoms")
    symptoms = st.text_area("Enter your symptoms (e.g., headache, fatigue, fever)")
    if st.button("Predict"):
        response = assistant.message_stateless(
            assistant_id=ASSISTANT_ID,
            input={"message_type": "text", "text": f"Symptoms: {symptoms}"}
        ).get_result()
        prediction = response["output"]["generic"][0]["text"]
        st.info(prediction)

# --- 3. Treatment Plan ---
elif option == "Treatment Plan":
    st.header("💊 Get Personalized Treatment Plan")
    condition = st.text_input("Enter diagnosed condition (e.g., Diabetes)")
    age = st.number_input("Enter your age", min_value=0, max_value=120, value=30)
    if st.button("Generate Plan"):
        prompt = f"Provide a treatment plan for a {age}-year-old with {condition}"
        response = assistant.message_stateless(
            assistant_id=ASSISTANT_ID,
            input={"message_type": "text", "text": prompt}
        ).get_result()
        plan = response["output"]["generic"][0]["text"]
        st.success(plan)

# --- 4. Health Analytics ---
elif option == "Health Analytics":
    st.header("📊 Health Data Dashboard")
    st.write("Upload a CSV file with columns: `date`, `heart_rate`, `blood_pressure`")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        df = pd.read_csv(file, parse_dates=["date"])
        st.write("Health Data:", df)

        fig = px.line(df, x="date", y=["heart_rate", "blood_pressure"],
                      title="Health Metrics Over Time", markers=True)
        st.plotly_chart(fig)

        tail = df.tail(5).to_dict(orient="records")
        insight_prompt = f"Analyze this recent health data: {tail}"
        response = assistant.message_stateless(
            assistant_id=ASSISTANT_ID,
            input={"message_type": "text", "text": insight_prompt}
        ).get_result()
        analysis = response["output"]["generic"][0]["text"]
        st.warning("AI Insight: " + analysis)
