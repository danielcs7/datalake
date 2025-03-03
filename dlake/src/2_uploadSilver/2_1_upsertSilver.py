import duckdb
import pandas as pd
from minio import Minio
import os

# Configuração do cliente MinIO
minio_client = Minio(
    #"127.0.0.1:9001",  # URL do MinIO
    "192.168.64.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Nomes dos buckets
datalake_bucket = "datalake"  # O bucket 'datalake' sem a barra
bronze_prefix = "bronze/"  # Prefixo para arquivos em 'bronze'
silver_prefix = "silver/"  # Prefixo para arquivos em 'silver'

# Função para baixar um arquivo do MinIO para o sistema local
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

# Função para listar arquivos em um bucket
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

# Configuração do DuckDB
def upsert_to_silver(file_path):
    # Conectando ao DuckDB em memória
    con = duckdb.connect()

    # Baixar arquivo bronze para o local temporário
    local_bronze_file = f"temp_bronze_{file_path.split('/')[-1]}"
    download_file(datalake_bucket, file_path, local_bronze_file)

    # Carregar o arquivo .parquet em um DataFrame
    df = pd.read_parquet(local_bronze_file)

    # Criar tabela temporária para armazenar os dados da "bronze"
    con.execute("CREATE TABLE IF NOT EXISTS bronze_table AS SELECT * FROM df")

    # Verificar se o arquivo da 'silver' existe localmente
    silver_file = file_path.replace("bronze", "silver")
    silver_local_path = f"temp_silver_{file_path.split('/')[-1]}"
    
    if os.path.exists(silver_local_path):
        try:
            # Se existir, carregar o arquivo da 'silver'
            silver_df = pd.read_parquet(silver_local_path)
            print(f"Arquivo '{silver_local_path}' carregado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar o arquivo 'silver': {e}")
            silver_df = df  # Se falhar, criar um DataFrame vazio para upsert
    else:
        print(f"O arquivo '{silver_local_path}' não existe, criando um novo.")
        silver_df = df  # Se não existir, criar o DataFrame da "bronze"

    # Verificar os registros existentes e atualizar conforme necessário
    silver_df = silver_df.set_index("id").combine_first(df.set_index("id")).reset_index()

    # Salvar o arquivo da 'silver' após upsert
    silver_df.to_parquet(silver_local_path)

    # Fazer o upload do arquivo atualizado para o MinIO
    upload_file(datalake_bucket, silver_file, silver_local_path)

    # Remover os arquivos temporários locais
    if os.path.exists(local_bronze_file):
        os.remove(local_bronze_file)
    if os.path.exists(silver_local_path):
        os.remove(silver_local_path)

# Verifica se o bucket 'datalake' existe ou cria ele
if not minio_client.bucket_exists(datalake_bucket):
    minio_client.make_bucket(datalake_bucket)
    print(f"Bucket '{datalake_bucket}' criado com sucesso.")

# Lista todos os arquivos na 'bronze'
bronze_files = list_files(datalake_bucket, bronze_prefix)

# Processa cada arquivo na 'bronze'
for file_path in bronze_files:
    # Verifica se o arquivo segue o padrão esperado (ex: tipo_dbX.parquet)
    if "_db" in file_path and file_path.endswith(".parquet"):
        upsert_to_silver(file_path)
