# PRD — Sistema de Gestão de Acesso Wi-Fi com FreeRADIUS e Portal Cativo Próprio

---

# PARTE 1: VISÃO DE PRODUTO

## 1. Visão Geral

### Contexto e Problema

A organização utiliza atualmente pontos de acesso Sophos (APX/AP6) com portal cativo proprietário. Esse modelo limita:

* flexibilidade de gestão de acessos;
* personalização de regras;
* rastreabilidade operacional;
* autonomia da equipe de TI.

Além disso, o controle de visitantes e colaboradores não possui granularidade suficiente (expiração dinâmica, controle por dispositivo, auditoria detalhada).

### Solução Proposta

Desenvolver um sistema próprio composto por:

* **Portal cativo web (Django)** para autenticação de usuários;
* **Backoffice administrativo** para gestão de acessos;
* **Integração com FreeRADIUS**, utilizando MySQL como backend de autenticação;
* Controle por:

  * credenciais de colaborador;
  * vouchers com QR Code para visitantes;
  * vínculo por MAC address;
  * políticas de expiração.

### Stakeholders

* Equipe de TI (administração e operação)
* Usuários finais (colaboradores e visitantes)
* Infraestrutura de rede (Sophos AP + FreeRADIUS)
* Time técnico responsável por manutenção

---

## 2. Objetivos de Negócio

### Metas

* Substituir completamente o portal cativo Sophos
* Reduzir tempo de criação de acesso visitante em **>80%**
* Garantir rastreabilidade de acessos (100% auditável)
* Eliminar acessos não controlados por dispositivo

### Impacto Esperado

* Maior controle de rede
* Redução de suporte manual
* Melhoria de segurança e governança

---

## 3. Público-Alvo e Personas

### Usuários Finais

* Colaboradores internos
* Visitantes temporários

### Administradores

* Equipe de TI

### Equipe Técnica

* Desenvolvedores responsáveis pelo sistema
* Operadores de infraestrutura

---

# ✦ 4. User Experience & Interface

## 4.1 Visão de UX

* Interface funcional e orientada à produtividade
* Zero fricção após primeiro acesso (persistência via MAC)
* Separação clara de fluxos: colaborador vs visitante

## 4.2 Telas

| Tela                 | Propósito          | Acesso  | Interação       |
| -------------------- | ------------------ | ------- | --------------- |
| Login Admin          | Autenticação       | TI      | Formulário      |
| Dashboard            | Métricas           | TI      | Visualização    |
| Gestão Colaboradores | CRUD               | TI      | Formulário      |
| Gestão Vouchers      | Geração e controle | TI      | Formulário      |
| Sessões Ativas       | Monitoramento      | TI      | Tabela          |
| Relatórios           | Histórico          | TI      | Filtros         |
| Configurações        | Políticas          | TI      | Formulário      |
| Portal Colaborador   | Login              | Usuário | Formulário      |
| Portal Visitante     | Login via QR       | Usuário | Auto-preenchido |

## 4.3 Responsividade

* Desktop-first
* Compatível com mobile
* Sem PWA no MVP

## 4.4 Acessibilidade

* Sem requisito formal no MVP

## 4.5 Design System

* Layout neutro funcional

---

# 5. User Stories

## 5.1 Epics

| Epic | Título                 | Entrega          | Depende |
| ---- | ---------------------- | ---------------- | ------- |
| 1    | Autenticação Base      | Portal funcional | —       |
| 2    | Gestão Admin           | CRUD e vouchers  | 1       |
| 3    | Sessões e Controle     | MAC + sessões    | 2       |
| 4    | Auditoria e Relatórios | Logs e histórico | 3       |

---

## Epic 1 — Autenticação Base

**Goal:** Permitir autenticação funcional via portal

### Story 1.1 — Login colaborador

*Como colaborador, quero autenticar com usuário e senha*

**Acceptance Criteria:**

1. Login retorna sucesso em até 3s p95
2. Valida credenciais via FreeRADIUS
3. Se inválido, exibe erro
4. Após sucesso, registra MAC
5. Persistência no banco
6. Feedback visual de sucesso

### Story 1.2 — Login visitante com voucher

*Como visitante, quero acessar usando voucher com QR Code*

**Acceptance Criteria:**

1. Leitura de QR Code preenche campos automaticamente
2. Valida voucher no FreeRADIUS
3. Exibe mensagem clara de sucesso/erro/expirado
4. Registra MAC e data de uso
5. Impede reuso em outro dispositivo
6. Feedback visual

---

## Epic 2 — Gestão Admin

**Goal:** Permitir gestão completa de acessos

### Story 2.1 — Criar colaborador

*Como admin, quero criar usuários*

**Acceptance Criteria:**

1. CRUD completo
2. Validação de campos
3. Persistência MySQL
4. Auditoria registrada
5. Feedback visual
6. Permissão restrita a admin

### Story 2.2 — Gerar lote de vouchers

*Como admin, quero gerar múltiplos vouchers de uma vez*

**Acceptance Criteria:**

1. Definir quantidade (1-1000)
2. Definir prazo de validade
3. Gerar códigos únicos
4. Exportar PDF com QR Codes
5. Listar todos vouchers gerados
6. Feedback visual

### Story 2.3 — Revogar voucher

*Como admin, quero revogar um voucher antes da expiração*

**Acceptance Criteria:**

1. Ação disponível na lista
2. Confirmação antes de revogar
3. Atualiza status no banco
4. Sessão ativa é encerrada (se possível)
5. Auditoria registrada
6. Feedback visual

---

## Epic 3 — Sessões e Controle

**Goal:** Controlar acesso por dispositivo

### Story 3.1 — Controle por MAC

*Como sistema, quero limitar por dispositivo*

