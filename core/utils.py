import os
import json
import csv
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import config


# date helpers
def get_target_date() -> date:
    """Retorna a data de hoje considerando o modo configurado (today ou specific)."""
    return date.today() if config.DATE_MODE == "today" else config.SPECIFIC_DATE


def format_date(dt: date, fmt: str = "%d/%m/%Y") -> str:
    """Formata a data para string."""
    return dt.strftime(fmt)


# file & directory helpers
def ensure_dir(path: str) -> None:
    """Cria diretório caso não exista."""
    os.makedirs(path, exist_ok=True)


def read_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Lê um arquivo JSON e retorna um dicionário."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON: {file_path}") from e


def write_json(file_path: str, data: Dict[str, Any]) -> None:
    """Grava um dicionário em um arquivo JSON."""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_csv(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """Lê um CSV e retorna lista de dicionários."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return None


def write_csv(file_path: str, rows: List[Dict[str, Any]]) -> None:
    """Grava uma lista de dicionários em CSV."""
    if not rows:
        return
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# generic helpers
def chunk_list(data: List[Any], size: int) -> List[List[Any]]:
    """Divide uma lista em pedaços menores."""
    return [data[i:i + size] for i in range(0, len(data), size)]


def safe_get(d: Dict[str, Any], key: str, default=None):
    """Tenta pegar o valor de um dicionário com chave opcional."""
    return d.get(key, default)


def timestamp() -> str:
    """Retorna timestamp formatado para logs."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
