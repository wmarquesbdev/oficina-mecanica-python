# Sistema Oficina Mecânica

Aplicação desktop em **Python + Tkinter + SQLite** para gerenciar clientes, veículos, serviços e ordens de serviço de uma oficina. Funciona em janela única, com login.

## Como testar

1. Instale o **Python 3.10+** (no Windows, marque *Add Python to PATH* na instalação). Tkinter e SQLite já vêm com o Python — não precisa instalar mais nada.
2. Na pasta do projeto, abra o terminal e rode:
   ```
   python app.py
   ```
3. Faça login:
   - **Usuário:** `admin`
   - **Senha:** `1234`

O banco `oficina.db` é criado sozinho na primeira execução (com o usuário `admin` e alguns serviços de exemplo).

## O que o sistema faz

- **Início** — painel com os totais (clientes, carros, serviços, ordens) e o faturamento das OS concluídas.
- **Clientes / Carros / Serviços** — cadastrar, editar, excluir e buscar.
- **Ordens de Serviço** — abrir uma OS com vários serviços (total calculado automaticamente), filtrar por status, ver o resumo e exportar.
- **Usuários** — cadastrar quem pode acessar o sistema (login e senha). O `admin` cria os usuários e repassa o login.

As listas têm **busca**, **ordenação por coluna** (clique no cabeçalho) e **exportação em CSV**.

## Arquivos

| Arquivo | Função |
|---|---|
| `app.py` | Interface gráfica (telas e navegação) |
| `database.py` | Banco de dados e funções de acesso aos dados |
| `oficina.db` | Banco de dados SQLite |