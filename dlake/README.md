
agora um outro desafio que é criar uma silverFornecedores, uma silverProdutos , uma silverVendedores e uma silverVendas. como funciona a lógica a tabela silverFornecedores irá conter somente dados dos fornecedores da silverbd1,silverdb2 e silverdb3 e assim por diante



que bom em perguntar dos projetos. Tenho um grande desefio para você. tenho um projeto de datalake feito com poetry nessa pasta /Volumes/MACBACKUP/workspaceDlake/dlake dentro dela tenho outra pasta chamada src e dentro da src existem essas pastas: 0_uploadLandzone, 1_uploadBronze,2_uploadSilver,3_uploadsilverAnaliticsMinio,4_uploadgoldMinio. O que desejo é criar um fluxo no airflow para executar os arquivos python que cada pasta. na pasta 0_uploadLandzone, tenho o arquivo  uploadLandzone.py que será executado de minuto a minuto observando se existe dados nessa pasta /Volumes/MACBACKUP/workspaceDlake/dlake/base e enviado para a camada landzone ou utilize esse script import os
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from minio import Minio
from minio.error import S3Error

# Configurações do MinIO
minio_client = Minio(
    "127.0.0.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "landzone"
source_dir = "/Volumes/MACBACKUP/workspaceDlake/dlake/base"
log_file = "/tmp/minio_uploaded_files.log"  # Arquivo para armazenar arquivos já enviados

# Função para carregar arquivos já enviados
def load_uploaded_files():
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            return set(f.read().splitlines())
    return set()

# Função para salvar arquivos enviados
def save_uploaded_file(file_name):
    with open(log_file, "a") as f:
        f.write(file_name + "\n")

# Função para verificar e enviar arquivos novos
def upload_new_files():
    uploaded_files = load_uploaded_files()
    try:
        if not minio_client.bucket_exists(bucket_name):
            logging.error(f"Bucket {bucket_name} não encontrado!")
            return

        for file_name in os.listdir(source_dir):
            file_path = os.path.join(source_dir, file_name)

            if os.path.isfile(file_path) and file_name not in uploaded_files:
                object_name = f"landzone/{file_name}"
                logging.info(f"Enviando {file_path} para {object_name}...")

                minio_client.fput_object(bucket_name, object_name, file_path)
                logging.info(f"Arquivo {file_name} enviado com sucesso para {object_name}!")

                save_uploaded_file(file_name)  # Registra arquivo como enviado

    except S3Error as e:
        logging.error(f"Erro ao acessar o MinIO: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")

# Configuração da DAG no Airflow
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "upload_to_minio",
    default_args=default_args,
    description="Verifica e envia arquivos novos para o MinIO",
    schedule_interval=timedelta(minutes=10),  # Roda a cada 10 minutos
    catchup=False,
)

upload_task = PythonOperator(
    task_id="check_and_upload_files",
    python_callable=upload_new_files,
    dag=dag,
)

upload_task
 depois irá rodar o script da pasta 1_uploadBronze que é 1_upsertBronze.py , DEPOIS IRÁ rodar o script da pasta 2_uploadSilver que é 2_upsertSilver.py, depois ira rodar o script da psta 3_uploadsilverAnaliticsMinio que é uploadAnalitics.py e por ultimo rodar o script da pasta 4_uploadgoldMinio que é 4_uploadgoldMinio



 essa é minha conexao com o minio minio_client = Minio(
    "127.0.0.1:9001",  # URL do MinIO
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
) essa é a minha variavel bronze_bucket = "datalake/bronze" onde informo o endereço do meu bucket onde tem o bucket datalake e dentro dele o bronze - aqui chamo a função bronze_files = list_files(bronze_bucket) e essa é minha função # Função para listar arquivos em um bucket
def list_files(bucket_name, prefix=""):
    if not minio_client.bucket_exists(bucket_name):
        print(f"Bucket '{bucket_name}' não existe.")
        return [] só que no bucket datalake tenho a subpasta bronze e dentro tenho outras subspastas que são db1 db2 e db3 e dentro de cada uma tenho os arquivos 
    
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        print(f"Erro ao listar arquivos no bucket '{bucket_name}': {e}")
        return [] só que 



datalake/
     bronze/
        db1/
          fornecedores/
                     fornecedores_db1.parquet
          produtos/
                  produtos_db1.parquet
        db2/
          fornecedores/
                     fornecedores_db2.parquet
          produtos/
                  produtos_db2.parquet
                                     
datalake/
     bronze/
        db1/
          fornecedores_db1.parquet
          produtos_db1.parquet
        db2/
          fornecedores_db2.parquet
          produtos_db2.parquet

datalake/
     silver/
        db1/
          fornecedores_db1.parquet
          produtos_db1.parquet
        db2/
          fornecedores_db2.parquet
          produtos_db2.parquet

datalake/
     silveranalitics/
            fornecedores.parquet
            produtos.parquet


