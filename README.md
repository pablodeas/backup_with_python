# Script de Backup com Gzip

Um script Python para realizar backups de diretórios com compressão gzip, incluindo sistema de logs e gerenciamento automático de backups antigos.

## Funcionalidades

- **Compressão de diretórios completos** usando formato tar.gz
- **Sistema de logs detalhado** no console e em arquivos
- **Rotação automática de backups** mantendo apenas os mais recentes
- **Estatísticas de backup** com tamanho original, comprimido e taxa de compressão
- **Medição de performance** com tempo de execução

## Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão: os, gzip, shutil, datetime, argparse, glob, logging, pathlib

## Instalação

Clone o repositório ou baixe o arquivo `backup_script.py`. O script não requer instalação adicional.

```bash
chmod +x backup_script.py  # Tornar o script executável (opcional)
```

## Uso

### Exemplo básico:

```bash
python backup_script.py /caminho/pasta/origem /caminho/pasta/destino
```

### Opções disponíveis:

```bash
python backup_script.py [pasta_origem] [pasta_destino] [opções]

Opções:
  -c, --compressao INT   Nível de compressão (1-9, padrão: 6)
  -m, --manter INT       Quantidade de backups a manter (padrão: 5)
  -l, --log ARQUIVO      Arquivo para salvar os logs
  -v, --verbose          Exibir mensagens detalhadas
  -h, --help             Mostrar ajuda
```

### Exemplos de uso:

```bash
# Backup com alta compressão, mantendo 10 backups
python backup_script.py /dados/importantes /backups/dados -c 9 -m 10

# Backup com log detalhado em arquivo específico
python backup_script.py /home/usuario/docs /mnt/backup/docs -v -l /var/log/meu_backup.log
```

## Estrutura de logs

Os logs são salvos por padrão em um subdiretório `logs` dentro da pasta de destino. Cada arquivo de log contém:

- Timestamp de início/fim
- Informações sobre o diretório de origem/destino
- Estatísticas de tamanho e compressão
- Detalhes sobre arquivos removidos durante a rotação
- Erros encontrados durante o processo

## Agendamento

Para executar o backup regularmente, considere usar o cron:

```bash
# Exemplo de entrada no crontab para backup diário às 3:00
0 3 * * * /usr/bin/python3 /caminho/para/backup_script.py /origem /destino >> /var/log/cron_backup.log 2>&1
```