from minio import Minio
import pandas as pd
import io

# Configuração do MinIO
minio_client = Minio(
    "127.0.0.1:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Bucket único e prefixos
bucket = "datalake"
bronze_prefix = "bronze"
silver_prefix = "silver"

# Listar diretórios dentro da Bronze
objects = minio_client.list_objects(bucket, prefix=bronze_prefix, recursive=True)

# Identificar os arquivos Parquet por database
files_by_db = {}
for obj in objects:
    parts = obj.object_name.split("/")
    if len(parts) > 2:  # Exemplo: "bronze/bronzedb1/fornecedores_db1.parquet"
        db_name = parts[1]  # bronzedb1, bronzedb2...
        file_name = parts[2]
        if db_name not in files_by_db:
            files_by_db[db_name] = []
        files_by_db[db_name].append(file_name)

# Processar cada database e seus arquivos Parquet
for db_name, files in files_by_db.items():
    silver_db_name = db_name.replace("bronzedb", "silverdb")  # Ajusta nome para Silver
    for file_name in files:
        bronze_path = f"{bronze_prefix}/{db_name}/{file_name}"
        silver_path = f"{silver_prefix}/{silver_db_name}/{file_name}"

        # Baixar Parquet da Bronze
        response = minio_client.get_object(bucket, bronze_path)
        bronze_df = pd.read_parquet(io.BytesIO(response.read()))

        try:
            # Tentar baixar Parquet da Silver para comparação
            response = minio_client.get_object(bucket, silver_path)
            silver_df = pd.read_parquet(io.BytesIO(response.read()))

            # Comparar e atualizar
            merged_df = pd.concat([silver_df, bronze_df]).drop_duplicates()
        except Exception:  # Se o arquivo não existir na Silver
            merged_df = bronze_df

        # Salvar o novo Parquet na Silver
        output_buffer = io.BytesIO()
        merged_df.to_parquet(output_buffer, engine="pyarrow", index=False)
        output_buffer.seek(0)

        # Upload para a Silver dentro do mesmo bucket
        minio_client.put_object(
            bucket,
            silver_path,
            data=output_buffer,
            length=output_buffer.getbuffer().nbytes,
            content_type="application/parquet"
        )

print("Processamento concluído!")
