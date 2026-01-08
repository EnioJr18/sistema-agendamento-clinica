# 🏥 Sistema de Agendamento Clínico

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![React](https://img.shields.io/badge/React-18-blue)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791)

> Um sistema completo para gestão de consultas médicas, focado em resolução de conflitos de horário, múltiplos perfis de usuário e validação robusta de dados.

---

## 📋 Sobre o Projeto

Este projeto é uma solução Fullstack para clínicas, consultórios ou profissionais autônomos (psicólogos, barbeiros, personal trainers). O objetivo principal é automatizar o processo de agendamento, garantindo que não haja conflitos de horário e fornecendo interfaces específicas para médicos e pacientes.

O sistema utiliza uma arquitetura **Monorepo**, contendo tanto o Backend (API) quanto o Frontend no mesmo repositório.

## ✨ Funcionalidades

### 🔐 Autenticação e Perfis
- **Múltiplos Papéis:** Sistema de login com diferenciação entre `Admin`, `Médico` e `Paciente`.
- **Cadastro Seguro:** Dados sensíveis protegidos e senhas criptografadas.

### 📅 Gestão de Agenda (Core)
- **Visualização de Horários:** O paciente vê apenas os horários livres (confirmação visual).
- **Bloqueio Automático:** O sistema impede agendamentos duplicados no mesmo horário (Constraint `unique_together` no banco).
- **Histórico:** Logs de data de criação (`criado_em`) para auditoria.

### ⚙️ Regras de Negócio
- Validação de datas (impedir agendamento no passado).
- Cancelamento e reagendamento de consultas.
- Cadastro de especialidades médicas e CRM.

---

## 🛠 Tecnologias Utilizadas

### Backend (API)
- **Linguagem:** Python 3
- **Framework:** Django & Django REST Framework (DRF)
- **Banco de Dados:** PostgreSQL
- **Segurança:** Python Decouple (Variáveis de ambiente) & CORS Headers

### Frontend (Interface)
- **Framework:** React.js (Vite)
- **Linguagem:** TypeScript
- **Estilização:** CSS Modules / Standard CSS

---

## 📂 Estrutura do Projeto

```text
projeto-clinica/
├── back/                 # Backend Django
│   ├── api/              # App principal (Models, Views, Serializers)
│   ├── core/             # Configurações do projeto (Settings, URLs)
│   ├── requirements.txt  # Dependências do Python
│   └── manage.py
│
├── front/frontend/       # Frontend React + Vite
│   ├── src/              # Código fonte React
│   ├── public/           # Assets estáticos
│   └── package.json      # Dependências do Node
│
└── README.md             # Documentação