from minio import Minio
from minio.error import S3Error
import pandas as pd
from io import BytesIO
import re

# Função para fazer upsert de arquivos da camada bronze para a camada silver
def upsert_bronze_to_silver(minio_client, datalake_bucket):
    try:
        # Listar todos os objetos no bucket datalake (camada bronze)
        objects = minio_client.list_objects(datalake_bucket, recursive=True)
        found_files = False  # Flag para verificar se encontramos arquivos para processar
        
        for obj in objects:
            file_name = obj.object_name
            print(f"Verificando arquivo: {file_name}")
            
            # Verifica se o arquivo está em uma das camadas bronze (bronzedb1, bronzedb2, bronzedb3)
            match = re.match(r"^(bronzedb[123])/(.*)", file_name)
            if match:
                found_files = True
                
                bronze_prefix = match.group(1)  # Exemplo: "bronzedb1"
                remaining_path = match.group(2)  # Exemplo: "fornecedores_DB1.parquet"

                # Criar o prefixo correto para a camada silver
                silver_prefix = bronze_prefix.replace("bronzedb", "silverdb")  # Exemplo: "silverdb1"
                silver_file_name = f"{silver_prefix}/{remaining_path}"  # Caminho correto na camada silver

                # Ler o arquivo da camada bronze
                response = minio_client.get_object(datalake_bucket, file_name)

                # Criar um buffer de BytesIO para armazenar os dados do arquivo
                parquet_buffer = BytesIO(response.read())

                # Ler o conteúdo Parquet para um DataFrame Pandas
                df = pd.read_parquet(parquet_buffer)

                # Aqui você pode processar ou transformar os dados, se necessário
                df_transformed = df  # Substitua com a transformação necessária

                # Verificar se o arquivo já existe na camada silver
                try:
                    minio_client.stat_object(datalake_bucket, silver_file_name)
                    print(f"Arquivo {silver_file_name} já existe, substituindo...")
                except S3Error:
                    print(f"Arquivo {silver_file_name} não encontrado, inserindo novo arquivo...")

                # Converter o DataFrame para parquet
                parquet_buffer = BytesIO()
                df_transformed.to_parquet(parquet_buffer)

                # Voltar o ponteiro do buffer para o início
                parquet_buffer.seek(0)

                # Enviar para a camada silver
                minio_client.put_object(datalake_bucket, silver_file_name, parquet_buffer, parquet_buffer.getbuffer().nbytes)
                print(f"Arquivo {silver_file_name} enviado com sucesso para a camada silver.")
        
        if not found_files:
            print("Nenhum arquivo correspondente encontrado para processar.")
    
    except S3Error as e:
        print(f"Erro ao fazer upsert: {e}")

# Conectar ao MinIO
minio_client = Minio(
    "127.0.0.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Caminho para o bucket datalake
datalake_bucket = "datalake"

# Chamar a função para fazer upsert dos arquivos da camada bronze para a camada silver
upsert_bronze_to_silver(minio_client, datalake_bucket)
