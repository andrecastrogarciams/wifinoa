# Arquitetura Técnica — Sistema Wi-Fi Viposa

**Status:** 🏗️ Design Phase
**Architect:** @architect (Alex)

## 1. Stack Tecnológica
- **Linguagem:** Python 3.10+
- **Framework:** Django 4.2+ (Monolito)
- **Banco de Dados:** MySQL 8.0 (Compartilhado com FreeRADIUS)
- **Servidor RADIUS:** FreeRADIUS 3.x
- **Frontend:** Django Templates + TailwindCSS (seguindo Design System Meridian)

## 2. Integração com FreeRADIUS
O Django atuará como a camada de gestão (Control Plane) sobre o banco de dados do FreeRADIUS.

### 2.1 Modelos Unmanaged (Tabelas Legadas)
Utilizaremos `managed = False` no Django para as tabelas nativas do RADIUS, evitando que migrações acidentais alterem a estrutura esperada pelo servidor RADIUS.

- **`RadCheck`:** Armazena `username`, `attribute` (ex: 'Cleartext-Password'), `op` (':='), e `value` (senha).
- **`RadAcct`:** Logs de acesso. Chave para monitoramento de sessões ativas (`acctstoptime IS NULL`).

### 2.2 Modelos Customizados (Lógica Viposa)
- **`UserMacMapping`:** 
  - `user`: ForeignKey(User)
  - `mac_address`: CharField(unique=True)
  - `device_info`: CharField (opcional)
- **`Voucher`:**
  - `code`: CharField(unique=True)
  - `created_at`: DateTimeField
  - `expires_at`: DateTimeField
  - `is_revoked`: BooleanField
  - `mac_address`: CharField (vincula ao dispositivo no primeiro uso)

## 3. Segurança e Infraestrutura
- **Comunicação CoA:** O Django enviará comandos de desconexão via socket RADIUS (porta 1700/UDP) usando a biblioteca `pyrad`.
- **Isolamento:** O Portal Cativo deve estar em uma DMZ com acesso restrito ao MySQL do RADIUS e aos APs.

## 4. Estratégia de Migração (Sophos -> Custom)
1. Instalação do FreeRADIUS integrado ao MySQL.
2. Configuração dos APs Sophos para usar o servidor RADIUS como autenticador externo.
3. Deploy do Portal Django apontando para o mesmo banco.
4. Testes de interceptação de MAC via parâmetros de query do Sophos.

---
*Planejado por @architect (Alex)*
