import os
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
    "db1": "bronzedb1",
    "db2": "bronzedb2",
    "db3": "bronzedb3"
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

            # Verifica em qual subpasta ele deve ser colocado
            for key, sub_prefix in sub_prefix_mapping.items():
                if key in filename.lower():  # Transforma em minúsculas para evitar erros
                    full_prefix = f"{base_prefix}/{sub_prefix}"
                    local_file = os.path.join(source_dir, filename)
                    object_name = f"{full_prefix}/{filename}"

                    print(f"⬆️ Enviando '{filename}' para '{bucket_name}/{object_name}'...")
                    minio_client.fput_object(bucket_name, object_name, local_file)
                    print(f"✅ '{filename}' enviado com sucesso!")
                    arquivo_enviado = True
                    break  # Sai do loop assim que encontra a correspondência correta
            
            if not arquivo_enviado:
                print(f"⚠️ '{filename}' não corresponde a nenhuma regra e não foi enviado.")

    except S3Error as e:
        print(f"❌ Erro ao enviar arquivo para o MinIO: {e}")

# Configurações
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"
bucket_name = "datalake"
base_prefix = "bronze"

# Chamar a função de upload
upload_files_to_minio(source_dir, bucket_name, base_prefix, minio_client)