**Acceptance Criteria:**

1. Apenas 1 MAC por credencial
2. Bloqueia novo acesso
3. Permite reset manual
4. Persistência
5. Feedback de erro
6. Controle de sessão

### Story 3.2 — Visualizar sessões ativas

*Como admin, quero ver quem está conectado*

**Acceptance Criteria:**

1. Tabela com dados em tempo real
2. Atualização periódica
3. Identificar usuário/voucher
4. Exibir MAC, IP, início da sessão
5. Opção de encerrar sessão
6. Estado vazio/carregando/erro

### Story 3.3 — Encerrar sessão remota (CoA)

*Como admin, quero desconectar um usuário*

**Acceptance Criteria:**

1. Botão "Encerrar sessão"
2. Confirmação prévia
3. Envia CoA ao FreeRADIUS
4. Fallback se CoA indisponível
5. Registro em auditoria
6. Feedback de sucesso/erro

---

## Epic 4 — Auditoria e Relatórios

**Goal:** Garantir rastreabilidade

### Story 4.1 — Registro de auditoria

*Como admin, quero histórico completo*

**Acceptance Criteria:**

1. Log de ações
2. Consulta por período
3. Retenção configurável
4. Exportação
5. Persistência
6. Feedback

### Story 4.2 — Dashboard operacional

*Como admin, quero visão rápida da operação*

**Acceptance Criteria:**

1. Cards com métricas principais
2. Gráfico de acessos por dia
3. Lista dos últimos acessos
4. Ações rápidas (criar/gerar)
5. Atualização em tempo real
6. Performance ≤ 2s

---

## Edge Cases

* Falha no FreeRADIUS → mensagem amigável e retry
* MAC duplicado → bloquear e orientar
* Sessão ativa sem accounting → alerta no dashboard
* Revogação sem CoA → registrar e tentar novamente
* Voucher expirado durante uso → encerrar na próxima validação
* Banco de dados indisponível → modo manutenção

---

# PARTE 2: REQUISITOS FUNCIONAIS

## 6. Funcionalidades Core

| Funcionalidade          | Prioridade | Descrição                                    |
| ----------------------- | ---------- | -------------------------------------------- |
| Portal cativo           | P0         | Interface para colaboradores e visitantes    |
| CRUD usuários           | P0         | Gestão completa de colaboradores             |
| Geração de vouchers     | P0         | Criação de lote e voucher individual         |
| Controle de sessão      | P1         | Visualização e encerramento de sessões       |
| Auditoria               | P1         | Log completo de ações e acessos              |
| Exportação PDF          | P1         | Geração de vouchers com QR Code              |
| Dashboard               | P1         | Métricas e visão rápida                      |
| Relatórios              | P2         | Consulta histórica com filtros               |
| Configurações           | P2         | Políticas e parâmetros do sistema            |

## 7. Integrações

| Integração      | Tipo          | Protocolo | Obrigatória |
| --------------- | ------------- | --------- | ----------- |
| FreeRADIUS      | Autenticação  | RADIUS    | Sim         |
| MySQL (FreeRADIUS) | Banco de dados | SQL       | Sim         |
| Sophos AP       | Rede          | RADIUS    | Sim         |
| CoA (opcional)  | Controle      | RADIUS    | Não         |

---

# PARTE 3: NÃO-FUNCIONAIS

## 8. Performance

| Métrica                    | Alvo          | Tolerância |
| -------------------------- | ------------- | ---------- |
| Tempo de resposta (p95)    | ≤ 3s          | 5s         |
| Usuários simultâneos       | 100           | 200        |
| Login portal               | ≤ 2s          | 4s         |
| Geração de vouchers (1000) | ≤ 10s         | 30s        |
| Exportação PDF (100)       | ≤ 5s          | 15s        |

## 9. Disponibilidade

| Métrica        | Alvo   | Observação                |
| -------------- | ------ | ------------------------- |
| SLA esperado   | 99.5%  | Horário comercial         |
| RTO            | 4–8h   | Restauração completa      |
| RPO            | 24h    | Backup diário             |
| Janela manutenção | Fora do horário comercial | Notificada |

## 10. Segurança

| Requisito                    | Especificação                        |
| ---------------------------- | ------------------------------------ |
| Senha colaborador mínimo     | 10 caracteres                        |
| Tentativas de login (admin)  | 5 tentativas                         |
| Bloqueio após tentativas     | 15 minutos                           |
| Sessão admin                 | 30 minutos inatividade               |
| Sessão colaborador (portal)  | 8 horas ou até expiração da credencial |
| Hash de senhas               | PBKDF2 (Django padrão)               |
| HTTPS                        | Obrigatório em produção              |
| Headers de segurança         | HSTS, X-Frame-Options, X-XSS-Protection |

## 11. Observabilidade

| Tipo              | Especificação                              |
| ----------------- | ------------------------------------------ |
| Logs estruturados | JSON com timestamp, nível, ação, usuário   |
| Retenção de logs  | 30 dias (configurável até 90)              |
| Métricas básicas  | Requests, erros, tempo de resposta         |
| Healthcheck       | Endpoint `/health` para monitoramento      |
| Alertas           | Falha FreeRADIUS, banco, alto erro de login|

## 12. Manutenibilidade

| Aspecto           | Especificação                              |
| ----------------- | ------------------------------------------ |
| Framework         | Django 4.x (monolito)                      |
| Banco de dados    | MySQL 8.x                                  |
| Testes automáticos| Unitários (cobertura mínima 70%)           |
| Documentação      | README, setup, runbook básico              |
| Versionamento     | Git (GitHub/GitLab)                        |

---

# PARTE 4: ARQUITETURA

## 13. Arquitetura Geral
