import os
import duckdb
import pandas as pd
import logging
from datetime import datetime
from minio import Minio
from minio.error import S3Error

# Configurações do MinIO
minio_client = Minio(
    "192.168.64.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Configurações do logging
LOG_FILE = "execution_log.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
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
    logging.info(f"Leitura da tabela {table_name} do banco {db_file} concluída com sucesso.")
    conn.close()
    return df

def download_csv_from_minio(csv_filename):
    """Baixa o arquivo CSV existente do MinIO se ele existir."""
    try:
        response = minio_client.get_object(bucket_name, f"landzone/{csv_filename}")
        df_existing = pd.read_csv(response, sep='|')
        response.close()
        response.release_conn()
        logging.info(f"Download do arquivo {csv_filename} do MinIO concluído.")
        return df_existing
    except S3Error:
        return pd.DataFrame()  # Retorna um DataFrame vazio se o arquivo não existir

def upsert_and_upload_csv(df_new, table_name, db_name):
    """Faz upsert dos dados do DuckDB no CSV do MinIO e envia o arquivo atualizado."""
    csv_filename = f"{table_name}_{db_name}.csv"
    df_existing = download_csv_from_minio(csv_filename)
    
    if not df_existing.empty:
        # Garante que a coluna 'id' existe em ambos os DataFrames
        if 'id' not in df_existing.columns or 'id' not in df_new.columns:
            print(f"Coluna 'id' não encontrada na tabela {table_name}. Pulando atualização.")
            logging.warning(f"Coluna 'id' não encontrada na tabela {table_name}. Pulando atualização.")
            return
        
        # Atualiza registros existentes e adiciona novos
        df_existing.set_index("id", inplace=True)
        df_new.set_index("id", inplace=True)
        
        df_updated = df_existing.combine_first(df_new)
        df_updated = df_updated.loc[df_new.index]
        df_inserts = df_new.loc[~df_new.index.isin(df_existing.index)]
        df_combined = pd.concat([df_existing, df_updated, df_inserts]).reset_index()
    else:
        df_combined = df_new.reset_index()
    
    # Adiciona a coluna dtcriação com a data e hora atual
    df_combined["dtcriação"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_combined["origem"] = db_name
    
    temp_file = f"/tmp/{csv_filename}"
    df_combined.to_csv(temp_file, sep='|', index=False)
    minio_client.fput_object(bucket_name, f"landzone/{csv_filename}", temp_file)
    logging.info(f"Arquivo {csv_filename} atualizado e enviado para MinIO.")
    print(f"Arquivo {csv_filename} atualizado e enviado para MinIO!")

# Processa cada banco DuckDB e tabela
for db_file in duckdb_files:
    db_name = os.path.basename(db_file).replace(".duckdb", "")
    for table in tables:
        df_new = read_duckdb_table(db_file, table)
        if not df_new.empty:
            print(f"TABLE : {table} BANCO {db_name}")
            upsert_and_upload_csv(df_new, table, db_name)
        else:
            print(f"Nenhum dado encontrado na tabela {table} do banco {db_name}.")
