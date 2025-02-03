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

# Função para criar um banco e popular com dados
def create_and_populate_db(db_name, db_path, fornecedores_count, produtos_count):
    conn = duckdb.connect(db_path)

    # Criando tabelas
    conn.execute("""
        CREATE TABLE fornecedores (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            endereco TEXT,
            telefone TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            preco FLOAT
        )
    """)

    conn.execute("""
        CREATE TABLE vendedores (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            email TEXT,
            idade INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE vendas (
            id INTEGER PRIMARY KEY,
            vendedor_id INTEGER,
            produto_id INTEGER,
            fornecedor_id INTEGER,
            quantidade INTEGER,
            valor_total FLOAT,
            data TEXT
        )
    """)

    # Inserindo fornecedores únicos para este banco
    fornecedores = []
    for i in range(1, fornecedores_count + 1):
        fornecedores.append((i, fake.company(), fake.address(), fake.phone_number()))
    
    conn.executemany("INSERT INTO fornecedores VALUES (?, ?, ?, ?)", fornecedores)

    # Inserindo produtos únicos para este banco
    produtos = []
    for i in range(1, produtos_count + 1):
        produtos.append((i, fake.word().capitalize(), round(random.uniform(10, 1000), 2)))
    
    conn.executemany("INSERT INTO produtos VALUES (?, ?, ?)", produtos)

    # Inserindo vendedores (podem se repetir entre bancos)
    vendedores = []
    for i in range(1, 6):  # 5 vendedores comuns
        vendedores.append((i, fake.name(), fake.email(), random.randint(20, 50)))
    
    conn.executemany("INSERT INTO vendedores VALUES (?, ?, ?, ?)", vendedores)

    # Inserindo vendas (baseadas nos produtos e fornecedores deste banco)
    vendas = []
    for i in range(1, 10):  # 10 vendas
        vendedor_id = random.randint(1, 5)
        produto_id = random.randint(1, produtos_count)
        fornecedor_id = random.randint(1, fornecedores_count)
        quantidade = random.randint(1, 10)
        preco = next(p[2] for p in produtos if p[0] == produto_id)
        valor_total = round(preco * quantidade, 2)
        data_venda = fake.date_this_decade()

        vendas.append((i, vendedor_id, produto_id, fornecedor_id, quantidade, valor_total, str(data_venda)))

    conn.executemany("INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?, ?)", vendas)

    conn.close()
    print(f"Banco {db_name} criado e populado com sucesso!")

# Criando DB1, DB2 e DB3 com quantidades diferentes de fornecedores e produtos
create_and_populate_db("DB1", db_paths["DB1"], fornecedores_count=5, produtos_count=10)
create_and_populate_db("DB2", db_paths["DB2"], fornecedores_count=7, produtos_count=12)
create_and_populate_db("DB3", db_paths["DB3"], fornecedores_count=6, produtos_count=15)

print("Todos os bancos DuckDB foram criados!")
