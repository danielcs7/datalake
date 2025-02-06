import os
import duckdb
import pandas as pd
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  
    access_key="minioadmin",  
    secret_key="minioadmin",  
    secure=False  
)

# Mapeamento de subpastas
sub_prefix_mapping = {
    "db1": "bronzedb1",
    "db2": "bronzedb2",
    "db3": "bronzedb3"
}
# Buckets e configurações
source_bucket = "landzone"  
dest_bucket = "datalake"    
base_prefix = "bronze"      

# Diretório temporário para processamento
temp_dir = "/tmp/minio_temp"
os.makedirs(temp_dir, exist_ok=True)

# Conexão com DuckDB
duckdb_conn = duckdb.connect(database=":memory:")  # Usando banco em memória para performance
def list_existing_files(minio_client, dest_bucket, base_prefix):
    """
    Lista os arquivos já existentes no bucket de destino para o prefixo fornecido.
    """
    try:
        # Lista todos os objetos no bucket de destino com o prefixo base
        objects = minio_client.list_objects(dest_bucket, prefix=base_prefix, recursive=True)
        existing_files = [obj.object_name for obj in objects]
        return existing_files
    except S3Error as e:
        print(f"❌ Erro ao listar arquivos existentes no bucket '{dest_bucket}': {e}")
        return []


def compare_and_upsert(landzone_file, bronze_file):
    """ Realiza o upsert garantindo que a estrutura e ordem dos dados sejam mantidas. """
    print(f"🔄 Processando upsert para '{landzone_file}'...")

    # Carregar os dados da landzone
    df_landzone = duckdb.read_parquet(landzone_file).df()

    # Salvar a ordem correta das colunas
    expected_columns = df_landzone.columns.tolist()

    # Se o arquivo bronze não existir, cria com a estrutura correta
    if not os.path.exists(bronze_file):
        print(f"📦 Criando bronze com a mesma estrutura da landzone.")
        df_landzone.to_parquet(bronze_file, index=False)
        return bronze_file

    # Carregar os dados da camada bronze
    df_bronze = duckdb.read_parquet(bronze_file).df()

    # **Forçar a mesma ordem de colunas**
    df_bronze = df_bronze.reindex(columns=expected_columns)

    # **Verificar diferenças entre landzone e bronze**
    df_diff = duckdb.sql("""
        SELECT * FROM df_landzone
        EXCEPT 
        SELECT * FROM df_bronze
    """).df()

    if df_diff.empty:
        print(f"✅ Nenhuma diferença encontrada. Nenhuma ação necessária.")
        return bronze_file

    print(f"⚠️ Diferenças encontradas! Inserindo ou atualizando dados.")

    # **Manter a ordem original da landzone**
    df_upserted = pd.concat([df_bronze, df_diff], ignore_index=True).drop_duplicates()
    df_upserted = df_upserted[expected_columns]  # 🔹 **Mantendo a ordem correta**

    # Salvar garantindo a ordem certa
    df_upserted.to_parquet(bronze_file, index=False)

    print(f"✅ Upsert concluído, {df_diff.shape[0]} linhas inseridas ou atualizadas.")
    print(f"📂 Ordem final das colunas no bronze: {df_upserted.columns.tolist()}")

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
                    compare_and_upsert(local_file, bronze_file)

                    # Enviar para o MinIO (camada bronze) na pasta correta
                    minio_client.fput_object(dest_bucket, dest_object_name, bronze_file)
                    print(f"✅ '{object_name}' atualizado na camada bronze '{dest_object_name}'!")

    except S3Error as e:
        print(f"❌ Erro ao transferir arquivos: {e}")

# Executar migração com upsert via DuckDB
migrate_files(minio_client, source_bucket, dest_bucket, base_prefix)
