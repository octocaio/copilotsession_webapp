# Guia Completo: Armazenamento no GitHub Actions

## Respondendo Suas Dúvidas sobre Consumo de Armazenamento

### 1. Artifacts e Cache realmente consomem da cota?

**Sim, ambos consomem!** Mas de formas diferentes:

#### Artifacts (Artefatos)
- São arquivos gerados durante workflows (relatórios, builds, logs)
- Contam diretamente na sua cota de armazenamento
- Ficam disponíveis por um período configurável (padrão: 90 dias)
- **Exemplo**: Se você publicar 500MB de relatórios por dia, em um mês terá ~15GB só de artifacts

#### Cache
- Usado para acelerar workflows (dependências npm, maven, etc)
- Também consome da mesma cota de armazenamento
- Limitado a 10GB por repositório (após isso, o mais antigo é deletado automaticamente)
- **Exemplo**: Cache de node_modules pode facilmente ocupar 2-3GB

### 2. Como verificar o consumo real em GB?

Existem várias maneiras de verificar:

#### Opção A: Via Interface Web do GitHub

**Para Artifacts:**
```
1. Acesse: https://github.com/[ORGANIZAÇÃO]/settings/billing/actions
2. Na seção "Storage for Actions and Packages"
3. Você verá o total usado em GB
```

**Para verificar por repositório:**
```
1. Vá até: Settings > Actions > General (do repositório)
2. Role até a seção "Artifact and log retention"
3. Use a API para detalhes (veja abaixo)
```

#### Opção B: Via GitHub API (Recomendado para análise detalhada)

**Consumo da Organização:**
```bash
curl -H "Authorization: token SEU_TOKEN" \
  https://api.github.com/orgs/SUA_ORG/settings/billing/actions
```

Retorna algo como:
```json
{
  "total_minutes_used": 5000,
  "total_paid_minutes_used": 2000,
  "included_minutes": 3000,
  "minutes_used_breakdown": {...},
  "storage_gb": 15.7
}
```

**Para listar Artifacts de um repositório:**
```bash
curl -H "Authorization: token SEU_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/artifacts?per_page=100"
```

#### Opção C: Script Python para Análise Completa

Crie um arquivo `analise_storage.py`:

```python
import requests
import json
from datetime import datetime

def obter_consumo_storage(org_name, token):
    """
    Analisa consumo de armazenamento da organização
    Retorna detalhes em GB e custos estimados
    """
    cabecalhos = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    
    # Buscar informações de billing
    endpoint = f'https://api.github.com/orgs/{org_name}/settings/billing/actions'
    resposta = requests.get(endpoint, headers=cabecalhos)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        storage_total = dados.get('storage_gb', 0)
        
        print(f"\n{'='*50}")
        print(f"Análise de Armazenamento - {org_name}")
        print(f"{'='*50}")
        print(f"Storage Total Usado: {storage_total} GB")
        print(f"Data da Consulta: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        return storage_total
    else:
        print(f"Erro ao consultar: {resposta.status_code}")
        return None

def listar_artifacts_grandes(owner, repo, token, tamanho_minimo_mb=50):
    """
    Lista artifacts que estão ocupando muito espaço
    """
    cabecalhos = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    
    endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/artifacts'
    resposta = requests.get(endpoint, headers=cabecalhos, params={'per_page': 100})
    
    if resposta.status_code == 200:
        artifacts = resposta.json()['artifacts']
        
        print(f"\n{'='*50}")
        print(f"Artifacts Grandes (>{tamanho_minimo_mb}MB)")
        print(f"{'='*50}")
        
        total_size_bytes = 0
        for artifact in artifacts:
            size_mb = artifact['size_in_bytes'] / (1024 * 1024)
            if size_mb >= tamanho_minimo_mb:
                print(f"\n📦 {artifact['name']}")
                print(f"   Tamanho: {size_mb:.2f} MB")
                print(f"   Criado: {artifact['created_at'][:10]}")
                print(f"   Expira: {artifact['expires_at'][:10]}")
            
            total_size_bytes += artifact['size_in_bytes']
        
        total_gb = total_size_bytes / (1024 * 1024 * 1024)
        print(f"\nTotal de Artifacts neste repo: {total_gb:.2f} GB")
        
    else:
        print(f"Erro ao listar artifacts: {resposta.status_code}")

# Exemplo de uso:
# obter_consumo_storage('minha-org', 'ghp_seu_token_aqui')
# listar_artifacts_grandes('minha-org', 'meu-repo', 'ghp_seu_token_aqui')
```

### 3. Como funciona a cobrança pelo excedente?

#### Estrutura de Cobrança

**Para contas GitHub Team:**
- ✅ 2 GB de storage incluído gratuitamente
- 💰 $0.008 USD por GB/dia adicional (aproximadamente $0.25 por GB/mês)

