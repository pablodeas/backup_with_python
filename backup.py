#!/usr/bin/env python3

import os
import gzip
import shutil
import datetime
import argparse
import glob
import logging
from pathlib import Path


def configurar_logger(log_file=None):
    """
    Configura o sistema de logging
    
    Args:
        log_file (str): Caminho para o arquivo de log. Se None, apenas log no console
    
    Returns:
        logger: Objeto logger configurado
    """
    # Criar logger
    logger = logging.getLogger('backup_script')
    logger.setLevel(logging.INFO)
    
    # Definir formato para as mensagens de log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Adicionar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Adicionar handler para arquivo se especificado
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def comprimir_pasta(pasta_origem, arquivo_destino, nivel_compressao=6, logger=None):
    """
    Comprime uma pasta inteira em um arquivo tar.gz
    
    Args:
        pasta_origem (str): Caminho da pasta a ser comprimida
        arquivo_destino (str): Caminho do arquivo de saída
        nivel_compressao (int): Nível de compressão (1-9)
        logger: Objeto logger para registrar as operações
    """
    if logger:
        logger.info(f"Iniciando compressão da pasta {pasta_origem}")
        logger.info(f"Nível de compressão: {nivel_compressao}")
    
    try:
        # Primeiro criamos um arquivo tar temporário
        temp_tar = f"{arquivo_destino}.temp.tar"
        
        if logger:
            logger.debug(f"Criando arquivo tar temporário: {temp_tar}")
        
        # A função make_archive do shutil cria um arquivo tar
        shutil.make_archive(
            os.path.splitext(temp_tar)[0],  # Nome base (sem extensão)
            'tar',                           # Formato
            root_dir=os.path.dirname(pasta_origem),
            base_dir=os.path.basename(pasta_origem)
        )
        
        # Calculando tamanho do arquivo tar para registro
        tar_size = os.path.getsize(temp_tar)
        if logger:
            logger.debug(f"Arquivo tar criado: {temp_tar} ({tar_size} bytes)")
        
        # Agora comprimimos o arquivo tar com gzip
        if logger:
            logger.debug(f"Comprimindo arquivo tar com gzip para: {arquivo_destino}")
        
        with open(temp_tar, 'rb') as f_in:
            with gzip.open(arquivo_destino, 'wb', compresslevel=nivel_compressao) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Calculando tamanho do arquivo comprimido para log
        gz_size = os.path.getsize(arquivo_destino)
        compression_ratio = tar_size / gz_size if gz_size > 0 else 0
        
        # Removemos o arquivo tar temporário
        os.remove(temp_tar)
        
        if logger:
            logger.info(f"Backup criado com sucesso: {arquivo_destino} ({gz_size} bytes)")
            logger.info(f"Taxa de compressão: {compression_ratio:.2f}x")
        else:
            print(f"Backup criado com sucesso: {arquivo_destino}")
        
        return True
    except Exception as e:
        if logger:
            logger.error(f"Erro ao comprimir pasta: {str(e)}")
        else:
            print(f"Erro ao comprimir pasta: {str(e)}")
        return False


def limpar_backups_antigos(pasta_backup, manter_quantidade, logger=None):
    """
    Remove os backups mais antigos, mantendo apenas a quantidade especificada
    
    Args:
        pasta_backup (str): Pasta onde estão os backups
        manter_quantidade (int): Quantidade de backups a manter
        logger: Objeto logger para registrar as operações
    """
    if logger:
        logger.info(f"Verificando backups antigos em: {pasta_backup}")
        logger.info(f"Número de backups a manter: {manter_quantidade}")
    
    try:
        # Lista todos os arquivos de backup
        padrão = os.path.join(pasta_backup, "backup_*.tar.gz")
        arquivos = glob.glob(padrão)
        
        if logger:
            logger.debug(f"Total de backups encontrados: {len(arquivos)}")
        
        # Ordena os arquivos pela data de modificação (mais antigos primeiro)
        arquivos_ordenados = sorted(arquivos, key=os.path.getmtime)
        
        # Remove os arquivos excedentes (mais antigos)
        arquivos_para_remover = arquivos_ordenados[:-manter_quantidade] if len(arquivos_ordenados) > manter_quantidade else []
        
        if logger:
            logger.debug(f"Arquivos a serem removidos: {len(arquivos_para_remover)}")
        
        for arquivo in arquivos_para_remover:
            try:
                os.remove(arquivo)
                if logger:
                    logger.info(f"Backup antigo removido: {arquivo}")
                else:
                    print(f"> Backup antigo removido: {arquivo}")
            except Exception as e:
                if logger:
                    logger.error(f"Erro ao remover arquivo {arquivo}: {str(e)}")
                else:
                    print(f"Erro ao remover arquivo {arquivo}: {str(e)}")
        
        return True
    except Exception as e:
        if logger:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")
        else:
            print(f"Erro ao limpar backups antigos: {str(e)}")
        return False


