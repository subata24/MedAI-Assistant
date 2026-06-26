import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

if api_key:
    genai.configure(api_key=api_key)


def safe_ai_call(prompt, model="gemini-3.1-flash-lite"):
    if not api_key:
        return (
            "AI service is not configured. "
            "Please set GOOGLE_API_KEY in your deployment secrets."
        )

    try:
        model_client = genai.GenerativeModel(model)

        response = model_client.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"AI ERROR: {str(e)}"