**Para contas GitHub Enterprise:**
- ✅ 50 GB de storage incluído gratuitamente  
- 💰 $0.008 USD por GB/dia adicional

#### Calculando seu custo mensal

Fórmula simples:
```
Custo Mensal = (Storage Usado - Storage Incluído) × $0.25
```

**Exemplos práticos:**

| Storage Usado | Plano | Storage Incluído | Excedente | Custo/Mês |
|---------------|-------|------------------|-----------|-----------|
| 5 GB          | Team  | 2 GB             | 3 GB      | ~$0.75    |
| 15 GB         | Team  | 2 GB             | 13 GB     | ~$3.25    |
| 100 GB        | Enterprise | 50 GB       | 50 GB     | ~$12.50   |

#### Como é cobrado?

1. **Cálculo diário**: GitHub calcula o GB usado por dia
2. **Proporcional**: Se você deletar artifacts no meio do mês, paga apenas pelos dias que ficaram armazenados
3. **Faturamento mensal**: Aparece na sua fatura mensal do GitHub

### 4. Ações Práticas para Reduzir Consumo

#### A. Reduzir tempo de retenção de Artifacts

No seu workflow, adicione:
```yaml
- name: Upload relatorio
  uses: actions/upload-artifact@v4
  with:
    name: relatorio-testes
    path: ./reports
    retention-days: 7  # Em vez dos 90 dias padrão
```

Ou configure globalmente no repositório:
```
Settings > Actions > General > Artifact and log retention
Altere de 90 para 7 ou 14 dias
```

#### B. Deletar Artifacts antigos via API

```bash
# Listar artifacts
gh api repos/OWNER/REPO/actions/artifacts --jq '.artifacts[] | "\(.id) \(.name)"'

# Deletar artifact específico
gh api -X DELETE repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID
```

#### C. Usar Cache de forma inteligente

```yaml
- name: Cache dependencias
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: npm-
```

**Dica importante**: Cache tem limite de 10GB por repo e auto-remove o mais antigo. Artifacts não têm esse limite!

#### D. Script de Limpeza Automática

Crie um workflow que roda semanalmente:

```yaml
name: Limpar Artifacts Antigos
on:
  schedule:
    - cron: '0 2 * * 0'  # Todo domingo às 2h
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Deletar artifacts com mais de 30 dias
        uses: actions/github-script@v7
        with:
          script: |
            const diasRetencao = 30;
            const milissegundosRetencao = diasRetencao * 24 * 60 * 60 * 1000;
            const agora = Date.now();
            
            const artifacts = await github.rest.actions.listArtifactsForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              per_page: 100
            });
            
            let deletados = 0;
            for (const artifact of artifacts.data.artifacts) {
              const dataExpiracao = new Date(artifact.created_at).getTime();
              const idade = agora - dataExpiracao;
              
              if (idade > milissegundosRetencao) {
                await github.rest.actions.deleteArtifact({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  artifact_id: artifact.id
                });
                console.log(`✓ Deletado: ${artifact.name} (${artifact.size_in_bytes} bytes)`);
                deletados++;
              }
            }
            
            console.log(`\nTotal deletado: ${deletados} artifacts`);
```

### 5. Monitoramento Contínuo

Crie alertas para monitorar seu consumo:

#### Dashboard Simples

```bash
#!/bin/bash
# salve como: check_storage.sh

ORG="sua-org"
TOKEN="seu-token"

echo "Consultando consumo de storage..."

curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/orgs/$ORG/settings/billing/actions" | \
  jq -r '"Storage usado: \(.storage_gb) GB"'

# Adicione no crontab para rodar diariamente:
# 0 9 * * * /caminho/check_storage.sh | mail -s "Storage GitHub Actions" seu@email.com
```

### 6. Checklist de Otimização

- [ ] Verificar consumo atual via API ou interface web
- [ ] Reduzir retention-days de artifacts para 7-14 dias
- [ ] Configurar workflow de limpeza automática
- [ ] Revisar quais artifacts são realmente necessários
- [ ] Documentar os artifacts essenciais vs descartáveis
- [ ] Considerar alternativas: S3, Azure Blob, etc para armazenamento de longo prazo
- [ ] Monitorar consumo mensalmente

### 7. Recursos Adicionais

- **Documentação Oficial**: https://docs.github.com/billing/managing-billing-for-github-actions
- **API Reference**: https://docs.github.com/rest/actions/artifacts
- **GitHub CLI**: https://cli.github.com/manual/gh_api

---

**💡 Dica Final**: Se você precisa manter relatórios por muito tempo (>30 dias), considere fazer upload para um storage externo (S3, Azure Blob) no próprio workflow. Assim você mantém histórico sem pagar pelo storage do GitHub Actions.

---

**Criado em**: Fevereiro 2026  
**Última atualização**: {{ data_atual }}
