# Migrador GitLab → GitHub

Ferramenta para migração de Merge Requests do GitLab para o GitHub, preservando histórico e contexto para fins de auditoria.

> 📚 **Navegação:** Este é o guia técnico completo. Para outros documentos, consulte [INDEX.md](INDEX.md)
> - 🚀 Início rápido? → [QUICK_START.md](QUICK_START.md)
> - 📊 Resumo executivo? → [ESTRATEGIA.md](ESTRATEGIA.md)
> - 🏗️ Arquitetura? → [ARCHITECTURE.md](ARCHITECTURE.md)

## 📋 Contexto e Estratégia de Migração

### Objetivo

Migrar Merge Requests (MRs) abertas do GitLab para o GitHub, **preservando apenas o histórico e contexto para auditoria**, sem necessidade de manter associações de pipelines ou fluxo ativo.

### Abordagem Recomendada pela GitHub

Existem algumas opções para tratar os Merge Requests abertos na migração GitLab → GitHub, sendo a abordagem mais recomendada pela GitHub migrar o código de forma limpa e preservar os MRs apenas como histórico (por exemplo, via Issues ou PRs fechados), evitando carregar fluxo ativo para o novo ambiente. Alternativamente, é possível recriar MRs de forma seletiva ou manter rastreabilidade sem continuidade operacional. Cada opção tem impactos diferentes em governança, CI/CD e automação, e por isso precisamos refinar o contexto com algumas perguntas antes de definir a estratégia final.

### Estratégia Implementada

Este migrador implementa a **melhor prática recomendada pela GitHub**:

1. ✅ **Código migra limpo** - Branches e commits são migrados separadamente
2. ✅ **MRs viram Issues no GitHub** - Preserva contexto sem carregar fluxo ativo
3. ✅ **Histórico completo preservado** - Descrição, comentários, discussões e metadados
4. ✅ **Rastreabilidade garantida** - Links para MRs originais no GitLab
5. ✅ **Sem migração de pipelines** - Conforme requisito, apenas histórico é preservado
6. ✅ **Automação via API** - Processo repetível e auditável

### Por que Issues e não PRs?

- **Governança**: Evita PRs "zumbis" que confundem o histórico ativo
- **Simplicidade**: Issues são mais adequadas para documentação histórica
- **Flexibilidade**: Times podem recriar PRs somente para o que ainda faz sentido
- **Clareza**: Separação clara entre histórico (Issues) e trabalho ativo (PRs novos)

## 🎯 Funcionalidades

- ✅ Migração automática de MRs do GitLab para Issues do GitHub
- ✅ Preservação de descrições, comentários e discussões
- ✅ Mapeamento de usuários GitLab → GitHub
- ✅ Labels automáticas para categorização (`legacy-mr`, `from-gitlab`, `was-open`, etc.)
- ✅ Links para MRs originais no GitLab
- ✅ Metadados completos (autor, datas, branches, status)
- ✅ Modo dry-run para testes
- ✅ Rate limiting configurável
- ✅ Suporte para diferentes estados de MR (abertos, fechados, merged, todos)

## 📦 Pré-requisitos

- Python 3.7+
- Acesso à API do GitLab (Personal Access Token)
- Acesso à API do GitHub (Personal Access Token)
- Permissões adequadas nos repositórios

### Tokens Necessários

#### GitLab Personal Access Token
Necessário com os seguintes scopes:
- `api` - Acesso completo à API
- `read_repository` - Leitura do repositório

**Como criar:**
1. GitLab → Settings → Access Tokens
2. Criar token com scopes acima
3. Guardar o token em local seguro

#### GitHub Personal Access Token
Necessário com os seguintes scopes:
- `repo` - Acesso completo a repositórios privados
- `public_repo` - Acesso a repositórios públicos (alternativa ao `repo`)

**Como criar:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Criar token com scopes acima
3. Guardar o token em local seguro

## 🚀 Instalação

