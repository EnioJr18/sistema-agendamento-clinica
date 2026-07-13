# Backend da Clinica Odontologica

API Django REST Framework para gestao odontologica multi-clinica.

## Contrato oficial

A API publica do produto esta versionada em `/api/v1/`.

Termos oficiais do dominio:

- `dentista`
- `cro`
- `nome_dentista`
- `/api/v1/dentistas/`

Nao fazem parte do contrato novo: `medico`, `crm`, `nome_medico` e `/medicos/`.

## Autenticacao

JWT:

- `POST /api/token/`
- `POST /api/token/refresh/`

Use o token de acesso no header:

```http
Authorization: Bearer <access_token>
```

## Endpoints principais

- `/api/v1/clinicas/`
- `/api/v1/usuarios/`
- `/api/v1/dentistas/`
- `/api/v1/procedimentos/`
- `/api/v1/agendamentos/`

Usuarios comuns acessam apenas dados da propria clinica. Staff/admin pode administrar globalmente nesta etapa.

## Agenda

Status oficiais de agendamento:

- `AGENDADA`
- `CONFIRMADA`
- `EM_ATENDIMENTO`
- `CONCLUIDA`
- `CANCELADA`
- `NAO_COMPARECEU`

Agendamentos nao devem ser alterados por `PATCH` ou `PUT` generico. Use as acoes explicitas:

- `POST /api/v1/agendamentos/{id}/cancelar/`
- `POST /api/v1/agendamentos/{id}/reagendar/`
- `POST /api/v1/agendamentos/{id}/confirmar/`
- `POST /api/v1/agendamentos/{id}/concluir/`
- `POST /api/v1/agendamentos/{id}/marcar-falta/`

Conflitos de horario e sobreposicoes retornam `409 Conflict`.

## Paginacao

Listagens usam a paginacao padrao do DRF:

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

## Documentacao OpenAPI

- `/api/schema/`
- `/api/docs/`
- `/api/redoc/`

## Desenvolvimento

Variaveis principais:

- `ENVIRONMENT`: `development`, `test` ou `production`
- `SECRET_KEY`: obrigatoria em producao
- `DEBUG`: `True` ou `False`
- `DATABASE_URL`: URL do banco; se ausente fora de producao, usa SQLite local
- `USE_SQLITE_FOR_TESTS`: `True` para testes locais em SQLite; `False` para usar `DATABASE_URL`
- `ALLOWED_HOSTS`: lista separada por virgula
- `CORS_ALLOWED_ORIGINS`: lista separada por virgula

Copie `.env.example` para `.env` no desenvolvimento local e ajuste os valores.

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Rode migrations e servidor:

```powershell
python manage.py migrate
python manage.py runserver
```

Rode testes:

```powershell
python manage.py test api
```

Lint:

```powershell
ruff check .
```

Coverage:

```powershell
coverage run manage.py test api
coverage report
```

## Docker

O compose de desenvolvimento fica em `back/docker-compose.yml` e sobe Django + PostgreSQL:

```powershell
docker compose up --build
```

O backend fica em `http://localhost:8000`.

Testes usando PostgreSQL via Docker:

```powershell
docker compose run --rm -e USE_SQLITE_FOR_TESTS=False backend python manage.py test api
```

## Health check

- `/api/health/`

Retorna apenas estado basico da aplicacao e do banco, sem expor segredos.

## CI

O workflow `Backend CI` roda em push e pull request para mudancas do backend. Ele instala dependencias, sobe PostgreSQL, roda lint, verifica migrations, executa migrations, testes e coverage. Nao ha deploy configurado nesta sprint.
