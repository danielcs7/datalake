from minio import Minio
from minio.error import S3Error
import duckdb
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
landzone_bucket = "landzone"
bronze_bucket = "datalake"

# Função para baixar um arquivo do MinIO para o sistema local
def download_file(bucket_name, file_path, local_path):
    try:
        minio_client.fget_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{file_path}' baixado para '{local_path}'.")
    except S3Error as e:
        print(f"Erro ao baixar o arquivo '{file_path}': {e}")

# Função para fazer upload de um arquivo para o MinIO
def upload_file(bucket_name, file_path, local_path):
    try:
        minio_client.fput_object(bucket_name, file_path, local_path)
        print(f"Arquivo '{local_path}' enviado para '{bucket_name}/{file_path}'.")
    except S3Error as e:
        print(f"Erro ao enviar o arquivo '{local_path}': {e}")

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

# Função para realizar o upsert usando DuckDB
def upsert_parquet(landzone_file, bronze_file, output_file):
    conn = duckdb.connect()

    # Verifica se o arquivo bronze existe
    bronze_exists = os.path.exists(bronze_file)

    # Lê os arquivos Parquet
    landzone_df = conn.execute(f"SELECT * FROM read_parquet('{landzone_file}')").fetchdf()
    if bronze_exists:
        bronze_df = conn.execute(f"SELECT * FROM read_parquet('{bronze_file}')").fetchdf()
    else:
        bronze_df = None

    # Supondo que há uma coluna única para identificar registros (ex: id)
    primary_key = "id"  # Altere para a coluna correta

    if bronze_df is not None:
        upsert_query = f"""
        SELECT * FROM landzone_df
        UNION ALL
        SELECT * FROM bronze_df
        WHERE {primary_key} NOT IN (SELECT {primary_key} FROM landzone_df)
        """
        result_df = conn.execute(upsert_query).fetchdf()
    else:
        result_df = landzone_df  # Apenas insere os novos dados se não houver bronze

    # Salva o resultado em um novo arquivo Parquet
    result_df.to_parquet(output_file)
    print(f"Upsert concluído. Resultado salvo em '{output_file}'.")

    conn.close()

# Verifica se o bucket 'datalake' existe ou cria ele
if not minio_client.bucket_exists(bronze_bucket):
    minio_client.make_bucket(bronze_bucket)
    print(f"Bucket '{bronze_bucket}' criado com sucesso.")

# Lista todos os arquivos na 'landzone'
landzone_files = list_files(landzone_bucket)

# Processa cada arquivo na 'landzone'
for file_path in landzone_files:
    file_name = file_path.split("/")[-1]

    # Verifica se o arquivo segue o padrão esperado (ex: tipo_dbX.parquet)
    if "_db" in file_name and file_name.endswith(".parquet"):
        file_type = file_name.split("_db")[0]
        db_number = file_name.split("_")[-1].split(".")[0]  # Ex: db1

        # Caminho no bucket 'bronze' (correção aqui)
        destination_path = f"bronze/{db_number}/{file_name}"

        # Arquivos locais temporários
        local_landzone_file = f"temp_landzone_{file_name}"
        local_bronze_file = f"temp_bronze_{file_name}"
        local_output_file = f"temp_output_{file_name}"

        # Baixa o arquivo da 'landzone'
        download_file(landzone_bucket, file_path, local_landzone_file)

        # Verifica se o arquivo existe na 'bronze' antes de tentar baixá-lo
        try:
            minio_client.stat_object(bronze_bucket, destination_path)
            download_file(bronze_bucket, destination_path, local_bronze_file)
            bronze_exists = True
        except S3Error:
            print(f"Arquivo '{destination_path}' não encontrado na bronze. Será inserido diretamente.")
            bronze_exists = False

        # Realiza o upsert
        try:
            if bronze_exists:
                upsert_parquet(local_landzone_file, local_bronze_file, local_output_file)
                upload_file(bronze_bucket, destination_path, local_output_file)
            else:
                upload_file(bronze_bucket, destination_path, local_landzone_file)
        finally:
            # Remove arquivos temporários
            for temp_file in [local_landzone_file, local_bronze_file, local_output_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