### 1. Clone o repositório ou copie os arquivos

```bash
cd migrator
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou manualmente:

```bash
pip install requests
```

### 3. Configure o arquivo de configuração

Copie o template e preencha com suas credenciais:

```bash
cp config.template.json config.json
```

Edite `config.json`:

```json
{
  "gitlab": {
    "url": "https://gitlab.com",
    "token": "glpat-xxxxxxxxxxxx",
    "project_id": "12345"
  },
  "github": {
    "api_url": "https://api.github.com",
    "token": "ghp_xxxxxxxxxxxx",
    "owner": "sua-org-ou-usuario",
    "repo": "seu-repositorio"
  },
  "user_mapping": {
    "usuario_gitlab1": "usuario_github1",
    "usuario_gitlab2": "usuario_github2"
  },
  "dry_run": false,
  "rate_limit_delay": 1
}
```

#### Configurações Explicadas

- **gitlab.url**: URL da instância GitLab (geralmente `https://gitlab.com`)
- **gitlab.token**: Personal Access Token do GitLab
- **gitlab.project_id**: ID do projeto GitLab (encontrado na página do projeto)
- **github.api_url**: URL da API GitHub (geralmente `https://api.github.com`)
- **github.token**: Personal Access Token do GitHub
- **github.owner**: Nome da organização ou usuário do GitHub
- **github.repo**: Nome do repositório no GitHub
- **user_mapping**: Mapeamento de usuários GitLab → GitHub (opcional)
- **dry_run**: `true` para simular sem criar issues, `false` para executar
- **rate_limit_delay**: Delay em segundos entre requisições (recomendado: 1-2)

## 📖 Uso

### Migração Básica (MRs Abertos)

```bash
python gitlab_to_github.py --config config.json
```

### Migração com Dry Run (Teste)

Recomendado fazer primeiro para validar:

```bash
python gitlab_to_github.py --config config.json --dry-run
```

### Migrar MRs em Estados Específicos

```bash
# Apenas MRs abertos (padrão)
python gitlab_to_github.py --config config.json --state opened

# Apenas MRs fechados
python gitlab_to_github.py --config config.json --state closed

# Apenas MRs merged
python gitlab_to_github.py --config config.json --state merged

# Todos os MRs
python gitlab_to_github.py --config config.json --state all
```

### Limitar Número de MRs (para testes)

```bash
# Migrar apenas os primeiros 5 MRs
python gitlab_to_github.py --config config.json --max 5
```

### Exemplo Completo de Teste

```bash
# 1. Dry run com apenas 3 MRs abertos
python gitlab_to_github.py --config config.json --state opened --max 3 --dry-run

# 2. Se ok, executar migração real
python gitlab_to_github.py --config config.json --state opened --max 3

# 3. Verificar resultado no GitHub, depois migrar todos
python gitlab_to_github.py --config config.json --state opened
```

## 📊 Formato das Issues Criadas

Cada MR do GitLab vira uma Issue no GitHub com o seguinte formato:

### Título
```
[GitLab MR !123] Título original do MR
```

### Corpo

```markdown
## 📋 Legacy Merge Request (GitLab)

**Original MR:** https://gitlab.com/projeto/repo/-/merge_requests/123
**Author:** @usuario_github (GitLab: @usuario_gitlab)
**Status at migration:** opened
**Created:** 2023-01-15T10:30:00Z
**Last updated:** 2023-02-10T15:45:00Z
**Source branch:** `feature/nova-funcionalidade`
**Target branch:** `main`
**Original labels:** `enhancement`, `priority-high`

### Description

Descrição original do MR...

### Discussion History

_This MR had 5 comment(s) in GitLab:_

**@usuario1** (GitLab: @gitlab_user1) - 2023-01-16T09:00:00Z
> Comentário do usuário...

**@usuario2** (GitLab: @gitlab_user2) - 2023-01-17T14:30:00Z
> Resposta ao comentário...

---

_This issue was automatically created for historical and audit purposes._
_The original merge request remains available in GitLab for reference._
```

