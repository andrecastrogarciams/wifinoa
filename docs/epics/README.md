# Sistema Wi-Fi Viposa S.A. — Status do Projeto

**Data da Última Atualização:** 06/04/2026
**Fase Atual:** Evolução Pós-MVP (UI/UX Editorial)

---

## 🎯 Resumo Executivo
O projeto Wi-Fi Viposa foi desenvolvido com sucesso, substituindo o portal nativo da Sophos por um ecossistema customizado em Django + FreeRADIUS. A fase MVP técnica foi entregue e a atual fase de **Interface Editorial** (The Orchestrated Core) atingiu 90% de completude.

## ✅ Entregas Concluídas

### 1. Autenticação e Portal Cativo
- [x] Portal Visitante (High-Fidelity UI, validação QR Code e alertas dinâmicos de erro).
- [x] Portal Colaborador (Vínculo automático de MAC Address).
- [x] Sincronização automatizada via `Signals` entre o Django e a tabela `radcheck` do FreeRADIUS.

### 2. Painel de Gestão (Interface Customizada)
- [x] **Dashboard:** KPIs em tempo real, gráfico interativo de acessos (Chart.js) e tabela de eventos recentes.
- [x] **Gráfico de Dispositivos (US-4.1):** Implementada a segmentação "Mobile vs Desktop" usando captura de User-Agent.
- [x] **Central de Auditoria Customizada:** Criada página de relatórios (`/gestao/relatorios/`) com filtros avançados e exportação CSV.
- [x] **Gestão de Colaboradores:** Listagem completa e modal lateral funcional para Criação de Colaboradores.
- [x] **Gestão de Vouchers:** Listagem com checkbox em lote, modal lateral para Geração de Lotes e exportação para PDF (QR Codes).
- [x] **Sessões Ativas:** Visualização em tempo real via tabela de accounting (`radacct`) com botão de Desconexão Remota (CoA via `pyrad`).

### 3. Backend / Segurança
- [x] Rastreabilidade completa via `AuditLog` para logins e ações administrativas.
- [x] Proxy Models e Views otimizadas.

---

## 🚀 Próximos Passos (Para Retomada)

As seguintes tarefas estão no Backlog prontas para serem desenvolvidas na próxima sessão:

1. **Auto-Purge (Manutenção de Banco):**
   - Criar um `Management Command` do Django (ex: `python manage.py purge_vouchers`) para limpar vouchers expirados há mais de 30 dias.
2. **Ambiente de Produção:**
   - Configurar variáveis de ambiente (`.env`) para conectar o Django ao MySQL real de produção do FreeRADIUS.

---

## 🛠️ Stack Local
- `python manage.py runserver` rodando em `127.0.0.1:8000`.
- Superuser de teste: `admin` / `admin123`.
- Ambiente Virtual ativado na pasta `venv/`.
