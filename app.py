import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Преобразование координат", layout="centered")
st.title("\U0001F4D1 Автоматизированная система преобразования координат")

API_URL = "https://project10-h0h1.onrender.com/transform"  

st.subheader("Загрузите Excel-файл с координатами")
uploaded_file = st.file_uploader("Выберите файл (.xlsx)", type=["xlsx"])

st.subheader("Выберите системы координат")
source_system = st.selectbox("Исходная система", ["ГСК-2011", "WGS-84"], index=0)
target_system = st.selectbox("Целевая система", ["WGS-84", "ГСК-2011"], index=1)

if st.button("Преобразовать"):
    if uploaded_file is None:
        st.error("Пожалуйста, загрузите файл.")
    elif source_system == target_system:
        st.warning("Исходная и целевая системы не должны совпадать.")
    else:
        with st.spinner("Отправка данных на сервер..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"source_system": source_system, "target_system": target_system}

            try:
                response = requests.post(API_URL, files=files, data=data)
                response.raise_for_status()
                markdown_text = response.text

                st.success("Преобразование завершено!")
                st.markdown(markdown_text)

                md_bytes = markdown_text.encode("utf-8")
                st.download_button(
                    label="Скачать отчёт в Markdown",
                    data=md_bytes,
                    file_name="report.md",
                    mime="text/markdown"
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при обращении к серверу: {e}")
