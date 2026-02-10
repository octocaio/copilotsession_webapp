# Arquitetura do Migrador GitLab → GitHub

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    MIGRADOR GitLab → GitHub                  │
│                                                               │
│  ┌────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Config   │───▶│   Migrator   │───▶│   GitHub     │    │
│  │   JSON     │    │    Class     │    │   Issues     │    │
│  └────────────┘    └──────────────┘    └──────────────┘    │
│                            │                                 │
│                            ▼                                 │
│                    ┌──────────────┐                         │
│                    │   GitLab     │                         │
│                    │   API        │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Migração

### Fluxo Principal

```
1. CONFIGURAÇÃO
   ├─ Carregar config.json
   ├─ Validar credenciais
   └─ Inicializar GitLabToGitHubMigrator

2. BUSCAR MRs DO GITLAB
   ├─ Conectar à API GitLab
   ├─ Buscar MRs (paginado)
   ├─ Filtrar por estado (opened/closed/merged/all)
   └─ Retornar lista de MRs

3. PROCESSAR CADA MR
   ├─ Buscar metadados do MR
   ├─ Buscar discussões/comentários
   ├─ Mapear usuários (GitLab → GitHub)
   ├─ Formatar corpo da Issue
   └─ Preparar labels

4. CRIAR ISSUE NO GITHUB
   ├─ Conectar à API GitHub
   ├─ Criar Issue com conteúdo formatado
   ├─ Aplicar labels automáticas
   ├─ Rate limiting (delay entre requests)
   └─ Registrar resultado

5. RELATÓRIO
   ├─ Total processado
   ├─ Sucesso
   ├─ Falhas
   └─ Pulados
```

### Fluxo de Dados Detalhado

```
GitLab MR                         GitHub Issue
───────────                       ─────────────

!123                             ──▶ [GitLab MR !123] Título
Título                           ──▶ Título (no corpo)
Descrição                        ──▶ ### Description
Autor (@gitlab_user)             ──▶ @github_user (mapeado)
Estado (opened/closed/merged)    ──▶ Labels (was-open/was-closed/was-merged)
Branches (source/target)         ──▶ Metadados no corpo
Comentários/Discussões           ──▶ ### Discussion History
Labels originais                 ──▶ Mencionados no corpo
Data criação/atualização         ──▶ Metadados no corpo
URL do MR                        ──▶ Link no corpo
```

## 🏗️ Componentes do Sistema

### 1. Classe GitLabToGitHubMigrator

```python
GitLabToGitHubMigrator
│
├── __init__(config)              # Inicialização com config
├── get_gitlab_headers()          # Headers para API GitLab
├── get_github_headers()          # Headers para API GitHub
├── fetch_gitlab_merge_requests() # Buscar MRs (paginado)
├── fetch_mr_discussions()        # Buscar comentários de um MR
├── map_user()                    # Mapear usuário GitLab → GitHub
├── format_issue_body()           # Formatar corpo da Issue
├── create_github_issue()         # Criar Issue no GitHub
└── migrate()                     # Executar migração completa
```

### 2. Configuração (config.json)

```json
{
  "gitlab": {
    "url": "https://gitlab.com",
    "token": "...",
    "project_id": "..."
  },
  "github": {
    "api_url": "https://api.github.com",
    "token": "...",
    "owner": "...",
    "repo": "..."
  },
  "user_mapping": {...},
  "dry_run": false,
  "rate_limit_delay": 1
}
```

### 3. Scripts Auxiliares

- **gitlab_to_github.py** - Script principal
- **migrate.sh** - Interface interativa
- **test_migrator.py** - Testes de validação

## 🔌 Integrações de API

### GitLab API

**Endpoints Utilizados:**

1. **Listar MRs**
   ```
   GET /api/v4/projects/{id}/merge_requests
   Params: state, per_page, page, order_by, sort
   ```

2. **Buscar Comentários**
   ```
   GET /api/v4/projects/{id}/merge_requests/{mr_iid}/notes
   ```

**Headers:**
```
PRIVATE-TOKEN: {gitlab_token}
Content-Type: application/json
```

### GitHub API

**Endpoints Utilizados:**

1. **Criar Issue**
   ```
   POST /repos/{owner}/{repo}/issues
   Body: { title, body, labels }
   ```

**Headers:**
```
Authorization: token {github_token}
Accept: application/vnd.github.v3+json
```

## 📊 Modelo de Dados

### MR do GitLab (Input)

```json
{
  "iid": 123,
  "title": "Feature: Nova funcionalidade",
  "description": "Descrição detalhada...",
  "state": "opened",
  "author": {
    "username": "gitlab_user"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-02T15:30:00Z",
  "source_branch": "feature-branch",
  "target_branch": "main",
  "labels": ["enhancement", "priority-high"],
  "web_url": "https://gitlab.com/.../merge_requests/123",
  "merged_at": null,
  "merged_by": null
}
```

