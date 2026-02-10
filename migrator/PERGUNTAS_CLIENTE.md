# Perguntas para Refinar a Migração GitLab → GitHub

## 📋 Contexto

Existem algumas opções para tratar os Merge Requests abertos na migração GitLab → GitHub, sendo a abordagem mais recomendada pela GitHub migrar o código de forma limpa e preservar os MRs apenas como histórico (por exemplo, via Issues ou PRs fechados), evitando carregar fluxo ativo para o novo ambiente. Alternativamente, é possível recriar MRs de forma seletiva ou manter rastreabilidade sem continuidade operacional. Cada opção tem impactos diferentes em governança, CI/CD e automação, e por isso precisamos refinar o contexto com algumas perguntas antes de definir a estratégia final.

## 🎯 Perguntas Estratégicas

### 1. Governança & Expectativa de Negócio

**Essas perguntas definem o que é "sucesso" para a migração:**

- [ ] O objetivo principal é **continuidade operacional** ou **preservação histórica**?
- [ ] Auditoria/compliance exige que MRs permaneçam **consultáveis** no novo ambiente?
- [ ] Existe alguma **exigência regulatória** para manter comentários, approvals ou timestamps?
- [ ] Alguém espera que os MRs abertos continuem **"ativos"** após a migração?
- [ ] O que é pior para o negócio:
  - **Perder histórico detalhado**, ou
  - **Carregar MRs antigos e possivelmente obsoletos**?

> **Nota:** Se a resposta for "continuidade total", isso é um red flag técnico.

### 2. Volume & Complexidade

**Aqui calibramos o quão agressivo podemos ser:**

- [ ] Quantos **repositórios** têm MRs abertos?
- [ ] Quantos **MRs abertos** no total?
- [ ] Distribuição dos MRs:
  - Quantos com **> 6 meses**?
  - Quantos com **> 12 meses**?
- [ ] Qual o **tamanho médio** das MRs? (small/medium/huge)
- [ ] Quantas MRs realmente fazem parte do **roadmap ativo** hoje?

> **Nota:** Normalmente, >50% dos MRs morre aqui quando olhamos os números.

### 3. Pessoas, Times e Ownership

**Sem isso, migração vira caos:**

- [ ] Cada MR tem um **owner ativo** hoje?
- [ ] Os **autores ainda estão na empresa**?
- [ ] Times atuais são os **mesmos da época** dos MRs?
- [ ] Há times que vão ser **descontinuados ou fundidos** durante a migração?
- [ ] **Quem decide** se uma MR ainda "vale a pena"?

> **Nota:** Se não tem owner → não deve virar PR ativo.

### 4. Pipeline, CI/CD e Qualidade

**Aqui mora um dos maiores riscos escondidos:**

- [ ] Os pipelines atuais estão **acoplados a MRs** do GitLab?
- [ ] Há **checks obrigatórios** para merge?
- [ ] Esses checks **existirão no GitHub** no dia 1?
- [ ] Algum MR depende de **runners, secrets ou variáveis** que não existirão inicialmente?
- [ ] Vocês aceitam que **PRs migrados não rodem CI** automaticamente?

> **Nota:** Se CI ≠ 1:1 → não migrar PR aberto.

### 5. Segurança & Compliance

**Esse bloco costuma matar opções "criativas":**

- [ ] Existem MRs com **dados sensíveis** em comentários?
- [ ] O histórico precisa respeitar **LGPD/GDPR**?
- [ ] Vocês precisam preservar **quem aprovou o quê**?
- [ ] Auditoria exige **imutabilidade** do histórico?
- [ ] Comentários inline são considerados **evidência formal**?

> **Nota:** Se "sim" → histórico sim, fluxo ativo não.

### 6. Automação & App de Migração

**Conectando com o app do cliente:**

- [ ] O app já migra **Issues e comentários** hoje?
- [ ] Ele suporta criação de **PRs fechados ou draft**?
- [ ] Consegue **mapear usuários** GitLab → GitHub?
- [ ] Consegue aplicar **labels, milestones e templates**?
- [ ] É aceitável **enriquecer o conteúdo** (ex: header "Legacy MR")?

> **Nota:** Quanto mais "sim", mais elegante fica a solução.

### 7. Estratégia de Cutover

**Sem isso, a discussão fica teórica:**

- [ ] Vai existir **freeze de código**? Por quanto tempo?
- [ ] MRs abertas após a data X entram onde?
- [ ] Quem **comunica** o fim do fluxo no GitLab?
- [ ] Haverá período de **convivência** (dual-write)?
- [ ] Qual é o **plano de rollback** se algo der errado?

## 🔑 Pergunta-Chave

**Use essa no meio da conversa:**

> "Se uma MR aberta hoje **nunca fosse migrada**, quem seria impactado amanhã?"

Silêncio depois dessa pergunta costuma ser revelador. 😄

## 📊 Matriz de Decisão

Com base nas respostas, podemos determinar a melhor abordagem:

### Cenário 1: Apenas Histórico/Auditoria ✅ (IMPLEMENTADO)

**Se:**
- Objetivo = preservação histórica
- MRs antigas (>6 meses)
- Poucos owners ativos
- CI/CD será reconstruído

**Então:**
- ✅ Migrar como **Issues** (solução atual)
- ✅ Preservar contexto completo
- ✅ Sem fluxo ativo
- ✅ Times recriam PRs conforme necessário

### Cenário 2: Rastreabilidade Forte

**Se:**
- Compliance rigoroso
- Auditoria exige histórico imutável
- Aprovações devem ser preservadas

**Então:**
- ✅ Migrar como **PRs fechados**
- ✅ Estado read-only
- ✅ Não mergeável
- ✅ Apenas referência

### Cenário 3: Migração Seletiva

**Se:**
- Poucos MRs (<50)
- Critérios claros (ex: com approval)
- Todos owners ativos

**Então:**
- ⚠️ Migrar seletivamente como **PRs ativos**
- ⚠️ Alto custo operacional
- ⚠️ Muitas exceções possíveis
- ⚠️ Pode virar dívida técnica

## 📝 Como Usar Este Documento

### Call 1 (30-45 min)
- Blocos 1, 2 e 7
- Definir escopo e expectativas

### Call 2 (Técnica)
- Blocos 4 e 6
- Validar viabilidade técnica

### Validação Final
- Blocos 3 e 5
- Confirmar estratégia e ownership

## ✅ Checklist de Decisão

Use este checklist para validar a estratégia escolhida:

- [ ] Objetivo claro definido (histórico vs. continuidade)
- [ ] Volume e distribuição dos MRs conhecidos
- [ ] Owners e responsáveis identificados
- [ ] Impacto em CI/CD avaliado
- [ ] Requisitos de compliance atendidos
- [ ] Capacidade do app de migração confirmada
- [ ] Plano de cutover documentado
- [ ] Comunicação aos times planejada
- [ ] Critérios de sucesso definidos
- [ ] Plano de rollback estabelecido

## 🎯 Próximos Passos

1. **Responder às perguntas** acima
2. **Validar cenário** aplicável
3. **Ajustar configuração** se necessário
4. **Executar dry-run** para validar
5. **Migrar em fases** conforme estratégia

---

**Documento preparado para:** Refinamento de estratégia de migração  
**Uso:** Discovery e planejamento de migração GitLab → GitHub  
**Atualizado:** 2024
