import duckdb
import random
from faker import Faker

fake = Faker("pt_BR")

# Caminhos dos bancos de dados DuckDB
db_paths = {
    "DB1": "db1.duckdb",
    "DB2": "db2.duckdb",
    "DB3": "db3.duckdb"
}

# Função para pegar o último ID da tabela
def get_last_id(conn, table_name):
    result = conn.execute(f"SELECT MAX(id) FROM {table_name}").fetchone()
    return result[0] if result[0] else 0  # Retorna 0 caso a tabela esteja vazia

# Função para inserir dados
def insert_data(db_name, db_path, fornecedores_count, produtos_count, vendas_count):
    conn = duckdb.connect(db_path)

    # Obter o último ID de cada tabela para garantir a sequência correta
    last_fornecedor_id = get_last_id(conn, "fornecedores")
    last_produto_id = get_last_id(conn, "produtos")
    last_vendedor_id = get_last_id(conn, "vendedores")
    last_venda_id = get_last_id(conn, "vendas")

    # Inserir novos fornecedores
    fornecedores = []
    for i in range(last_fornecedor_id + 1, last_fornecedor_id + 1 + fornecedores_count):
        fornecedores.append((i, fake.company(), fake.address(), fake.phone_number()))
    
    conn.executemany("INSERT INTO fornecedores VALUES (?, ?, ?, ?)", fornecedores)

    # Inserir novos produtos
    produtos = []
    for i in range(last_produto_id + 1, last_produto_id + 1 + produtos_count):
        produtos.append((i, fake.word().capitalize(), round(random.uniform(10, 1000), 2)))
    
    conn.executemany("INSERT INTO produtos VALUES (?, ?, ?)", produtos)

    # Inserir vendedores
    vendedores = []
    for i in range(last_vendedor_id + 1, last_vendedor_id + 1 + 5):  # 5 vendedores
        vendedores.append((i, fake.name(), fake.email(), random.randint(20, 50)))
    
    conn.executemany("INSERT INTO vendedores VALUES (?, ?, ?, ?)", vendedores)

    # Inserir vendas
    vendas = []
    for i in range(last_venda_id + 1, last_venda_id + 1 + vendas_count):
        vendedor_id = random.randint(last_vendedor_id + 1, last_vendedor_id + 5)  # Vendedores entre 1 e 5
        produto_id = random.randint(last_produto_id + 1, last_produto_id + produtos_count)
        fornecedor_id = random.randint(last_fornecedor_id + 1, last_fornecedor_id + fornecedores_count)
        quantidade = random.randint(1, 10)
        preco = next(p[2] for p in produtos if p[0] == produto_id)
        valor_total = round(preco * quantidade, 2)
        data_venda = fake.date_this_decade()

        vendas.append((i, vendedor_id, produto_id, fornecedor_id, quantidade, valor_total, str(data_venda)))
    
    conn.executemany("INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?, ?)", vendas)

    conn.close()
    print(f"Banco {db_name} atualizado com novos dados!")

# Inserir dados nas bases de dados
insert_data("DB1", db_paths["DB1"], fornecedores_count=3, produtos_count=5, vendas_count=7)
insert_data("DB2", db_paths["DB2"], fornecedores_count=4, produtos_count=6, vendas_count=10)
insert_data("DB3", db_paths["DB3"], fornecedores_count=5, produtos_count=8, vendas_count=12)

print("Todos os dados foram inseridos nas bases DuckDB!")
