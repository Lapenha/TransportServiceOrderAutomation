# Loop Adventure

Aplicativo desktop local para criacao e gerenciamento de Ordens de Servico da Loop Adventure.

## Funcionalidades

- Criar, editar, buscar, excluir e gerar PDF de O.S.
- Cadastro de clientes com documento e telefone.
- Cadastro de prestadores com apelido, documento e telefone.
- Cadastro de motoristas com nome completo, CPF, CNH e telefone.
- Cadastro de veiculos com tipo, placa e prefixo.
- Tipos de O.S.: `So ida`, `So retorno` e `Servico completo`.
- Multiplos trechos apenas para `Servico completo`.
- Campo `Criado por` salvo no banco de dados.
- PDF com logo da Loop Adventure e campos de KM em branco para preenchimento manual.
- Banco local SQLite, sem Docker, sem servidor e sem internet.

## Tecnologias

- Python
- CustomTkinter
- SQLAlchemy
- SQLite
- ReportLab
- Pillow
- PyInstaller

## Como Rodar Em Desenvolvimento

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\scripts\run.ps1
```

O banco de desenvolvimento e criado em:

```text
data\os_transport.db
```

## Gerar Executavel

```powershell
.\scripts\build.ps1
```

O executavel sera gerado em:

```text
release\Loop Adventure\Loop Adventure.exe
```

Para criar o atalho na area de trabalho:

```powershell
.\scripts\create_desktop_shortcut.ps1
```

## Instalar Em Outro Computador

Envie a pasta completa:

```text
release\Loop Adventure
```

Nao envie apenas o `.exe`, porque ele depende da pasta `_internal`.

No outro computador nao precisa instalar Python, Docker ou banco de dados. Basta extrair a pasta e abrir:

```text
Loop Adventure.exe
```

## Banco De Dados Na Versao Instalada

Na versao empacotada, o banco fica dentro da propria pasta do aplicativo:

```text
Loop Adventure\data\os_transport.db
```

Esse arquivo guarda clientes, prestadores, motoristas, veiculos e ordens de servico mesmo apos fechar ou reiniciar o computador.

## Arquivos Que Nao Devem Ir Para O GitHub

O projeto ignora automaticamente:

- `.env`
- `.venv`
- bancos SQLite em `data/`
- builds em `build/`, `dist/`, `release/` e `release_v*/`
- arquivos `.zip`
- arquivos temporarios Python
