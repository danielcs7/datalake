import duckdb
import pandas as pd
from minio import Minio
import os

# Configuração do cliente MinIO
minio_client = Minio(
    "192.168.64.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Nomes dos buckets
datalake_bucket = "datalake"
bronze_prefix = "bronze/"
silver_prefix = "silver/"

# Função para baixar um arquivo do MinIO

def download_file(bucket_name, file_path, local_path):
    try:
        minio_client.fget_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{file_path}' baixado para '{local_path}'.")
    except Exception as e:
        print(f"Erro ao baixar o arquivo '{file_path}': {e}")

# Função para fazer upload de um arquivo para o MinIO
def upload_file(bucket_name, file_path, local_path):
    try:
        minio_client.fput_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{local_path}' enviado para '{bucket_name}/{file_path}'.")
    except Exception as e:
        print(f"Erro ao enviar o arquivo '{local_path}': {e}")

# Função para listar arquivos no MinIO
def list_files(bucket_name, prefix=""):
    if not minio_client.bucket_exists(bucket_name):
        print(f"Bucket '{bucket_name}' não existe.")
        return []
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except Exception as e:
        print(f"Erro ao listar arquivos no bucket '{bucket_name}': {e}")
        return []

def upsert_to_silver(file_path):
    con = duckdb.connect()
    local_bronze_file = f"temp_bronze_{file_path.split('/')[-1]}"
    download_file(datalake_bucket, file_path, local_bronze_file)
    
    # Ler CSV da bronze
    df = pd.read_csv(local_bronze_file, sep="|", dtype=str)
    print(f"Colunas do arquivo bronze: {df.columns.tolist()}")
    
    if "id" not in df.columns:
        print(f"Erro: A coluna 'id' não está presente no arquivo {file_path}")
        return

    # Criar tabela temporária
    con.execute("CREATE TABLE IF NOT EXISTS bronze_table AS SELECT * FROM df")
    
    silver_file = file_path.replace("bronze", "silver")
    silver_local_path = f"temp_silver_{file_path.split('/')[-1]}"
    
    if os.path.exists(silver_local_path):
        try:
            silver_df = pd.read_csv(silver_local_path, sep="|", dtype=str)
            print(f"Colunas do arquivo silver: {silver_df.columns.tolist()}")
        except Exception as e:
            print(f"Erro ao carregar o arquivo silver: {e}")
            silver_df = df
    else:
        print(f"O arquivo '{silver_local_path}' não existe, criando um novo.")
        silver_df = df

    if "id" not in silver_df.columns:
        print(f"Erro: A coluna 'id' não está presente no arquivo silver. Criando um novo a partir do bronze.")
        silver_df = df

    # Upsert
    silver_df = silver_df.set_index("id").combine_first(df.set_index("id")).reset_index()
    silver_df.to_csv(silver_local_path, sep="|", index=False)
    
    upload_file(datalake_bucket, silver_file, silver_local_path)
    os.remove(local_bronze_file)
    os.remove(silver_local_path)

# Criar bucket, se necessário
if not minio_client.bucket_exists(datalake_bucket):
    minio_client.make_bucket(datalake_bucket)
    print(f"Bucket '{datalake_bucket}' criado com sucesso.")

# Processar arquivos
bronze_files = list_files(datalake_bucket, bronze_prefix)
for file_path in bronze_files:
    if "_db" in file_path and file_path.endswith(".csv"):
        upsert_to_silver(file_path)
