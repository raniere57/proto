# Plano de Recriação - Sistema de Protocolos (Django → FastAPI + Vue.js)

## Visão Geral

Sistema de gestão de protocolos de rede para a **Megalink Telecom**. Originalmente em Django, será refeito em **FastAPI (backend)** + **Vue.js 3 (frontend)**.

---

## Estrutura do Projeto

```
proto/
├── back/                          # FastAPI Backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Configurações (.env)
│   │   │   ├── database.py        # SQLAlchemy engine + session
│   │   │   ├── security.py        # JWT + bcrypt
│   │   │   └── dependencies.py    # Dependências (auth, grupos)
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── trecho.py          # Segmentos de rede
│   │   │   ├── servico.py         # Serviços (HubSoft)
│   │   │   ├── responsavel.py     # Técnicos responsáveis
│   │   │   ├── atendimento.py     # Tickets HubSoft
│   │   │   ├── mensagem.py        # Mensagens dos atendimentos
│   │   │   ├── protocolo.py       # Protocolo NOC TX/IP
│   │   │   ├── suporte_protocolo.py # Protocolo Suporte FTTH
│   │   │   ├── ordem_servico.py   # Ordens de serviço
│   │   │   ├── descricao_trecho.py # Descrições de trecho
│   │   │   └── usuario.py         # Usuários + Grupos (auth)
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── routers/               # FastAPI routers
│   │   │   ├── auth.py            # Login, me
│   │   │   ├── trechos.py         # CRUD trechos + JSON endpoint
│   │   │   ├── servicos.py        # Listagem serviços
│   │   │   ├── responsaveis.py    # Listagem responsáveis
│   │   │   ├── protocolos.py      # CRUD Protocolo + mensagens
│   │   │   ├── suporte.py         # CRUD Suporte FTTH
│   │   │   ├── dashboard.py       # Agregações e analytics
│   │   │   └── relacionar.py      # Vínculo NOC ↔ Suporte
│   │   ├── services/
│   │   │   └── hubsoft.py         # Integração HubSoft API
│   │   └── main.py                # App FastAPI + CORS
│   ├── alembic/                   # Migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
├── front/                         # Vue.js Frontend
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts          # Axios instance + interceptors
│   │   │   ├── auth.ts            # Login, getMe
│   │   │   ├── protocolos.ts      # Protocolos, trechos, servicos
│   │   │   ├── suporte.ts         # Suporte FTTH
│   │   │   └── dashboard.ts       # Dashboard + relacionar
│   │   ├── components/
│   │   │   └── layout/
│   │   │       └── AppLayout.vue  # Sidebar + header + content
│   │   ├── router/
│   │   │   └── index.ts           # Vue Router + guards
│   │   ├── stores/
│   │   │   └── auth.ts            # Pinia auth store
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript interfaces
│   │   └── views/
│   │       ├── auth/
│   │       │   └── LoginView.vue
│   │       ├── protocolos/
│   │       │   ├── HomeView.vue           # Listagem com filtros
│   │       │   ├── CriarProtocoloView.vue  # Formulário NOC
│   │       │   ├── DetalhesProtocoloView.vue # Detalhes + chat
│   │       │   ├── GestaoProtocolosView.vue  # Gestão com cores
│   │       │   └── RelacionarView.vue      # Vínculo NOC↔Suporte
│   │       ├── suporte/
│   │       │   ├── HomeSuporteView.vue     # Listagem suporte
│   │       │   ├── CriarSuporteView.vue    # Form FTTH
│   │       │   └── DetalhesSuporteView.vue # Detalhes suporte
│   │       └── dashboard/
│   │           └── DashboardView.vue       # Gráficos + analytics
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── repomix.xml                    # Código fonte original Django
└── plano.md                       # Este arquivo
```

---

## Mapeamento Django → FastAPI + Vue

### Models (9 tabelas no PostgreSQL)

| Django Model | SQLAlchemy Model | Tabela |
|---|---|---|
| `Trecho` | `models/trecho.py` | `protocolocd_trecho` |
| `Servico` | `models/servico.py` | `protocolocd_servico` |
| `Responsavel` | `models/responsavel.py` | `protocolocd_responsavel` |
| `Atendimento` | `models/atendimento.py` | `protocolocd_atendimento` |
| `Mensagem` | `models/mensagem.py` | `protocolocd_mensagem` |
| `Protocolo` | `models/protocolo.py` | `protocolocd_protocolo` |
| `SuporteProtocolo` | `models/suporte_protocolo.py` | `protocolocd_suporte_protocolo` |
| `OrdemServico` | `models/ordem_servico.py` | `protocolocd_ordem_servico` |
| `DescricaoTrecho` | `models/descricao_trecho.py` | `protocolocd_descricao_trecho` |
| `User + Group` | `models/usuario.py` | `auth_user` + `auth_group` |

