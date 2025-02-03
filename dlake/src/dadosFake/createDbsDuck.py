import duckdb
import faker
import random
from datetime import datetime, timedelta

# Inicializar Faker para dados fictícios
fake = faker.Faker()

def create_fake_data(n=100):
    fornecedores = [(i, fake.company(), fake.address(), fake.phone_number()) for i in range(1, n+1)]
    vendedores = [(i, fake.name(), fake.email(), random.randint(20, 60)) for i in range(1, n+1)]
    produtos = [(i, fake.word(), round(random.uniform(10, 500), 2)) for i in range(1, n+1)]
    vendas = [
        (
            i,
            random.randint(1, n),  # ID do vendedor
            random.randint(1, n),  # ID do produto
            random.randint(1, n),  # ID do fornecedor
            round(random.uniform(1, 10), 2),  # Quantidade
            round(random.uniform(10, 1000), 2),  # Valor total
            fake.date_between(start_date='-2y', end_date='today')
        ) 
        for i in range(1, n+1)
    ]
    return fornecedores, vendedores, produtos, vendas

def create_db(db_name):
    conn = duckdb.connect(f'{db_name}.duckdb')
    fornecedores, vendedores, produtos, vendas = create_fake_data()
    
    conn.execute("""
    CREATE TABLE fornecedores (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        endereco TEXT,
        telefone TEXT
    )"""
    )
    conn.executemany("INSERT INTO fornecedores VALUES (?, ?, ?, ?)", fornecedores)
    
    conn.execute("""
    CREATE TABLE vendedores (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        email TEXT,
        idade INTEGER
    )"""
    )
    conn.executemany("INSERT INTO vendedores VALUES (?, ?, ?, ?)", vendedores)
    
    conn.execute("""
    CREATE TABLE produtos (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        preco REAL
    )"""
    )
    conn.executemany("INSERT INTO produtos VALUES (?, ?, ?)", produtos)
    
    conn.execute("""
    CREATE TABLE vendas (
        id INTEGER PRIMARY KEY,
        vendedor_id INTEGER,
        produto_id INTEGER,
        fornecedor_id INTEGER,
        quantidade REAL,
        valor_total REAL,
        data_venda DATE,
        FOREIGN KEY (vendedor_id) REFERENCES vendedores(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
    )"""
    )
    conn.executemany("INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?, ?)", vendas)
    
    conn.close()
    print(f"Banco {db_name} criado com sucesso!")

# Criar os bancos de dados DB1, DB2 e DB3
for db in ['DB1', 'DB2', 'DB3']:
    create_db(db)