def main():
    # Parse dos argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Script de backup usando gzip')
    parser.add_argument('pasta_origem', help='Pasta a ser compactada')
    parser.add_argument('pasta_destino', help='Pasta onde o backup será salvo')
    parser.add_argument('-c', '--compressao', type=int, default=6, 
                        choices=range(1, 10), help='Nível de compressão (1-9)')
    parser.add_argument('-m', '--manter', type=int, default=5,
                        help='Quantidade de backups a manter')
    parser.add_argument('-l', '--log', help='Arquivo para salvar os logs')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Exibir mensagens detalhadas')
    
    args = parser.parse_args()
    
    # Configura o diretório de logs
    log_dir = os.path.join(args.pasta_destino, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Define nome do arquivo de log com data/hora se não especificado
    if not args.log:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"backup_{timestamp}.log")
    else:
        log_file = args.log
    
    # Configura o logger
    logger = configurar_logger(log_file)
    
    if args.verbose:
        # Definir nível de log mais detalhado se verbose estiver ativado
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
    
    # Registra início do backup
    logger.info("=" * 60)
    logger.info(f"Iniciando processo de backup em {datetime.datetime.now()}")
    logger.info(f"Origem: {args.pasta_origem}")
    logger.info(f"Destino: {args.pasta_destino}")
    
    # Garante que as pastas existem
    if not os.path.exists(args.pasta_origem):
        logger.error(f"Erro: A pasta de origem '{args.pasta_origem}' não existe!")
        return
    
    os.makedirs(args.pasta_destino, exist_ok=True)
    
    # Cria nome do arquivo de backup com data e hora atual
    data_atual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_pasta = os.path.basename(os.path.normpath(args.pasta_origem))
    arquivo_backup = os.path.join(
        args.pasta_destino, 
        f"backup_{nome_pasta}_{data_atual}.tar.gz"
    )
    
    # Registra estatísticas iniciais
    tamanho_origem = calcular_tamanho_diretorio(args.pasta_origem)
    logger.info(f"Tamanho original: {tamanho_origem} bytes ({formatar_tamanho(tamanho_origem)})")
    
    # Registra hora de início
    hora_inicio = datetime.datetime.now()
    
    # Realiza o backup
    sucesso_compressao = comprimir_pasta(args.pasta_origem, arquivo_backup, args.compressao, logger)
    
    # Calcula tempo de execução
    hora_fim = datetime.datetime.now()
    duracao = hora_fim - hora_inicio
    
    if sucesso_compressao:
        # Registra estatísticas finais
        tamanho_backup = os.path.getsize(arquivo_backup)
        taxa_compressao = tamanho_origem / tamanho_backup if tamanho_backup > 0 else 0
        
        logger.info(f"Tamanho do backup: {tamanho_backup} bytes ({formatar_tamanho(tamanho_backup)})")
        logger.info(f"Taxa de compressão: {taxa_compressao:.2f}x")
        logger.info(f"Tempo de execução: {duracao.total_seconds():.2f} segundos")
        
        # Limpa backups antigos
        limpar_backups_antigos(args.pasta_destino, args.manter, logger)
    else:
        logger.error("Backup falhou!")
    
    # Registra fim do backup
    logger.info(f"Processo de backup finalizado em {datetime.datetime.now()}")
    logger.info("=" * 60)


def calcular_tamanho_diretorio(diretorio):
    """Calcula o tamanho total de um diretório em bytes"""
    tamanho_total = 0
    for dirpath, dirnames, filenames in os.walk(diretorio):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                tamanho_total += os.path.getsize(fp)
    return tamanho_total


def formatar_tamanho(tamanho_bytes):
    """Formata o tamanho em bytes para uma string legível (KB, MB, GB)"""
    for unidade in ['B', 'KB', 'MB', 'GB', 'TB']:
        if tamanho_bytes < 1024.0:
            return f"{tamanho_bytes:.2f} {unidade}"
        tamanho_bytes /= 1024.0
    return f"{tamanho_bytes:.2f} PB"


if __name__ == "__main__":
    main()