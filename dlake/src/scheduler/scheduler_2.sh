#!/bin/bash

echo "Em processamento UPLOAD BRONZE..."

#Caminho para o diretorio do projeto
cd /Volumes/MACBACKUP/workspaceDlake/dlake || {
    echo "Erro: Diretorio nao ecnontrado"
    exit 1
}

# ATIVA O AMBIENTE VIRTUAL
source .venv/bin/activate || {
    echo "Error: Nao foi possívl ativar o ambiente virtual"
    exit 1
}

# Executa o script Python
python src/s_uploadSilver/1_upsertSilver.py || {
    echo "Error: O script Python encontrou um problema"
    deactivate
    exit 1
}

echo "Processo Finalizado"

#desativa o ambiente virtual
deactivate