### Issue do GitHub (Output)

```json
{
  "title": "[GitLab MR !123] Feature: Nova funcionalidade",
  "body": "## 📋 Legacy Merge Request...",
  "labels": [
    "legacy-mr",
    "from-gitlab",
    "was-open"
  ]
}
```

## 🎯 Decisões de Design

### Por que Issues e não PRs?

1. **Governança** - Issues não executam CI/CD
2. **Simplicidade** - Modelo mais adequado para histórico
3. **Flexibilidade** - Times podem recriar PRs quando necessário
4. **Clareza** - Separação clara entre histórico e trabalho ativo

### Por que não migrar Pipelines?

1. **Requisito explícito** - Cliente pediu apenas histórico
2. **Complexidade** - Pipelines GitLab ≠ GitHub Actions
3. **Temporário** - Pipelines são efêmeros, histórico não
4. **Prático** - Novo fluxo CI/CD será criado no GitHub

### Rate Limiting

- **Delay configurável** entre requests (padrão: 1s)
- **Paginação** para lidar com grandes volumes
- **Retry logic** pode ser adicionado no futuro

### User Mapping

- **Opcional** - Usa username GitLab se não mapeado
- **Configurável** - Via config.json
- **Flexível** - Pode ser expandido para buscar via API

## 🔒 Segurança

### Proteção de Credenciais

- ✅ Config.json no `.gitignore`
- ✅ Tokens nunca em código
- ✅ Template sem credenciais
- ✅ Validação de permissões

### Validação de Input

- ✅ Validação de JSON
- ✅ Campos obrigatórios
- ✅ Tratamento de erros de API
- ✅ Sanitização de conteúdo

## 📈 Escalabilidade

### Para Grandes Volumes

1. **Paginação** - Suporta qualquer número de MRs
2. **Batching** - Pode processar em lotes com `--max`
3. **Resumable** - Pode ser executado múltiplas vezes
4. **Monitoring** - Logs detalhados de progresso

### Otimizações Futuras

- [ ] Processamento paralelo
- [ ] Cache de usuários mapeados
- [ ] Retry automático em falhas
- [ ] Checkpoint/resume automático
- [ ] Bulk API operations

## 🧪 Testabilidade

### Testes Incluídos

1. **Config Loading** - Validação de configuração
2. **Migrator Class** - Instanciação correta
3. **User Mapping** - Mapeamento funcional
4. **Issue Formatting** - Formatação correta

### Dry Run Mode

- Simula migração sem criar Issues
- Valida configuração e conectividade
- Testa formatação e lógica
- Reporta estatísticas

## 🔄 Manutenção

### Atualizações de API

- APIs versionadas (GitLab v4, GitHub v3)
- Headers configuráveis
- URLs configuráveis
- Fácil adaptação a mudanças

### Extensibilidade

O código é estruturado para facilitar:
- Adição de novos campos
- Customização de formatação
- Novos modos de migração
- Integração com outras ferramentas

## 📝 Logs e Monitoramento

### Formato de Logs

```
📥 Fetching opened merge requests from GitLab...
  Fetched page 1 (100 MRs)
  Fetched page 2 (45 MRs)
✅ Total MRs fetched: 145

📦 Starting migration of 145 merge request(s)...

[1/145] 📝 Processing MR !123: Feature: Nova funcionalidade
  ✅ Created GitHub issue #456

[2/145] 📝 Processing MR !124: Fix: Correção de bug
  ✅ Created GitHub issue #457

...

📊 Migration Summary
Total MRs processed: 145
Successfully migrated: 143
Failed: 2
Skipped: 0
```

### Tratamento de Erros

- Erros de API são logados com detalhes
- Migração continua mesmo com falhas individuais
- Estatísticas finais mostram taxa de sucesso
- Dry-run permite validação prévia

## 🎓 Boas Práticas Implementadas

1. ✅ **Single Responsibility** - Cada método tem uma função clara
2. ✅ **Configuration over Code** - Tudo configurável via JSON
3. ✅ **Fail-safe** - Dry-run, validação, tratamento de erros
4. ✅ **Auditability** - Logs detalhados, links preservados
5. ✅ **Documentação** - README, QUICK_START, ARCHITECTURE
6. ✅ **Testing** - Testes de validação automatizados
7. ✅ **Security** - Proteção de credenciais, sanitização
8. ✅ **Usability** - CLI intuitivo, script interativo

---

**Versão:** 1.0  
**Data:** 2024  
**Autor:** GitHub Copilot  
**Propósito:** Documentação técnica do migrador GitLab → GitHub
