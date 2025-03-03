from minio import Minio
from minio.error import S3Error
import os
import pandas as pd

# Configuração do cliente MinIO
minio_client = Minio(
    "192.168.64.1:9001",  # URL do MinIO
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Nomes dos buckets
landzone_bucket = "landzone"
bronze_bucket = "datalake"

# Função para baixar um arquivo do MinIO para o sistema local
def download_file(bucket_name, file_path, local_path):
    try:
        minio_client.fget_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{file_path}' baixado para '{local_path}'.")
    except S3Error as e:
        print(f"Erro ao baixar o arquivo '{file_path}': {e}")
        raise

# Função para fazer upload de um arquivo para o MinIO
def upload_file(bucket_name, file_path, local_path):
    try:
        minio_client.fput_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{local_path}' enviado para '{bucket_name}/{file_path}'.")
    except S3Error as e:
        print(f"Erro ao enviar o arquivo '{local_path}': {e}")
        raise

# Função para listar arquivos em um bucket
def list_files(bucket_name, prefix=""):
    if not minio_client.bucket_exists(bucket_name):
        print(f"Bucket '{bucket_name}' não existe.")
        return []
    
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        print(f"Erro ao listar arquivos no bucket '{bucket_name}': {e}")
        return []

# Verifica se o bucket 'datalake' existe ou cria ele
if not minio_client.bucket_exists(bronze_bucket):
    minio_client.make_bucket(bronze_bucket)
    print(f"Bucket '{bronze_bucket}' criado com sucesso.")

# Lista todos os arquivos na 'landzone'
landzone_files = list_files(landzone_bucket)

# Processa cada arquivo na 'landzone'
for file_path in landzone_files:
    file_name = file_path.split("/")[-1]

    # Verifica se o arquivo segue o padrão esperado (ex: tipo_dbX.csv)
    if "_db" in file_name and file_name.endswith(".csv"):
        file_type = file_name.split("_db")[0]
        db_number = file_name.split("_")[-1].split(".")[0]  # Ex: db1

        # Caminho no bucket 'bronze'
        destination_path = f"bronze/{db_number}/{file_name}"

        # Arquivo local temporário
        local_landzone_file = f"temp_landzone_{file_name}"
        local_bronze_file = f"temp_bronze_{file_name}"

        try:
            # Baixa o arquivo da 'landzone'
            download_file(landzone_bucket, file_path, local_landzone_file)

            # Lê o arquivo CSV e salva novamente com o separador '|'
            df = pd.read_csv(local_landzone_file, sep="|", dtype=str)  # Garante que lê corretamente
            df.to_csv(local_bronze_file, sep="|", index=False)

            # Faz upload do arquivo convertido para a 'bronze'
            upload_file(bronze_bucket, destination_path, local_bronze_file)

        finally:
            # Remove os arquivos temporários
            for temp_file in [local_landzone_file, local_bronze_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
