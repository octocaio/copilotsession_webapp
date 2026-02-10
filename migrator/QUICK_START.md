# Guia Rápido de Início - Migrador GitLab → GitHub

Este guia te ajuda a começar em **5 minutos**.

## 🚀 Início Rápido

### 1. Instalar Dependências (30 segundos)

```bash
cd migrator
pip install -r requirements.txt
```

### 2. Configurar Credenciais (2 minutos)

```bash
# Copiar template
cp config.template.json config.json

# Editar com suas credenciais
nano config.json  # ou vim, code, etc.
```

**Mínimo necessário:**
- `gitlab.token` - Seu token GitLab (Settings → Access Tokens)
- `gitlab.project_id` - ID do projeto (na página do projeto no GitLab)
- `github.token` - Seu token GitHub (Settings → Developer settings → Tokens)
- `github.owner` - Sua organização ou usuário GitHub
- `github.repo` - Nome do repositório GitHub

### 3. Testar (30 segundos)

```bash
# Dry run com 3 MRs
python3 gitlab_to_github.py --config config.json --max 3 --dry-run
```

### 4. Migrar (1-2 minutos)

```bash
# Executar migração real dos primeiros 3 MRs
python3 gitlab_to_github.py --config config.json --max 3

# Se ok, migrar todos
python3 gitlab_to_github.py --config config.json
```

## 🎯 Ou Use o Script Interativo

```bash
./migrate.sh
```

Ele te guia pelo processo completo!

## ✅ Checklist Pré-Migração

- [ ] Backup do repositório GitLab feito
- [ ] Tokens GitLab e GitHub criados
- [ ] Repositório GitHub criado
- [ ] Labels criadas no GitHub: `legacy-mr`, `from-gitlab`
- [ ] Times comunicados sobre a migração
- [ ] Dry run executado e validado

## 📊 O que Esperar

Cada MR do GitLab vira:
- ✅ Uma Issue no GitHub
- ✅ Com título `[GitLab MR !123] Título original`
- ✅ Com todo o histórico e comentários
- ✅ Com labels automáticas
- ✅ Com link para o MR original

## 🆘 Problemas?

1. **"requests not found"** → `pip install requests`
2. **"401 Unauthorized"** → Verifique seus tokens
3. **"404 Not Found"** → Verifique project_id, owner, repo
4. **Rate limiting** → Aumente `rate_limit_delay` no config

## 📖 Documentação Completa

Veja `README.md` para documentação detalhada.

## 💡 Dica

Sempre comece com:
1. Dry run (`--dry-run`)
2. Poucos MRs (`--max 3`)
3. Validar resultado
4. Depois migrar tudo

---

**Tempo total estimado:** 5-10 minutos (primeira vez)