### Rotas (Django URLs → FastAPI endpoints)

| Django | FastAPI | Função |
|---|---|---|
| `/` | `GET /protocolos/` | Home - listar protocolos |
| `/criar-protocolo/` | `POST /protocolos/` | Criar protocolo NOC |
| `/protocolo/<id>/` | `GET /protocolos/<id>` | Detalhes protocolo |
| `/trecho/<id>/json/` | `GET /trechos/<id>/json` | Auto-preenchimento trecho |
| `/gestao-de-protocolos/` | `GET /protocolos/` (filtrado) | Gestão com cores |
| `/criar-protocolo-suporte/` | `POST /suporte/` | Criar suporte FTTH |
| `/suporte/` | `GET /suporte/` | Home suporte |
| `/suporte/<id>/` | `GET /suporte/<id>` | Detalhes suporte |
| `/dashboard-protocolos-noctx/` | `GET /dashboard/noc` | Dashboard analytics |
| `/relacionar-protocolos/` | `POST /relacionar/vincular` | Vincular protocolos |
| `/admin/login/` | `POST /auth/login` | Autenticação JWT |
| Envio de mensagem | `POST /protocolos/<id>/mensagens` | Mensagens chat |

### Funcionalidades do Django Admin → Frontend

- **Admin Trecho** → CRUD via API + tela de listagem
- **Admin Serviço + Importar HubSoft** → Botão de importação + listagem
- **Admin Protocolo** → Gestão de protocolos com formulário
- **Admin Atendimento** → Visualização via chat nos detalhes
- **Admin Responsável** → CRUD via API
- **Admin OrdemServico** → Listagem

---

## Partes da Implementação

### ✅ Parte 1: Estrutura Base (CONCLUÍDA)
- Backend: FastAPI + SQLAlchemy + Alembic + JWT
- Frontend: Vue 3 + Vite + PrimeVue + Pinia + Router
- 9 modelos SQLAlchemy + schemas Pydantic + routers + services

### 🔲 Parte 2: Modelos e Migrations (PRONTO)
- Todos os 9 modelos criados em `back/app/models/`
- Alembic configurado em `back/alembic/`
- **Referência no repomix.xml**: linhas 11655-12308 (models.py original)

### 🔲 Parte 3: Autenticação (PRONTO)
- JWT implementado em `back/app/core/security.py`
- Dependências: `get_current_user`, `require_group`
- Endpoints: `/auth/login`, `/auth/me`
- Frontend: LoginView + auth store + router guard
- **Referência no repomix.xml**: middleware.py linha 11629, views.py função `is_suporte_cliente` linha 12385

### 🔲 Parte 4: API Protocolos NOC (PRONTO)
- CRUD em `back/app/routers/protocolos.py`
- Auto-preenchimento via trecho
- Geração de título automática
- Mensagens (chat)
- **Referência no repomix.xml**: views.py `criar_protocolo` linha 13015, `detalhes_protocolo` linha 12737, `gestao_protocolos` linha 12570
- **Template HTML**: `criar_protocolo_noctx_new.html` (linha 2188) → `CriarProtocoloView.vue`
- **Template HTML**: `detalhes_protocolo.html` → `DetalhesProtocoloView.vue`
- **Template HTML**: `gestao_protocolos.html` → `GestaoProtocolosView.vue`

### 🔲 Parte 5: API Suporte FTTH (PRONTO)
- CRUD em `back/app/routers/suporte.py`
- Multi-select: Slot/PON, Rotas, CTOs
- Geração automática de descrição
- **Referência no repomix.xml**: views.py `criar_protocolo_suporte` linha 12389
- **Template HTML**: `criar_protocolo_suporte.html` (linha 3316) → `CriarSuporteView.vue`

### 🔲 Parte 6: Integração HubSoft (PRONTO)
- Service em `back/app/services/hubsoft.py`
- OAuth2 token management
- `new_atendimento()` + `adicionar_mensagem()`
- **Referência no repomix.xml**: models.py funções `new_token()`, `new_atendimento()` linha 11662-11727, views.py replica linha 12530-12568

