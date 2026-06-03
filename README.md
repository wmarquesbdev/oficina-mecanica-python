# Sistema Oficina Mecanica

Trabalho final da disciplina **Desenvolvimento Rapido de Aplicacoes em Python** (ADS - Estacio).
Aplicacao desktop em **Python + Tkinter** com banco **SQLite**, cobrindo Login + CRUD de
Clientes, Carros, Servicos e Ordens de Servico.

---

## 1. Requisitos atendidos (enunciado)

| Item do enunciado | Onde esta no sistema |
|---|---|
| Tela de Login | `TelaLogin` (login + senha com hash SHA-256) |
| CRUD do Cliente | `TelaClientes` |
| CRUD Carro | `TelaCarros` (vinculado ao cliente via chave estrangeira) |
| CRUD do Servico | `TelaServicos` |
| CRUD Ordem de Servico | `TelaOrdens` (cliente + carro + varios servicos + total) |
| Listar a Ordem de Servico | Lista de OS na propria `TelaOrdens` |
| Icones / botoes estilo card | Menu principal com cards clicaveis |
| Arquivo do Banco de Dados | `oficina.db` (gerado pelo SQLite) |
| Sistema no Git | Ver secao 8 |
| Documento de requisitos | Arquivo .docx separado |

---

## 2. Pre-requisitos

- **Python 3.10 ou superior** (no Windows, marque "Add Python to PATH" na instalacao).
- Tkinter e sqlite3 ja vem embutidos no Python. **Nao precisa instalar nada via pip.**
  - (Apenas no Linux, se faltar Tkinter: `sudo apt install python3-tk`.)
- **SQLiteStudio** (opcional) — so para visualizar/editar o `oficina.db` manualmente.

Conferir a instalacao:
```bash
python --version
python -c "import tkinter, sqlite3; print('OK')"
```

---

## 3. Estrutura dos arquivos

```
oficina/
├── app.py          # Interface grafica (Tkinter): login, menu e telas
├── database.py     # Camada de dados: tabelas, seed e funcoes CRUD (SQLite)
├── oficina.db      # Banco de dados (criado/atualizado automaticamente)
├── .gitignore
└── README.md
```

Separacao de responsabilidades: `app.py` cuida da tela, `database.py` cuida dos dados.
Toda operacao no banco passa por uma funcao em `database.py`.

---

## 4. Como executar

```bash
cd oficina
python app.py
```

Na primeira execucao o `database.py` cria o `oficina.db` e insere os dados iniciais
(usuario padrao e 5 servicos). Se quiser criar o banco manualmente antes:
```bash
python database.py
```

**Login padrao:** usuario `admin` | senha `1234`

---

## 5. Como usar (fluxo de demonstracao)

1. Faca login com `admin` / `1234`.
2. No menu, clique no card **Clientes** e cadastre um cliente (nome e obrigatorio).
3. Clique em **Carros**, escolha o cliente no combo, informe a placa e salve.
4. Clique em **Servicos** e confira/edite a tabela de precos (ja vem com 5 servicos).
5. Clique em **Ordens de Servico** e:
   - escolha o **Cliente** (o combo de **Carro** passa a mostrar so os carros dele);
   - selecione um **Servico**, informe a **Qtd** e clique em **+ Adicionar item**
     (repita para varios servicos — o **Total** e calculado automaticamente);
   - defina o **Status** e clique em **Salvar OS**;
   - a OS aparece na lista de baixo. Clique nela para editar, ou use **Excluir OS**.

Em todas as listas, clicar em um registro carrega os dados no formulario para edicao.

---

## 6. Modelo de dados

```
usuarios(id, nome, login, senha)                                  -> senha em hash SHA-256
clientes(id, nome, cpf, telefone, email)
carros(id, cliente_id -> clientes, placa, marca, modelo, ano, cor)
servicos(id, descricao, preco)
ordens_servico(id, cliente_id -> clientes, carro_id -> carros,
               data_abertura, status, observacoes)
os_itens(id, ordem_id -> ordens_servico, servico_id -> servicos,
         quantidade, preco_unit)                                  -> itens de cada OS
```

A tabela `os_itens` liga uma OS a varios servicos (relacao N:N), demonstrando uso de
chave estrangeira e `JOIN` — conteudo do tema "Python com Banco de Dados".

---

## 7. Inspecionar o banco no SQLiteStudio

1. Abra o SQLiteStudio.
2. `Database > Add a database` e selecione o arquivo `oficina.db`.
3. Conecte (duplo clique) e abra a aba **Data** de qualquer tabela para ver/editar os registros,
   ou a aba **SQL** para rodar consultas (ex.: `SELECT * FROM ordens_servico`).

---

## 8. Git — versionamento e entrega

Pre-requisito: ter o Git instalado (`git --version`) e uma conta no GitHub.

```bash
# dentro da pasta oficina/
git init
git add .
git commit -m "Sistema Oficina: login, CRUDs e ordens de servico"
git branch -M main

# crie um repositorio vazio no GitHub e cole a URL dele abaixo:
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

O `oficina.db` deve ser enviado junto (e o "Arquivo do Banco de Dados" da entrega) —
o `.gitignore` ignora apenas `__pycache__/` e `.pyc`, nao o banco.

Para entregas seguintes:
```bash
git add .
git commit -m "descricao da mudanca"
git push
```

> **Confirmar com a professora:** o enunciado cita "EnildadaRosa - Git". O mais provavel
> e adicionar a professora como **colaboradora** do repositorio em
> `Settings > Collaborators` no GitHub. Confirme se e isso antes de finalizar.

---

## 9. Checklist de entrega

- [ ] Sistema rodando (`python app.py`) com login e os 4 CRUDs
- [ ] `oficina.db` incluido
- [ ] Repositorio no GitHub com os arquivos e os commits
- [ ] Professora adicionada como colaboradora (a confirmar)
- [ ] Documento de requisitos (.docx) finalizado
