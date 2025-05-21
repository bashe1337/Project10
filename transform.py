import pandas as pd
import json
import sympy as sp
from typing import Tuple, List, Dict, Union
from pathlib import Path

def transform_coordinates(
    input_data: Union[str, pd.DataFrame],
    source_system: str,
    target_system: str,
    params_path: Union[str, Path]
) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict]]:
    """
    Преобразует координаты из одной системы в другую с использованием преобразования Гельмерта.

    Аргументы:
        input_data: DataFrame или путь к CSV-файлу с координатами (Name, X, Y, Z).
        source_system: Начальная система координат (например, "ГСК-2011").
        target_system: Конечная система координат (например, "WGS-84").
        params_path: Путь к JSON-файлу с параметрами перехода.

    Возвращает:
        tuple: (DataFrame с преобразованными координатами, исходные данные, шаги вычислений для первой точки).
    """
    if isinstance(input_data, pd.DataFrame):
        data = input_data
    else:
        data = pd.read_excel(input_data)

    with open(params_path, 'r', encoding='utf-8') as f:
        parameters = json.load(f)

    if source_system == "ГСК-2011":
        direct_transform = True
        if target_system not in parameters:
            raise ValueError(f"Целевая система {target_system} не найдена в параметрах.")
        params = parameters[target_system]
    elif target_system == "ГСК-2011":
        direct_transform = False
        if source_system not in parameters:
            raise ValueError(f"Начальная система {source_system} не найдена в параметрах.")
        params = parameters[source_system]
    else:
        raise ValueError("Обе системы должны включать ГСК-2011 (либо как начальную, либо как конечную).")

    delta_x, delta_y, delta_z = params['dX'], params['dY'], params['dZ']
    wx, wy, wz, m = params['wx'], params['wy'], params['wz'], params['m']

    X, Y, Z = sp.symbols('X Y Z')
    coords = sp.Matrix([X, Y, Z])

    if direct_transform:
        scale = 1 + m
        rotation = sp.Matrix([
            [1, wz, -wy],
            [-wz, 1, wx],
            [wy, -wx, 1]
        ])
        translation = sp.Matrix([delta_x, delta_y, delta_z])
        transformed = scale * (rotation * coords) + translation
    else:
        scale = 1 - m
        rotation = sp.Matrix([
            [1, -wz, wy],
            [wz, 1, -wx],
            [-wy, wx, 1]
        ])
        translation = sp.Matrix([delta_x, delta_y, delta_z])
        transformed = scale * (rotation * (coords - translation))

    X_new_expr, Y_new_expr, Z_new_expr = transformed[0], transformed[1], transformed[2]

    transformed_coords = []
    computation_steps = []

    for idx, row in data.iterrows():
        x_val, y_val, z_val = row['X'], row['Y'], row['Z']
        name = row['Name']
        subs_dict = {X: x_val, Y: y_val, Z: z_val}

        x_new = float(X_new_expr.subs(subs_dict))
        y_new = float(Y_new_expr.subs(subs_dict))
        z_new = float(Z_new_expr.subs(subs_dict))

        transformed_coords.append([name, x_new, y_new, z_new])

        if idx == 0:
            steps = {
                "name": name,
                "source_system": source_system,
                "target_system": target_system,
                "initial_coords": f"X={x_val:.3f}, Y={y_val:.3f}, Z={z_val:.3f}",
                "params": f"ΔX={delta_x:.3f}, ΔY={delta_y:.3f}, ΔZ={delta_z:.3f}, ωx={wx:.6f}, ωy={wy:.6f}, ωz={wz:.6f}, m={m:.6f}",
                "general_formula": (
                    f"X' = {X_new_expr}\n"
                    f"Y' = {Y_new_expr}\n"
                    f"Z' = {Z_new_expr}"
                ),
                "substituted_coords": (
                    f"X' = {X_new_expr.subs(subs_dict):.3f}\n"
                    f"Y' = {Y_new_expr.subs(subs_dict):.3f}\n"
                    f"Z' = {Z_new_expr.subs(subs_dict):.3f}"
                ),
                "final_coords": f"X'={x_new:.3f}, Y'={y_new:.3f}, Z'={z_new:.3f}"
            }
            computation_steps.append(steps)

    result_df = pd.DataFrame(transformed_coords, columns=['Name', 'X_new', 'Y_new', 'Z_new'])
    return result_df, data, computation_steps
