from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import tempfile
from core.converter import transform_coordinates

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transform")
async def transform(
    file: UploadFile = File(...),
    source_system: str = Form(...),
    target_system: str = Form(...)
):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        df = pd.read_excel(tmp_path)

        with open("core/parameters.json", encoding="utf-8") as f:
            params = json.load(f)

        result_df, original_df, steps = transform_coordinates(
            input_data=df,
            source_system=source_system,
            target_system=target_system,
            params_path="core/parameters.json"
        )

        markdown = f"## Преобразование координат из {source_system} в {target_system}\n\n"
        markdown += "**Исходные данные:**\n\n"
        markdown += original_df.to_markdown(index=False)
        markdown += "\n\n**Результаты:**\n\n"
        markdown += result_df.to_markdown(index=False)
        markdown += "\n\n**Подробности для первой точки:**\n\n"
        for step in steps:
            markdown += f"**{step['name']}**\n"
            markdown += f"- Исходные координаты: {step['initial_coords']}\n"
            markdown += f"- Параметры: {step['params']}\n"
            markdown += f"- Результат: {step['final_coords']}\n"
        return {"markdown": markdown}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