### Labels Automáticas

- `legacy-mr` - Identifica que é um MR migrado
- `from-gitlab` - Origem da migração
- `was-open` - MR estava aberto no momento da migração
- `was-merged` - MR foi merged no GitLab
- `was-closed` - MR foi fechado sem merge

## 🔄 Workflow Recomendado

### Preparação (Antes da Migração)

1. ✅ **Fazer backup** dos repositórios GitLab
2. ✅ **Comunicar aos times** sobre a migração
3. ✅ **Mapear usuários** GitLab → GitHub
4. ✅ **Criar labels** no GitHub (`legacy-mr`, `from-gitlab`)
5. ✅ **Testar com dry-run** e poucos MRs

### Execução

1. ✅ **Dry run completo** para validar
2. ✅ **Migração gradual** (começar com MRs fechados/merged)
3. ✅ **Validar resultados** intermediários
4. ✅ **Migrar MRs abertos** por último
5. ✅ **Documentar processo** e issues criadas

### Pós-Migração

1. ✅ **Validar Issues criadas** no GitHub
2. ✅ **Comunicar localização** do histórico aos times
3. ✅ **Marcar repositório GitLab** como read-only (opcional)
4. ✅ **Times avaliam** quais MRs recriar como PRs
5. ✅ **Fluxo ativo** continua 100% no GitHub

## ⚠️ Considerações Importantes

### O que É Migrado

- ✅ Título e descrição do MR
- ✅ Comentários e discussões
- ✅ Metadados (autor, datas, branches, status)
- ✅ Labels originais (como referência)
- ✅ Links para MRs originais no GitLab

### O que NÃO É Migrado

- ❌ Aprovações e reviewers
- ❌ Pipelines e CI/CD status
- ❌ Checks e testes
- ❌ Commits inline comments (apenas comentários gerais)
- ❌ Estado executável do MR (não vira PR ativo)

### Limitações Conhecidas

- **Rate Limiting**: APIs têm limites de requisições. O script inclui delay configurável.
- **Usuários não mapeados**: Usuários sem mapeamento aparecem com username GitLab.
- **Comentários inline**: Comentários em linhas específicas de código não são preservados exatamente.
- **Threads complexas**: Threads são linearizadas no formato de comentários.

## 🛠️ Troubleshooting

### Erro: "requests library not found"
```bash
pip install requests
```

### Erro: "401 Unauthorized" (GitLab)
- Verifique se o token GitLab está correto
- Confirme que o token tem scope `api`
- Teste: `curl -H "PRIVATE-TOKEN: seu_token" https://gitlab.com/api/v4/user`

### Erro: "401 Unauthorized" (GitHub)
- Verifique se o token GitHub está correto
- Confirme que o token tem scope `repo`
- Teste: `curl -H "Authorization: token seu_token" https://api.github.com/user`

### Erro: "404 Not Found" (GitLab)
- Verifique o `project_id` no GitLab
- Confirme que você tem acesso ao projeto

### Erro: "404 Not Found" (GitHub)
- Verifique `owner` e `repo` no GitHub
- Confirme que o repositório existe e você tem acesso

### Rate Limiting
Se encontrar erros de rate limiting:
1. Aumente `rate_limit_delay` no config
2. Pause a execução e aguarde
3. Use `--max` para migrar em lotes menores

## 📚 Referências

- [GitHub API - Issues](https://docs.github.com/en/rest/issues/issues)
- [GitLab API - Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html)
- [GitHub Migration Best Practices](https://docs.github.com/en/migrations)

## 🤝 Suporte

Para questões ou melhorias:
1. Consulte a documentação das APIs
2. Verifique os logs de erro detalhados
3. Teste com `--dry-run` primeiro
4. Use `--max` para validar com poucos MRs

## 📝 Licença

Este script é fornecido "como está" para fins de migração e auditoria.
