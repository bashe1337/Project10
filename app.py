import streamlit as st
import requests
import json

# Загрузим параметры координатных систем
with open("core/parameters.json", encoding="utf-8") as f:
    parameters = json.load(f)

coordinate_systems = list(parameters.keys())

st.title("Система преобразования координат")
st.markdown("Загрузите Excel-файл и выберите системы координат.")

uploaded_file = st.file_uploader("Выберите Excel-файл", type=["xlsx"])

source_system = st.selectbox("Начальная система координат", coordinate_systems)
target_system = st.selectbox("Целевая система координат", coordinate_systems)

if st.button("Преобразовать") and uploaded_file:
    with st.spinner("Обработка..."):
        try:
            response = requests.post(
                "https://project10-h0h1.onrender.com/transform",
                files={"file": uploaded_file.getvalue()},
                data={
                    "source_system": source_system,
                    "target_system": target_system
                }
            )
            if response.status_code == 200:
                result = response.json()
                st.markdown(result["markdown"])
                st.download_button("Скачать отчёт", result["markdown"], file_name="report.md")
            else:
                st.error(f"Ошибка: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Ошибка при подключении к серверу: {e}")
