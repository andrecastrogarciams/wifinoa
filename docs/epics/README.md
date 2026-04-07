# Sistema Wi-Fi Viposa S.A. — Status do Projeto

**Data da Última Atualização:** 07/04/2026
**Fase Atual:** Evolução Pós-MVP Concluída

---

## 🎯 Resumo Executivo
O projeto Wi-Fi Viposa foi desenvolvido com sucesso, substituindo o portal nativo da Sophos por um ecossistema customizado em Django + FreeRADIUS. Todas as fases, incluindo a **Interface Editorial** e as funcionalidades de **Evolução Pós-MVP**, foram entregues com 100% de completude.

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
- [x] **Ambiente de Produção:** Configuração via `.env` para suporte a MySQL/FreeRADIUS real.
- [x] **Auto-Purge (Manutenção de Banco):** Criado o comando `python manage.py purge_vouchers` para limpeza automática de vouchers antigos.
- [x] Rastreabilidade completa via `AuditLog` para logins e ações administrativas.
- [x] Proxy Models e Views otimizadas.

---

## 🚀 Próximos Passos
O sistema está pronto para implantação em larga escala. Próximas recomendações:
1.  **Monitoramento:** Integração com Sentry para rastreamento de erros em produção.
2.  **Backup:** Agendamento automático de backups do banco de dados MySQL.

---

## 🛠️ Stack Local
- `python manage.py runserver` rodando em `127.0.0.1:8000`.
- Superuser de teste: `admin` / `admin123`.
- Ambiente Virtual ativado na pasta `venv/`.
