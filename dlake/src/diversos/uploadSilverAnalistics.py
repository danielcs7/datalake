import duckdb
import pandas as pd
from minio import Minio
from minio.error import S3Error
from io import BytesIO
import re

# Função para conectar ao MinIO e ao DuckDB
def upsert_silver_tables_with_duckdb(minio_client, datalake_bucket, duckdb_connection):
    try:
        # Listar todos os objetos no bucket datalake (camada silver)
        objects = minio_client.list_objects(datalake_bucket, recursive=True)
        found_files = False  # Flag para verificar se encontramos arquivos para processar

        for obj in objects:
            file_name = obj.object_name
            print(f"Verificando arquivo: {file_name}")
            
            # Verifica se o arquivo está em uma das camadas silver (silverdb1, silverdb2, silverdb3)
            match = re.match(r"^(silverdb[123])/(.*)", file_name)
            if match:
                found_files = True
                
                silver_prefix = match.group(1)  # Exemplo: "silverdb1"
                remaining_path = match.group(2)  # Exemplo: "fornecedores_DB1.parquet"

                # Ler o arquivo da camada silver
                response = minio_client.get_object(datalake_bucket, file_name)

                # Criar um buffer de BytesIO para armazenar os dados do arquivo
                parquet_buffer = BytesIO(response.read())

                # Ler o conteúdo Parquet para um DataFrame Pandas
                df = pd.read_parquet(parquet_buffer)
                

                # Separar os dados em diferentes DataFrames conforme necessário
                if silver_prefix == "silverdb1":
                    # Colunas corretas para cada tabela
                    df_produtos = df[['idProduto', 'nomeProduto', 'precoProduto', 'origem']]  # silverProdutos
                    df_vendas = df[['idVendas', 'idVendedor', 'idProduto', 'idFornecedor', 'quantidade', 'valorTotal', 'origem']]  # silverVendas
                    df_fornecedores = df[['idFornecedor', 'nomeFornecedor', 'enderecoFornecedor', 'telefoneFornecedor', 'origem']]  # silverFornecedores
                    df_vendedores = df[['idVendedor', 'nomeVendedor', 'emailVendedor', 'idadeVendedor', 'origem']]  # silverVendedores

                    # Realizar upsert para cada DataFrame usando SQL
                    upsert_table_with_duckdb(duckdb_connection, 'silverProdutos', df_produtos)
                    upsert_table_with_duckdb(duckdb_connection, 'silverVendas', df_vendas)
                    upsert_table_with_duckdb(duckdb_connection, 'silverFornecedores', df_fornecedores)
                    upsert_table_with_duckdb(duckdb_connection, 'silverVendedores', df_vendedores)

                elif silver_prefix == "silverdb2":
                    # Processar dados de silverdb2 da mesma forma
                    pass

                elif silver_prefix == "silverdb3":
                    # Processar dados de silverdb3 da mesma forma
                    pass
        
        if not found_files:
            print("Nenhum arquivo correspondente encontrado para processar.")
    
    except S3Error as e:
        print(f"Erro ao fazer upsert: {e}")

# Função para fazer upsert nas tabelas usando DuckDB
def upsert_table_with_duckdb(duckdb_connection, table_name, df):
    try:
        # Carregar o DataFrame para uma tabela temporária no DuckDB
        duckdb_connection.register('temp_table', df)
        
        # SQL para inserir ou atualizar os dados na tabela destino
        query = f"""
        INSERT INTO {table_name}
        SELECT * FROM temp_table
        ON CONFLICT (id) DO UPDATE
        SET nomeProduto = EXCLUDED.nomeProduto, precoProduto = EXCLUDED.precoProduto, origem = EXCLUDED.origem
        """
        duckdb_connection.execute(query)
        print(f"Upsert realizado com sucesso para a tabela {table_name}.")
    
    except Exception as e:
        print(f"Erro ao fazer upsert na tabela {table_name}: {e}")

# Conectar ao MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Substitua com o endereço correto
    access_key="minioadmin",  # Substitua com a chave de acesso correta
    secret_key="minioadmin",  # Substitua com a chave secreta correta
    secure=False  # Mude para True se for HTTPS
)

# Caminho para o bucket datalake
datalake_bucket = "datalake"

# Conectar ao DuckDB
duckdb_connection = duckdb.connect(database=':memory:')  # Ou forneça o caminho para um banco de dados persistente

# Chamar a função para fazer upsert nas tabelas específicas usando DuckDB
upsert_silver_tables_with_duckdb(minio_client, datalake_bucket, duckdb_connection)
