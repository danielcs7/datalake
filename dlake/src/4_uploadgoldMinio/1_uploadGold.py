import os
import pandas as pd
import duckdb
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    #"127.0.0.1:9001",
    "192.168.64.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Nome do bucket
bucket_name = "datalake"
silver_prefix = "silveranalitics/"
gold_prefix = "gold/"

# Mapeamento de arquivos da camada *silveranalitics* e seus destinos na *gold*
gold_mapping = {
    "Fornecedor": {
        "source_file": silver_prefix + "silverAnaliticsFornecedor.parquet",
        "dest_file": gold_prefix + "goldFornecedor.parquet",
        "id_column": "id"
    },
    "Produtos": {
        "source_file": silver_prefix + "silverAnaliticsProdutos.parquet",
        "dest_file": gold_prefix + "goldProdutos.parquet",
        "id_column": "id"
    },
    "Vendas": {
        "source_file": silver_prefix + "silverAnaliticsVendas.parquet",
        "dest_file": gold_prefix + "goldVendas.parquet",
        "id_column": "id",
        "join_files": {
            "Vendedor": silver_prefix + "silverAnaliticsVendedor.parquet",
            "Produtos": silver_prefix + "silverAnaliticsProdutos.parquet",
            "Fornecedor": silver_prefix + "silverAnaliticsFornecedor.parquet"
        }
    },
    "Vendedor": {
        "source_file": silver_prefix + "silverAnaliticsVendedor.parquet",
        "dest_file": gold_prefix + "goldVendedor.parquet",
        "id_column": "id"
    }
}

def process_gold(data_category, config):
    """Cria a camada *gold* a partir dos dados da *silveranalitics*."""
    try:
        local_path = f"/tmp/{config['source_file'].split('/')[-1]}"
        
        # Baixar arquivo da *silveranalitics*
        try:
            minio_client.fget_object(bucket_name, config["source_file"], local_path)
            df = pd.read_parquet(local_path)
            print(f"📥 Arquivo '{config['source_file']}' carregado.")
        except S3Error as e:
            print(f"⚠️ Erro ao baixar '{config['source_file']}': {e}")
            return
        
        # Conectar ao DuckDB
        con = duckdb.connect(database='/tmp/mydb.duckdb', read_only=False)
        con.register("df", df)
        con.execute("DROP TABLE IF EXISTS temp_table")
        con.execute("CREATE TABLE temp_table AS SELECT * FROM df")

        # Caso seja a tabela de Vendas, realizar os *joins*
        if data_category == "Vendas" and "join_files" in config:
            for join_table, join_file in config["join_files"].items():
                join_local_path = f"/tmp/{join_file.split('/')[-1]}"
                try:
                    minio_client.fget_object(bucket_name, join_file, join_local_path)
                    join_df = pd.read_parquet(join_local_path)
                    con.register(join_table.lower(), join_df)
                    print(f"🔗 '{join_file}' carregado para *join*.")
                except S3Error as e:
                    print(f"⚠️ Erro ao baixar '{join_file}': {e}")
                    return
            
            # Executar *join* para trazer os nomes
            con.execute(f"""
                DROP TABLE IF EXISTS final_table;
                CREATE TABLE final_table AS
                SELECT 
                    v.id as idVendas, 
                    v.data as dataVenda, 
                    STRFTIME('%Y%m', CAST(v.data AS DATE)) AS anoMes,
                    CASE
                        WHEN STRFTIME('%m', CAST(v.data AS DATE)) BETWEEN '01' AND '06' THEN '1'
                        ELSE '2'
                    END AS semestre,
                    CAST((CAST(STRFTIME('%m', CAST(v.data AS DATE)) AS INTEGER) + 1) / 2 AS TEXT) AS bimestre,
                    CAST((CAST(STRFTIME('%m', CAST(v.data AS DATE)) AS INTEGER) + 2) / 3 AS TEXT) AS trimestre,         
                    v.valor_total as valorTotal, 
                    p.nome as nomeProduto, 
                    f.nome as nomeFornecedor, 
                    ve.nome as nomeVendedor
                FROM temp_table v
                LEFT JOIN produtos p ON v.id = p.id
                LEFT JOIN fornecedor f ON v.id = f.id
                LEFT JOIN vendedor ve ON v.id = ve.id
                ORDER BY v.id ASC
            """)
        else:
            # Apenas remover duplicatas para as outras tabelas
            con.execute(f"""
                DROP TABLE IF EXISTS final_table;
                CREATE TABLE final_table AS
                SELECT DISTINCT * FROM temp_table
                ORDER BY {config["id_column"]} ASC
            """)

        # Exportar resultado para *Parquet*
        output_file = f"/tmp/{config['dest_file'].split('/')[-1]}"
        con.execute(f"COPY final_table TO '{output_file}' (FORMAT 'PARQUET')")
        
        # Enviar para o MinIO na camada *gold*
        try:
            minio_client.fput_object(bucket_name, config["dest_file"], output_file)
            print(f"✅ '{config['dest_file']}' atualizado e enviado para '{bucket_name}'.")
        except S3Error as e:
            print(f"❌ Erro ao enviar '{config['dest_file']}' para '{bucket_name}': {e}")

    except Exception as e:
        print(f"❌ Erro no processamento de {data_category}: {e}")

# Processar cada conjunto de arquivos para a camada *gold*
for category, config in gold_mapping.items():
    process_gold(category, config)
