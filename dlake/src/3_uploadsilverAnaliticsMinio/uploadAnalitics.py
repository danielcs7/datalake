import os
import pandas as pd
import duckdb
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Endereço do servidor MinIO
    access_key="minioadmin",  # Usuário
    secret_key="minioadmin",  # Senha
    secure=False  # Se False, não usa SSL
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
    
    # Enviar um arquivo fictício para garantir que o "diretório" silveranalitics existe
    minio_client.fput_object(bucket_name, silver_prefix + ".keep", temp_file)
    print(f"📂 'silveranalitics/' inicializado no bucket '{bucket_name}'.")
except S3Error as e:
    print(f"⚠️ Erro ao criar placeholder para 'silveranalitics/': {e}")

# Mapeamento dos arquivos de origem e destino
file_mapping = {
    "Fornecedor": {
        "source_files": ["fornecedores_db1.parquet", "fornecedores_db2.parquet", "fornecedores_db3.parquet"],
        "dest_file": silver_prefix + "silverAnaliticsFornecedor.parquet",
        "id_column": "idFornecedor"
    },
    "Produtos": {
        "source_files": ["produtos_db1.parquet", "produtos_db2.parquet", "produtos_db3.parquet"],
        "dest_file": silver_prefix + "silverAnaliticsProdutos.parquet",
        "id_column": "idProduto"
    },
    "Vendas": {
        "source_files": ["vendas_db1.parquet", "vendas_db2.parquet", "vendas_db3.parquet"],
        "dest_file": silver_prefix + "silverAnaliticsVendas.parquet",
        "id_column": "idVendas"
    },
    "Vendedor": {
        "source_files": ["vendedores_db1.parquet", "vendedores_db2.parquet", "vendedores_db3.parquet"],
        "dest_file": silver_prefix + "silverAnaliticsVendedor.parquet",
        "id_column": "idVendedor"
    }
}

def upsert_and_upload(data_category, config):
    """Realiza upsert dos arquivos com DuckDB e salva no bucket datalake/silveranalitics."""
    try:
        dataframes = []
        
        # Baixa e carrega os arquivos Parquet
        for i, file in enumerate(config["source_files"]):
            db_folder = f"silver/silverdb{i + 1}"  # Exemplo: silver/silverdb1
            object_path = f"{db_folder}/{file}"
            local_path = f"/tmp/{file}"
            
            try:
                minio_client.fget_object(bucket_name, object_path, local_path)
                df = pd.read_parquet(local_path)
                dataframes.append(df)
                print(f"📥 Arquivo '{file}' carregado de {db_folder}.")
            except S3Error as e:
                print(f"⚠️ Erro ao baixar '{file}' de {db_folder}: {e}")
        
        if not dataframes:
            print(f"❌ Nenhum arquivo carregado para {data_category}")
            return
        
        # Concatena os DataFrames
        full_df = pd.concat(dataframes, ignore_index=True)
        
        # Usando DuckDB para realizar operações de upsert (remover duplicatas)
        con = duckdb.connect(database='/tmp/mydb.duckdb', read_only=False)

        # Dropar a tabela caso já exista
        con.execute("DROP TABLE IF EXISTS temp_table")

        # Criar a tabela temporária no DuckDB
        con.register("df", full_df)
        con.execute("CREATE TABLE temp_table AS SELECT * FROM df")

        # Remover duplicatas com base na coluna de ID
        con.execute(f"""
            DROP TABLE IF EXISTS final_table;
            CREATE TABLE final_table AS
            SELECT DISTINCT * FROM temp_table
            ORDER BY {config["id_column"]} ASC
        """)
        
        # Exportar os resultados para um novo arquivo Parquet
        output_file = f"/tmp/{config['dest_file'].split('/')[-1]}"  # Apenas o nome do arquivo
        con.execute(f"COPY final_table TO '{output_file}' (FORMAT 'PARQUET')")
        
        # Enviar para o MinIO dentro de "silveranalitics"
        try:
            minio_client.fput_object(bucket_name, config["dest_file"], output_file)
            print(f"✅ '{config['dest_file']}' atualizado e enviado para '{bucket_name}'.")
        except S3Error as e:
            print(f"❌ Erro ao enviar '{config['dest_file']}' para '{bucket_name}': {e}")

    except Exception as e:
        con.close()
        print(f"❌ Erro no processamento de {data_category}: {e}")

# Processar cada conjunto de arquivos
for category, config in file_mapping.items():
    upsert_and_upload(category, config)
