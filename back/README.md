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

Instale as dependencias do backend:

```powershell
pip install -r requirements.txt
```

Rode os testes:

```powershell
python manage.py test api
```
