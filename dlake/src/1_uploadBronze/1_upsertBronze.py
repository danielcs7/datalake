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
source_bucket = "landzone"  
dest_bucket = "datalake"    
base_prefix = "bronze"      

# Mapeamento de subpastas
sub_prefix_mapping = {
    "db1": "bronzedb1",
    "db2": "bronzedb2",
    "db3": "bronzedb3"
}

# Diretório temporário para processamento
temp_dir = "/tmp/minio_temp"
os.makedirs(temp_dir, exist_ok=True)

# Conexão com DuckDB
duckdb_conn = duckdb.connect(database=":memory:")  # Usando banco em memória para performance

def list_existing_files(minio_client, bucket_name, prefix):
    """ Lista os arquivos existentes no bucket de destino """
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return {obj.object_name for obj in objects}
    except S3Error as e:
        print(f"❌ Erro ao listar arquivos no bucket '{bucket_name}': {e}")
        return set()

def process_upsert(landzone_file, bronze_file):
    """ Realiza o upsert entre os dados do landzone e bronze usando DuckDB """
    print(f"🔄 Processando upsert para '{landzone_file}'...")

    # Carregar o novo arquivo da landzone
    df_new = duckdb.read_parquet(landzone_file)

    # Verificar se o arquivo já existe na camada bronze
    if os.path.exists(bronze_file):
        df_existing = duckdb.read_parquet(bronze_file)

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
    df_upserted.to_parquet(bronze_file)
    return bronze_file

def migrate_files(minio_client, source_bucket, dest_bucket, base_prefix):
    try:
        # Verifica se o bucket de destino existe
        if not minio_client.bucket_exists(dest_bucket):
            minio_client.make_bucket(dest_bucket)
            print(f"✅ Bucket '{dest_bucket}' criado com sucesso.")

        # Lista os arquivos existentes no bronze
        existing_files = list_existing_files(minio_client, dest_bucket, base_prefix)

        # Lista arquivos da camada landzone
        objects = minio_client.list_objects(source_bucket, recursive=True)
        arquivos = [obj.object_name for obj in objects if obj.object_name.endswith(".parquet")]

        if not arquivos:
            print(f"⚠️ Nenhum arquivo .parquet encontrado no bucket '{source_bucket}'")
            return

        print(f"📂 Arquivos encontrados no bucket '{source_bucket}': {arquivos}")

        for object_name in arquivos:
            local_file = os.path.join(temp_dir, os.path.basename(object_name))

            # Baixa o arquivo do bucket landzone
            minio_client.fget_object(source_bucket, object_name, local_file)
            print(f"⬇️ Arquivo '{object_name}' baixado do bucket '{source_bucket}'.")

            for key, sub_prefix in sub_prefix_mapping.items():
                if key in object_name.lower():
                    full_prefix = f"{base_prefix}/{sub_prefix}"
                    dest_object_name = f"{full_prefix}/{os.path.basename(object_name)}"

                    bronze_file = os.path.join(temp_dir, f"bronze_{os.path.basename(object_name)}")

                    # Fazer o upsert com DuckDB
                    process_upsert(local_file, bronze_file)

                    # Enviar para o MinIO (camada bronze)
                    minio_client.fput_object(dest_bucket, dest_object_name, bronze_file)
                    print(f"✅ '{object_name}' atualizado na camada bronze '{dest_object_name}'!")

    except S3Error as e:
        print(f"❌ Erro ao transferir arquivos: {e}")

# Executar migração com upsert via DuckDB
migrate_files(minio_client, source_bucket, dest_bucket, base_prefix)
