import os
import duckdb
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  
    access_key="minioadmin",  
    secret_key="minioadmin",  
    secure=False  
)

# Buckets e configurações
source_bucket = "datalake"  # Origem: bronze
dest_bucket = "datalake"    # Destino: silver
bronze_prefix = "bronze"    
silver_prefix = "silver"    

# Diretório temporário para processamento
temp_dir = "/tmp/minio_temp"
os.makedirs(temp_dir, exist_ok=True)

# Conexão com DuckDB
duckdb_conn = duckdb.connect(database=":memory:")  # Banco em memória para performance

def list_existing_files(minio_client, bucket_name, prefix):
    """ Lista os arquivos existentes na camada Silver """
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return {obj.object_name for obj in objects}
    except S3Error as e:
        print(f"❌ Erro ao listar arquivos no bucket '{bucket_name}': {e}")
        return set()

def process_upsert(bronze_file, silver_file):
    """ Realiza o upsert dos dados da Bronze para a Silver """
    print(f"🔄 Processando upsert para '{bronze_file}'...")

    # Carregar os dados da camada bronze
    df_new = duckdb.read_parquet(bronze_file)

    # Verificar se o arquivo já existe na camada silver
    if os.path.exists(silver_file):
        df_existing = duckdb.read_parquet(silver_file)

        # Fazendo um merge (upsert) baseado na chave primária (ajuste conforme necessário)
        df_upserted = duckdb.sql("""
            SELECT * FROM df_existing
            WHERE id NOT IN (SELECT id FROM df_new)  
            UNION ALL 
            SELECT * FROM df_new
        """).df()

        print(f"✅ Upsert concluído, registros novos/finalizados: {df_upserted.shape[0]}")
    else:
        df_upserted = df_new  # Se o arquivo não existe, apenas mantém os novos dados

    # Salvar o resultado atualizado
    df_upserted.to_parquet(silver_file)
    return silver_file

def migrate_files(minio_client, source_bucket, dest_bucket, bronze_prefix, silver_prefix):
    try:
        # Verifica se a camada silver já tem dados
        existing_files = list_existing_files(minio_client, dest_bucket, silver_prefix)

        # Lista arquivos da camada bronze
        objects = minio_client.list_objects(source_bucket, prefix=bronze_prefix, recursive=True)
        arquivos = [obj.object_name for obj in objects if obj.object_name.endswith(".parquet")]

        if not arquivos:
            print(f"⚠️ Nenhum arquivo .parquet encontrado no bucket '{source_bucket}/{bronze_prefix}'")
            return

        print(f"📂 Arquivos encontrados no bucket '{source_bucket}/{bronze_prefix}': {arquivos}")

        for object_name in arquivos:
            local_file = os.path.join(temp_dir, os.path.basename(object_name))

            # Baixa o arquivo do bucket Bronze
            minio_client.fget_object(source_bucket, object_name, local_file)
            print(f"⬇️ Arquivo '{object_name}' baixado do bucket Bronze.")

            # Ajusta o caminho para Silver
            silver_object_name = object_name.replace(bronze_prefix, silver_prefix, 1)
            silver_file = os.path.join(temp_dir, f"silver_{os.path.basename(object_name)}")

            # Fazer o upsert com DuckDB
            process_upsert(local_file, silver_file)

            # Enviar para o MinIO (camada Silver)
            minio_client.fput_object(dest_bucket, silver_object_name, silver_file)
            print(f"✅ '{object_name}' atualizado na camada Silver '{silver_object_name}'!")

    except S3Error as e:
        print(f"❌ Erro ao transferir arquivos: {e}")

# Executar migração com upsert via DuckDB (Bronze → Silver)
migrate_files(minio_client, source_bucket, dest_bucket, bronze_prefix, silver_prefix)
