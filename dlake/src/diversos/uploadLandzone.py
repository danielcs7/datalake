import os
from minio import Minio
from minio.error import S3Error

# Função para enviar arquivos para o MinIO
def upload_files_to_minio(source_dir, bucket_name, minio_client):
    try:
        # Verificando se o bucket já existe (não criamos, apenas verificamos)
        if not minio_client.bucket_exists(bucket_name):
            print(f"Bucket {bucket_name} não encontrado!")
            return
        else:
            print(f"Bucket {bucket_name} já existe.")

        # Iterando sobre todos os arquivos na pasta source_dir
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Definindo o caminho dentro do bucket (sem prefixo extra)
                object_name = f"landzone/{file}"  # Apenas prefixo "landzone"
                print(f"Enviando {file_path} para {object_name}...")

                # Enviar o arquivo para o MinIO
                minio_client.fput_object(bucket_name, object_name, file_path)
                print(f"Arquivo {file} enviado com sucesso para {object_name}!")

    except S3Error as e:
        print(f"Erro ao acessar o MinIO: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Configurações do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Endereço do MinIO
    access_key="minioadmin",  # Chave de acesso
    secret_key="minioadmin",  # Chave secreta
    secure=False  # Usando HTTP, altere para True se usar HTTPS
)

# Caminho da pasta local contendo os arquivos
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"

# Nome do bucket onde os dados serão enviados
bucket_name = "landzone"  # O bucket já existe e os dados serão enviados para a camada landzone

# Chamando a função para enviar os arquivos
upload_files_to_minio(source_dir, bucket_name, minio_client)
