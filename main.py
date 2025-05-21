from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
import shutil
from transform import transform_coordinates

app = FastAPI(title="Координатный преобразователь")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload", response_class=PlainTextResponse)
async def upload_file(
    file: UploadFile = File(...),
    source_system: str = Form(...),
    target_system: str = Form(...)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Поддерживаются только Excel-файлы (.xlsx)")

    temp_path = UPLOAD_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result_df, original_df, steps = transform_coordinates(
            input_data=temp_path,
            source_system=source_system,
            target_system=target_system,
            params_path="parameters.json"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")

    # Формируем markdown-результат
    markdown = [
        f"## Результаты преобразования из {source_system} в {target_system}",
        "\n### Исходные координаты:",
        original_df.to_markdown(index=False),
        "\n### Преобразованные координаты:",
        result_df.to_markdown(index=False),
        "\n### Шаги вычислений для первой точки:",
    ]

    for step in steps:
        markdown.append(f"#### Точка: {step['name']}")
        markdown.append(f"**Исходные координаты:** {step['initial_coords']}")
        markdown.append(f"**Параметры:** {step['params']}")
        markdown.append("**Формула преобразования:**\n```")
        markdown.append(step['general_formula'])
        markdown.append("```")
        markdown.append("**Подставленные значения:**\n```")
        markdown.append(step['substituted_coords'])
        markdown.append("```")
        markdown.append(f"**Итог:** {step['final_coords']}")

    return "\n\n".join(markdown)
