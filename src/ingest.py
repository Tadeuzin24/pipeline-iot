import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "IOT-temp.csv"


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {CSV_PATH}")

    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "Defina a variável de ambiente DB_PASSWORD antes de executar."
        )

    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "iot_user"),
        password=password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME", "iot_data"),
    )

    print("Lendo o arquivo CSV...")
    df = pd.read_csv(CSV_PATH)

    # Ajusta os nomes das colunas para facilitar as consultas SQL.
    df = df.rename(
        columns={
            "room_id/id": "room_id",
            "out/in": "out_in",
        }
    )

    required = ["id", "room_id", "noted_date", "temp", "out_in"]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {missing}")

    total_original = len(df)

    # Interpreta as datas no formato dia-mês-ano.
    df["noted_date"] = pd.to_datetime(
        df["noted_date"],
        format="%d-%m-%Y %H:%M",
        errors="coerce",
    )
    df["temp"] = pd.to_numeric(df["temp"], errors="coerce")

    # Remove registros com campos essenciais inválidos.
    df = df.dropna(subset=required).copy()
    descartados = total_original - len(df)

    df["temp"] = df["temp"].astype("int64")
    df = df[required]

    print(f"Registros válidos: {len(df)}")
    print(f"Registros descartados: {descartados}")
    print("Conectando ao PostgreSQL...")

    engine = create_engine(url, pool_pre_ping=True)

    try:
        df.to_sql(
            "temperature_readings",
            engine,
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi",
        )

        with engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM temperature_readings")
            ).scalar_one()

        print("Importação concluída.")
        print(f"Registros no PostgreSQL: {count}")
        print("Tabela criada: temperature_readings")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
