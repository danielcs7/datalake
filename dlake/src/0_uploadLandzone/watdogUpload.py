import os
import time
from minio import Minio
from minio.error import S3Error
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configurações do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Endereço do MinIO
    access_key="minioadmin",  # Chave de acesso
    secret_key="minioadmin",  # Chave secreta
    secure=False  # Usando HTTP, altere para True se usar HTTPS
)

# Nome do bucket
bucket_name = "landzone"

# Caminho da pasta a ser monitorada
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"

# Função para enviar arquivos para o MinIO
def upload_file_to_minio(file_path):
    try:
        if not minio_client.bucket_exists(bucket_name):
            print(f"Bucket {bucket_name} não encontrado!")
            return
        
        file_name = os.path.basename(file_path)
        object_name = f"landzone/{file_name}"
        
        print(f"Enviando {file_path} para {object_name}...")
        minio_client.fput_object(bucket_name, object_name, file_path)
        print(f"Arquivo {file_name} enviado com sucesso para {object_name}!")

    except S3Error as e:
        print(f"Erro ao acessar o MinIO: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Classe para monitorar a pasta
class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:  # Garante que não está pegando diretórios
            print(f"Novo arquivo detectado: {event.src_path}")
            upload_file_to_minio(event.src_path)

# Inicializa o monitoramento
event_handler = FileEventHandler()
observer = Observer()
observer.schedule(event_handler, path=source_dir, recursive=False)

try:
    print(f"Monitorando a pasta: {source_dir}")
    observer.start()
    while True:
        time.sleep(5)  # Mantém o script rodando
except KeyboardInterrupt:
    observer.stop()
    print("Monitoramento encerrado.")

observer.join()
