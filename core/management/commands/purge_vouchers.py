from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Voucher, RadCheck, AuditLog

class Command(BaseCommand):
    help = 'Remove vouchers expirados há mais de 30 dias (Django e FreeRADIUS)'

    def handle(self, *args, **options):
        threshold_date = timezone.now() - timedelta(days=30)
        
        # 1. Buscar vouchers expirados há mais de 30 dias
        expired_vouchers = Voucher.objects.filter(expires_at__lt=threshold_date)
        count = expired_vouchers.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum voucher antigo para remover.'))
            return

        # 2. Remover do FreeRADIUS (RadCheck) de forma sincronizada
        codes_to_remove = expired_vouchers.values_list('code', flat=True)
        RadCheck.objects.using('default').filter(username__in=codes_to_remove).delete()
        
        # 3. Remover do Django
        expired_vouchers.delete()
        
        # 4. Registrar em Auditoria (Story 4.1)
        AuditLog.objects.create(
            admin=None, # Ação do sistema (Cron/Task)
            action_type="SYSTEM_PURGE_VOUCHERS",
            target_object=f"Lote: {count} vouchers",
            details=f"Limpeza automática de vouchers expirados antes de {threshold_date.strftime('%d/%m/%Y')}."
        )

        self.stdout.write(self.style.SUCCESS(f'Sucesso: {count} vouchers removidos do sistema.'))
