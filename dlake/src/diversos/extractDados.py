import duckdb
import pandas as pd

# Caminhos dos bancos de dados DuckDB
db_paths = {
    "DB1": "db1.duckdb",
    "DB2": "db2.duckdb",
    "DB3": "db3.duckdb"
}

# Função para adicionar a coluna de origem e salvar como parquet
def save_to_parquet(conn, table_name, db_name, output_path):
    # Extrair os dados da tabela
    df = conn.execute(f"SELECT * FROM {table_name}").df()

    # Adicionar a coluna de origem
    df['origem'] = db_name

    # Salvar em .parquet
    df.to_parquet(f"{output_path}/{table_name}_{db_name}.parquet", index=False)
    print(f"Tabela {table_name} de {db_name} salva como {table_name}_{db_name}.parquet")

# Função para extrair os dados de todas as tabelas e gerar arquivos .parquet
def extract_and_save_data():
    output_path = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"  # Caminho de saída para os arquivos .parquet
    
    # Processar os bancos de dados
    for db_name, db_path in db_paths.items():
        conn = duckdb.connect(db_path)
        
        # Extrair e salvar dados das tabelas
        for table in ["fornecedores", "produtos", "vendedores", "vendas"]:
            save_to_parquet(conn, table, db_name, output_path)

        conn.close()

# Rodar a função para extrair e salvar os dados
extract_and_save_data()

print("Todos os dados foram extraídos e salvos em .parquet!")