### 🔲 Parte 7: Dashboard (PRONTO)
- Endpoint em `back/app/routers/dashboard.py`
- Agregações: eventos, redes, estados, top trechos
- **Referência no repomix.xml**: views.py `dashboard_protocolos_noctx` linha 13246
- **Template HTML**: `dashboard_protocolos_noctx.html` (linha 4919) → `DashboardView.vue`

### 🔲 Parte 8: Frontend - Layout + Auth (PRONTO)
- AppLayout.vue com sidebar fixa
- LoginView com JWT
- router/index.ts com guards

### 🔲 Parte 9: Frontend - Protocolos NOC (PRONTO)
- HomeView - listagem com filtros e DataTable
- CriarProtocoloView - formulário completo com auto-fill
- DetalhesProtocoloView - detalhes + chat de mensagens
- GestaoProtocolosView - gestão com cores (verde/amarelo/vermelho)

### 🔲 Parte 10: Frontend - Suporte FTTH (PRONTO)
- HomeSuporteView - listagem
- CriarSuporteView - formulário com MultiSelect Slot/PON/Rota/CTO
- DetalhesSuporteView - detalhes com tabela técnica

### 🔲 Parte 11: Frontend - Dashboard (PRONTO)
- DashboardView com Chart.js (gráficos doughnut + pie)
- Cards de estatísticas
- Tabela top trechos

### 🔲 Parte 12: Relacionar + Finalização (PRONTO)
- RelacionarView - vincular/desvincular protocolos
- Endpoint `POST /relacionar/vincular`
- Endpoint `GET /relacionar/relacoes`

---

## Convenções de Código

### Backend
- **Python 3.12+**, tipagem estrita
- Rotas: verbos HTTP padronizados (GET, POST, PUT, DELETE)
- Schemas: Pydantic v2 com `from_attributes = True`
- Auth: JWT Bearer via `HTTPBearer`
- DB: SQLAlchemy 2.0 style (`session.query` ou `select()`)
- Erros: `HTTPException` com código e detail

### Frontend
- **Vue 3** Composition API + `<script setup>`
- **TypeScript** estrito
- **PrimeVue** para componentes UI
- **Pinia** para estado global
- **Axios** com interceptor de autenticação
- Rotas protegidas via `beforeEach` guard

---

## Principais Arquivos de Referência no repomix.xml

| Arquivo | Linha | O que contém |
|---|---|---|
| `settings.py` | 296 | Config Django (DB, apps, middleware) |
| `urls.py` (projeto) | 468 | Rotas principais |
| `models.py` | 11655 | Todos os 9 modelos + HubSoft API |
| `views.py` | 12361 | Todas as views (protocolo, suporte, dashboard, etc) |
| `forms.py` | 11549 | Forms (ProtocoloForm, SuporteProtocoloForm) |
| `admin.py` | 11296 | Admin + importação serviços |
| `middleware.py` | 11629 | Redirecionamento por grupo |
| `urls.py` (app) | 12316 | Rotas do app protocolocd |
| `criar_protocolo_noctx_new.html` | 2188 | Template principal do formulário NOC |
| `criar_protocolo_suporte.html` | 3316 | Template do formulário Suporte FTTH |
| `dashboard_protocolos_noctx.html` | 4919 | Template do Dashboard com Chart.js |
| `detalhes_protocolo.html` | (não incluso) | Detalhes + chat |
| `detalhes_protocolo_suporte.html` | 5923 | Detalhes suporte |
| `gestao_protocolos.html` | (não incluso) | Gestão com cores |
| `relacionar_protocolos.html` | (não incluso) | Vincular protocolos |
| `static/js/criar_protocolo.js` | 1752 | JS auto-preenchimento trecho |
| `static/protocolocd/js/select-filter.js` | 1827 | Select filtrável |
| `management/commands/import_servicos.py` | 519 | Script importação HubSoft |
| `management/commands/importar_trechos.py` | 660 | Script importação CSV trechos |
| `management/a.csv` | 752 | CSV de trechos (~300 registros) |

---

## Próximos Passos

Quando você aprovar o plano, podemos avançar para implementar cada parte seguindo a ordem acima, convertendo funcionalidade por funcionalidade do Django para FastAPI + Vue.js, consultando o `repomix.xml` para pegar lógicas de negócio, choices, validações, e templates.
