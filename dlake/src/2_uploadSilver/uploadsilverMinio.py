import os
import pandas as pd
from minio import Minio
from minio.error import S3Error

# Configuração do MinIO
minio_client = Minio(
    "127.0.0.1:9001",  # Endereço do servidor MinIO
    access_key="minioadmin",  # Usuário
    secret_key="minioadmin",  # Senha
    secure=False  # Se False, não usa SSL
)

# Mapeamento de arquivos para suas respectivas subpastas
sub_prefix_mapping = {
    "db1": "silverdb1",
    "db2": "silverdb2",
    "db3": "silverdb3"
}

# Mapeamento de colunas para renomeação
column_mappings = {
    "db1": {
        "fornecedores_DB1": {
            "id": "idFornecedor",
            "nome": "nomeFornecedor",
            "endereco": "enderecoFornecedor",
            "telefone": "telefoneFornecedor",
            "origem": "origem"
        },
        "produtos_DB1": {
            "id": "idProduto",
            "nome": "nomeProduto",
            "preço": "precoProduto",
            "origem": "origem"
        },
        "vendas_DB1": {
            "id": "idVendas",
            "vendedor_id": "idVendedor",
            "produto_id": "idProdutos",
            "fornecedor_id": "idFornecedor",
            "quantidade": "quantidade",
            "valor_total": "valorTotal",
            "origem": "origem"
        },
        "vendedores_DB1": {
            "id": "idVendedor",
            "nome": "nomeVendedor",
            "email": "emailVendedor",
            "idade": "idadeVendedor",
            "origem": "origem"
        }
    },
    "db2": {
        "fornecedores_DB2": {
            "id": "idFornecedor",
            "nome": "nomeFornecedor",
            "endereco": "enderecoFornecedor",
            "telefone": "telefoneFornecedor",
            "origem": "origem"
        },
        "produtos_DB2": {
            "id": "idProduto",
            "nome": "nomeProduto",
            "preço": "precoProduto",
            "origem": "origem"
        },
        "vendas_DB2": {
            "id": "idVendas",
            "vendedor_id": "idVendedor",
            "produto_id": "idProdutos",
            "fornecedor_id": "idFornecedor",
            "quantidade": "quantidade",
            "valor_total": "valorTotal",
            "origem": "origem"
        },
        "vendedores_DB2": {
            "id": "idVendedor",
            "nome": "nomeVendedor",
            "email": "emailVendedor",
            "idade": "idadeVendedor",
            "origem": "origem"
        }
    },
    "db3": {
        "fornecedores_DB3": {
            "id": "idFornecedor",
            "nome": "nomeFornecedor",
            "endereco": "enderecoFornecedor",
            "telefone": "telefoneFornecedor",
            "origem": "origem"
        },
        "produtos_DB3": {
            "id": "idProduto",
            "nome": "nomeProduto",
            "preço": "precoProduto",
            "origem": "origem"
        },
        "vendas_DB3": {
            "id": "idVendas",
            "vendedor_id": "idVendedor",
            "produto_id": "idProdutos",
            "fornecedor_id": "idFornecedor",
            "quantidade": "quantidade",
            "valor_total": "valorTotal",
            "origem": "origem"
        },
        "vendedores_DB3": {
            "id": "idVendedor",
            "nome": "nomeVendedor",
            "email": "emailVendedor",
            "idade": "idadeVendedor",
            "origem": "origem"
        }
    }
}

# Função para upload
def upload_files_to_minio(source_dir, bucket_name, base_prefix, minio_client):
    try:
        # Verifica se o bucket existe
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' criado com sucesso.")
        else:
            print(f"ℹ️ Bucket '{bucket_name}' já existe.")

        # Lista arquivos na pasta local
        arquivos = [f for f in os.listdir(source_dir) if f.endswith(".parquet")]
        if not arquivos:
            print(f"⚠️ Nenhum arquivo .parquet encontrado em {source_dir}")
            return

        print(f"📂 Arquivos encontrados: {arquivos}")

        # Processa cada arquivo
        for filename in arquivos:
            arquivo_enviado = False
            
            for key, sub_prefix in sub_prefix_mapping.items():
                for file_key, column_mapping in column_mappings[key].items():
                    if file_key.lower() in filename.lower():  # Verifica qual base o arquivo pertence
                        full_prefix = f"{base_prefix}/{sub_prefix}"
                        local_file = os.path.join(source_dir, filename)
                        object_name = f"{full_prefix}/{filename}"
                        
                        # Lê o arquivo e renomeia as colunas
                        df = pd.read_parquet(local_file)
                        df.rename(columns=column_mapping, inplace=True)
                        
                        temp_file = os.path.join(source_dir, f"temp_{filename}")
                        df.to_parquet(temp_file)  # Salva temporariamente
                        local_file = temp_file
                        
                        print(f"⬆️ Enviando '{filename}' para '{bucket_name}/{object_name}'...")
                        minio_client.fput_object(bucket_name, object_name, local_file)
                        print(f"✅ '{filename}' enviado com sucesso!")

                        if "temp_" in local_file:
                            os.remove(local_file)  # Remove arquivo temporário

                        arquivo_enviado = True
                        break  # Sai do loop

            if not arquivo_enviado:
                print(f"⚠️ '{filename}' não corresponde a nenhuma regra e não foi enviado.")
    except S3Error as e:
        print(f"❌ Erro ao enviar arquivo para o MinIO: {e}")

# Configurações
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"
bucket_name = "datalake"
base_prefix = "silver"

# Chamar a função de upload
upload_files_to_minio(source_dir, bucket_name, base_prefix, minio_client)
