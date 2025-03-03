import os
import pandas as pd
import duckdb
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    "192.168.64.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Nome do bucket principal
bucket_name = "datalake"
silver_prefix = "silveranalitics/"

# Verificar se o bucket 'datalake' existe
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"✅ Bucket '{bucket_name}' criado com sucesso.")
    else:
        print(f"ℹ️ Bucket '{bucket_name}' já existe.")
except S3Error as e:
    print(f"⚠️ Erro ao verificar/criar o bucket '{bucket_name}': {e}")

# Criar um placeholder para garantir que 'silveranalitics/' existe
try:
    temp_file = "/tmp/.keep"
    with open(temp_file, "w") as f:
        f.write("placeholder")
    minio_client.fput_object(bucket_name, silver_prefix + ".keep", temp_file)
    print(f"📂 'silveranalitics/' inicializado no bucket '{bucket_name}'.")
except S3Error as e:
    print(f"⚠️ Erro ao criar placeholder para 'silveranalitics/': {e}")

# Mapeamento dos arquivos de origem e destino
file_mapping = {
    "Fornecedor": {
        "source_files": ["fornecedores_db1.csv", "fornecedores_db2.csv", "fornecedores_db3.csv"],
        "dest_file": silver_prefix + "silverAnaliticsFornecedor.csv",
        "id_column": "id"
    },
    "Produtos": {
        "source_files": ["produtos_db1.csv", "produtos_db2.csv", "produtos_db3.csv"],
        "dest_file": silver_prefix + "silverAnaliticsProdutos.csv",
        "id_column": "id"
    },
    "Vendas": {
        "source_files": ["vendas_db1.csv", "vendas_db2.csv", "vendas_db3.csv"],
        "dest_file": silver_prefix + "silverAnaliticsVendas.csv",
        "id_column": "id"
    },
    "Vendedor": {
        "source_files": ["vendedores_db1.csv", "vendedores_db2.csv", "vendedores_db3.csv"],
        "dest_file": silver_prefix + "silverAnaliticsVendedor.csv",
        "id_column": "id"
    }
}

def upsert_and_upload(data_category, config):
    """Realiza upsert dos arquivos CSV com DuckDB e salva no bucket MinIO."""
    try:
        dataframes = []
        
        for i, file in enumerate(config["source_files"]):
            db_folder = f"silver/db{i + 1}"
            object_path = f"{db_folder}/{file}"
            local_path = f"/tmp/{file}"
            
            try:
                minio_client.fget_object(bucket_name, object_path, local_path)
                df = pd.read_csv(local_path, sep='|')
                dataframes.append(df)
                print(f"📥 Arquivo '{file}' carregado de {db_folder}.")
            except S3Error as e:
                print(f"⚠️ Erro ao baixar '{file}' de {db_folder}: {e}")
        
        if not dataframes:
            print(f"❌ Nenhum arquivo carregado para {data_category}")
            return
        
        full_df = pd.concat(dataframes, ignore_index=True)
        
        con = duckdb.connect(database='/tmp/mydb.duckdb', read_only=False)
        con.execute("DROP TABLE IF EXISTS temp_table")
        con.register("df", full_df)
        con.execute("CREATE TABLE temp_table AS SELECT * FROM df")
        
        con.execute(f"""
            DROP TABLE IF EXISTS final_table;
            CREATE TABLE final_table AS
            SELECT DISTINCT * FROM temp_table
            ORDER BY {config["id_column"]} ASC
        """)
        
        output_file = f"/tmp/{config['dest_file'].split('/')[-1]}"
        con.execute(f"COPY final_table TO '{output_file}' (FORMAT 'CSV', DELIMITER '|')")
        
        try:
            minio_client.fput_object(bucket_name, config["dest_file"], output_file)
            print(f"✅ '{config['dest_file']}' atualizado e enviado para '{bucket_name}'.")
        except S3Error as e:
            print(f"❌ Erro ao enviar '{config['dest_file']}' para '{bucket_name}': {e}")
    
    except Exception as e:
        con.close()
        print(f"❌ Erro no processamento de {data_category}: {e}")

for category, config in file_mapping.items():
    upsert_and_upload(category, config)
