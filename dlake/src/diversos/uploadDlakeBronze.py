import os
from minio import Minio
from minio.error import S3Error

# Configurações do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Endereço do servidor MinIO
    access_key="minioadmin",  # Usuário
    secret_key="minioadmin",  # Senha
    secure=False  # Se False, não usa SSL
)

# Função para enviar arquivos
def upload_files_to_minio(source_dir, bucket_name, prefix, minio_client):
    try:
        # Verifica se o bucket existe, caso contrário, cria
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' criado com sucesso.")

        # Enviar todos os arquivos .parquet para o MinIO no prefixo especificado
        for filename in os.listdir(source_dir):
            if filename.endswith(".parquet"):
                local_file = os.path.join(source_dir, filename)
                object_name = f"{prefix}/{filename}"  # Arquivo será enviado para o prefixo
                minio_client.fput_object(bucket_name, object_name, local_file)
                print(f"Arquivo '{filename}' enviado para '{bucket_name}/{object_name}'.")

    except S3Error as e:
        print(f"Erro ao enviar arquivo para o MinIO: {e}")

# Caminho dos arquivos .parquet e o bucket de destino
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"  # Caminho dos arquivos
bucket_name = "datalake"  # Nome do bucket no MinIO
prefixes = ["bronzedb1", "bronzedb2", "bronzedb3"]  # Prefixos dentro do bucket

# Enviar os arquivos para o bucket 'datalake' nas camadas
for prefix in prefixes:
    upload_files_to_minio(source_dir, bucket_name, prefix, minio_client)
