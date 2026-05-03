# 🦷 Sistema de Agendamento Odontológico

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![React](https://img.shields.io/badge/React-19-blue)
![Postgres](https://img.shields.io/badge/PostgreSQL-18-336791)
![Neon](https://img.shields.io/badge/Neon-Serverless-00e599)

> Um sistema completo para gestão de consultas odontológicas, focado em resolução de conflitos de horário, múltiplos perfis de usuário e validação robusta de dados.

---

## 📋 Sobre o Projeto

Este projeto é uma solução Fullstack para clínicas odontológicas e profissionais autônomos. O sistema utiliza uma arquitetura **Monorepo**, contendo tanto o Backend (API) quanto o Frontend no mesmo repositório, com banco de dados em nuvem para facilitar a colaboração da equipe.

## ✨ Funcionalidades

### 🔐 Autenticação e Perfis
- **Múltiplos Papéis:** Sistema de login com diferenciação entre `Admin`, `Dentista` e `Paciente`.
- **Cadastro Seguro:** Dados sensíveis protegidos e senhas criptografadas.

### 📅 Gestão de Agenda (Core)
- **Visualização de Horários:** O paciente vê apenas os horários livres (confirmação visual).
- **Bloqueio Automático:** O sistema impede agendamentos duplicados no mesmo horário (Constraint `unique_together` no banco).
- **Procedimentos:** Registro específico do procedimento a ser realizado em cada consulta (ex: Limpeza, Extração).
- **Histórico:** Logs de data de criação para auditoria.

### ⚙️ Regras de Negócio e Qualidade (QA)
- Validação de datas (impedir agendamento no passado).
- Cancelamento e reagendamento de consultas.
- Cadastro de especialidades odontológicas e validação de registro profissional (CRO).
- **Testes Automatizados:** Suíte de testes (Modelos e Views) configurada para rodar em banco SQLite isolado, garantindo confiabilidade sem afetar a produção.

---

## 🛠 Tecnologias Utilizadas

### Backend (API)
- **Linguagem:** Python 3.13
- **Framework:** Django & Django REST Framework (DRF)
- **Banco de Dados:** PostgreSQL 18 (Via Neon Tech - Serverless)
- **Banco de Dados (Testes):** SQLite (In-memory)
- **Libs Principais:** `python-decouple`, `dj-database-url`, `django-cors-headers`

### Frontend (Interface)
- **Framework:** React.js (Vite)
- **Linguagem:** TypeScript
- **Estilização:** CSS Modules / Standard CSS

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* Python 3.13+ instalado.
* Node.js 20+ (LTS).
* Conta no [Neon.tech](https://neon.tech) (para pegar a string de conexão).

### 1️⃣ Configurando o Backend (Django)

1.  Entre na pasta do backend:
    ```bash
    cd back
    ```
2.  Crie e ative o ambiente virtual:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure as variáveis de ambiente:
    * Crie um arquivo `.env` na pasta `back/` e cole a URL do banco Neon (peça para qualquer um da equipe):
    ```ini
    SECRET_KEY=sua_chave_secreta_aqui
    DEBUG=True
    DATABASE_URL=postgres://user:password@ep-xyz.aws.neon.tech/clinica-db?sslmode=require (Exemplo do Link)
    ```
5.  Execute as migrações (Isso cria as tabelas no Neon):
    ```bash
    python manage.py migrate
    ```
6.  Crie seu usuário administrador:
    ```bash
    python manage.py createsuperuser
    ```
7.  Rode o servidor:
    ```bash
    python manage.py runserver
    ```
    *Acesse o painel em: `http://127.0.0.1:8000/admin`*

Para rodar os testes automatizados da API, utilize o comando  ```bash python manage.py test ```

### 2️⃣ Configurando o Frontend (React)

1.  Abra um novo terminal e entre na pasta do frontend:
    ```bash
    cd front/frontend
    ```
2.  Instale as dependências:
    ```bash
    npm install
    ```
3.  Rode o projeto:
    ```bash
    npm run dev
    ```
    *O Frontend estará rodando geralmente em: `http://localhost:5173/`*

---

## 📝 Licença

Este projeto está sob a licença MIT.

## 🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 👨‍💻 Autores

O desenvolvimento está dividido em duas frentes principais:

* **Backend (API e Banco de Dados):** Desenvolvido por Enio Jr.
* **Frontend (Web):** Desenvolvido por Daivid Gabriel.

Entre em contato com Enio Jr. para dúvidas, sugestões ou colaborações futuras: <br>
📧 E-mail: eniojr100@gmail.com <br>
🔗 LinkedIn: https://www.linkedin.com/in/enioeduardojr <br>
📷 Instagram: https://www.instagram.com/enio_juniorrr <br>

Entre em contato com David Gabriel para dúvidas, sugestões ou colaborações futuras: <br>
📧 E-mail: davidglm.trabalho@gmail.com <br>
🔗 LinkedIn: https://www.linkedin.com/in/davidgabriellm <br>
📷 Instagram: https://www.instagram.com/davinho_glm <br>