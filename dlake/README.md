
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
