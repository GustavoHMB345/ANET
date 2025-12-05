# 📦 Sistema de Importação e Análise de Aparatos (JSON/BLOB)

Este projeto é uma aplicação de **Engenharia de Dados e Visualização** desenvolvida em Python. O sistema conecta-se a um banco de dados MySQL, extrai Notas Fiscais armazenadas em formato binário (`BLOB`), decodifica o conteúdo JSON e filtra automaticamente equipamentos de informática (Notebooks e Computadores) para exibição em um dashboard interativo.

## 🚀 Funcionalidades

- **Extração de BLOB SQL**: Leitura de dados binários diretamente do MySQL e conversão para string UTF-8.
- **Parsing de JSON**: Tratamento de estruturas de dados semi-estruturadas (JSON) dentro de um banco relacional.
- **Filtragem Inteligente**: Identificação automática de itens como "Notebook", "Computador" ou "PC" dentro dos itens da nota fiscal.
- **Visualização de Dados**: Interface web interativa construída com Streamlit.
- **Drill-down**: Possibilidade de inspecionar o JSON bruto da nota fiscal original de cada produto.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.x
- **Interface/Frontend**: [Streamlit](https://streamlit.io/)
- **Manipulação de Dados**: [Pandas](https://pandas.pydata.org/)
- **Banco de Dados**: MySQL (via `mysql-connector-python`)
- **IDE/Ferramentas**: VS Code, MySQL Workbench

## ⚙️ Pré-requisitos

Antes de começar, certifique-se de ter instalado:
- Python 3.8 ou superior
- Servidor MySQL rodando localmente ou remotamente

## 📥 Instalação e Configuração

1. **Clone o repositório** (ou baixe os arquivos):
   ```bash
   git clone [https://github.com/seu-usuario/seu-projeto.git](https://github.com/seu-usuario/seu-projeto.git)
   cd seu-projeto