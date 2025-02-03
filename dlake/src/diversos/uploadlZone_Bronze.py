from minio import Minio
from minio.error import S3Error
from minio.api import CopySource

# Função para mover arquivos da landzone para o datalake com base no nome
def move_files_from_landzone_to_datalake(minio_client, landzone_bucket, datalake_bucket):
    try:
        # Listar todos os objetos (arquivos) no bucket landzone
        objects = minio_client.list_objects(landzone_bucket, recursive=True)
        found_files = False  # Flag para verificar se encontramos arquivos para mover
        
        for obj in objects:
            file_name = obj.object_name
            print(f"Verificando arquivo: {file_name}")
            
            # Verifica se o arquivo está na pasta landzone
            if "landzone" in file_name.lower():
                found_files = True

                # Determina para qual pasta do datalake o arquivo deve ser enviado
                if "db1" in file_name.lower():
                    destination_path = f"bronzedb1/{file_name.split('/')[-1]}"
                elif "db2" in file_name.lower():
                    destination_path = f"bronzedb2/{file_name.split('/')[-1]}"
                elif "db3" in file_name.lower():
                    destination_path = f"bronzedb3/{file_name.split('/')[-1]}"
                else:
                    print(f"Arquivo {file_name} não corresponde ao padrão esperado (db1, db2, db3).")
                    continue  # Pular arquivos que não correspondem ao padrão
                
                # Criar o objeto CopySource para a cópia
                copy_source = CopySource(landzone_bucket, file_name)
                
                # Copiar o arquivo para o novo destino
                print(f"Enviando arquivo para {destination_path}...")
                minio_client.copy_object(datalake_bucket, destination_path, copy_source)
                print(f"Arquivo {file_name} enviado com sucesso para {destination_path}.")

        if not found_files:
            print("Nenhum arquivo correspondente encontrado para mover.")
    
    except S3Error as e:
        print(f"Erro ao mover arquivos: {e}")

# Conectar ao MinIO
minio_client = Minio(
    "127.0.0.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Caminho para os buckets
landzone_bucket = "landzone"
datalake_bucket = "datalake"

# Chamar a função para mover os arquivos
move_files_from_landzone_to_datalake(minio_client, landzone_bucket, datalake_bucket)
