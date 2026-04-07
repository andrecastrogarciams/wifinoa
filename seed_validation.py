import os
import django
from django.db import connection

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wifinoa_project.settings')
    django.setup()

    # 0. Criar tabelas RADIUS simuladas (Necessário pois managed=False)
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS radcheck (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(64),
                attribute VARCHAR(64),
                op VARCHAR(2),
                value VARCHAR(253)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS radacct (
                radacctid INTEGER PRIMARY KEY AUTOINCREMENT,
                acctsessionid VARCHAR(64),
                acctuniqueid VARCHAR(32),
                username VARCHAR(64),
                groupname VARCHAR(64),
                realm VARCHAR(64),
                nasipaddress VARCHAR(15),
                nasportid VARCHAR(15),
                nasporttype VARCHAR(32),
                acctstarttime DATETIME,
                acctupdatetime DATETIME,
                acctstoptime DATETIME,
                acctinterval INTEGER,
                acctsessiontime BIGINT,
                acctauthentic VARCHAR(32),
                connectinfo_start VARCHAR(50),
                connectinfo_stop VARCHAR(50),
                acctinputoctets BIGINT,
                acctoutputoctets BIGINT,
                calledstationid VARCHAR(50),
                callingstationid VARCHAR(50),
                acctterminatecause VARCHAR(32),
                servicetype VARCHAR(32),
                framedprotocol VARCHAR(32),
                framedipaddress VARCHAR(15)
            )
        """)

    from datetime import timedelta
    from django.utils import timezone
    from django.contrib.auth.models import User
    from core.models import Voucher, UserMacMapping, AuditLog, RadAcct

    print("Iniciando Seed de Validação...")

    # 1. Colaborador
    user, _ = User.objects.get_or_create(username='colaborador.teste', defaults={'first_name': 'João', 'is_staff': False})
    user.set_password('viposa123')
    user.save()
    
    # Criar vínculo de MAC (Isso disparará o Signal para o radcheck)
    mapping, _ = UserMacMapping.objects.get_or_create(
        user=user, 
        defaults={'mac_address': 'AA:BB:CC:DD:EE:FF', 'device_info': 'Smartphone João'}
    )
    print("- Colaborador de teste criado e sincronizado com RADIUS.")

    # 2. Vouchers
    Voucher.objects.get_or_create(code='ABCD-1234', defaults={'expires_at': timezone.now() + timedelta(days=1)})
    Voucher.objects.get_or_create(code='EXPI-0000', defaults={'expires_at': timezone.now() - timedelta(hours=5)})
    Voucher.objects.get_or_create(code='REV0-1111', defaults={'expires_at': timezone.now() + timedelta(days=1), 'is_revoked': True})
    print("- Vouchers criados.")

    # 3. Auditoria
    AuditLog.objects.create(action_type="SYSTEM_VALIDATION", target_object="Database", details="Seed de dados executado com sucesso.")
    
    # 4. Sessões Simuladas
    RadAcct.objects.get_or_create(
        acctsessionid='TEST-SESS-001',
        acctuniqueid='UNIQUE-001',
        username='colaborador.teste',
        nasipaddress='192.168.1.1',
        acctstarttime=timezone.now() - timedelta(hours=2),
        callingstationid='AA:BB:CC:DD:EE:FF',
        framedipaddress='10.0.0.50'
    )
    print("- Sessão ativa simulada criada.")

    print("\nValidação concluída!")
    print("Acesse http://127.0.0.1:8000/admin para visualizar o Dashboard.")

if __name__ == "__main__":
    seed()
