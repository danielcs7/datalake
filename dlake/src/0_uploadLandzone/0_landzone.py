import os
import duckdb
import pandas as pd
from datetime import datetime
from minio import Minio
from minio.error import S3Error
from io import BytesIO

# Configurações do MinIO
minio_client = Minio(
    "127.0.0.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "landzone"

duckdb_files = [
    "/Volumes/MACBACKUP/workspaceDlake/dlake/db1.duckdb",
    "/Volumes/MACBACKUP/workspaceDlake/dlake/db2.duckdb",
    "/Volumes/MACBACKUP/workspaceDlake/dlake/db3.duckdb"
]

tables = ["fornecedores", "vendedores", "vendas", "produtos"]

def read_duckdb_table(db_file, table_name):
    """Lê os dados de uma tabela específica de um banco DuckDB."""
    conn = duckdb.connect(db_file)
    query = f"SELECT * FROM {table_name}"
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

def download_parquet_from_minio(parquet_filename):
    """Baixa o arquivo Parquet existente do MinIO se ele existir."""
    try:
        response = minio_client.get_object(bucket_name, f"landzone/{parquet_filename}")
        df_existing = pd.read_parquet(BytesIO(response.data))
        response.close()
        response.release_conn()
        return df_existing
    except S3Error:
        return pd.DataFrame()  # Retorna um DataFrame vazio se o arquivo não existir

def upsert_and_upload_parquet(df_new, table_name, db_name):
    """Faz upsert dos dados do DuckDB no Parquet do MinIO e envia o arquivo atualizado."""
    parquet_filename = f"{table_name}_{db_name}.parquet"
    df_existing = download_parquet_from_minio(parquet_filename)
    
    if not df_existing.empty:
        # Garante que a coluna 'id' existe em ambos os DataFrames
        if 'id' not in df_existing.columns or 'id' not in df_new.columns:
            print(f"Coluna 'id' não encontrada na tabela {table_name}. Pulando atualização.")
            return
        
        # Identifica registros novos e registros que precisam ser atualizados
        df_existing.set_index("id", inplace=True)
        df_new.set_index("id", inplace=True)
        
        # Atualiza registros existentes apenas se houver mudanças
        df_updated = df_existing.combine_first(df_new)
        df_updated = df_updated.loc[df_new.index]
        
        # Identifica registros que precisam ser inseridos
        df_inserts = df_new.loc[~df_new.index.isin(df_existing.index)]
        
        # Junta os registros atualizados e novos
        df_combined = pd.concat([df_existing, df_updated, df_inserts]).reset_index()
    else:
        df_combined = df_new.reset_index()
    
    # Adiciona a coluna dtcriação com a data e hora atual
    df_combined["dtcriação"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Adiciona a coluna de origem
    df_combined["origem"] = db_name
    
    temp_file = f"/tmp/{parquet_filename}"
    df_combined.to_parquet(temp_file, index=False)
    minio_client.fput_object(bucket_name, f"landzone/{parquet_filename}", temp_file)
    print(f"Arquivo {parquet_filename} atualizado e enviado para MinIO!")

# Processa cada banco DuckDB e tabela
for db_file in duckdb_files:
    db_name = os.path.basename(db_file).replace(".duckdb", "")
    for table in tables:
        df_new = read_duckdb_table(db_file, table)
        if not df_new.empty:
            upsert_and_upload_parquet(df_new, table, db_name)
        else:
            print(f"Nenhum dado encontrado na tabela {table} do banco {db_name}.")
