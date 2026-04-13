from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import RadAcct, UserMacMapping, Voucher, AuditLog
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Sincroniza os MAC Addresses das sessões do FreeRADIUS (Accounting) para os modelos da aplicação.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando sincronização de MACs via FreeRADIUS Accounting..."))
        
        # 1. Buscar sessões recentes (Accounting Start)
        sessoes = RadAcct.objects.filter(acctstoptime__isnull=True).order_by('-acctstarttime')[:100]
        
        sync_count = 0
        
        for sessao in sessoes:
            mac = sessao.callingstationid
            username = sessao.username
            
            if not mac or not username:
                continue
                
            # --- TENTATIVA 1: COLABORADORES ---
            try:
                user = User.objects.get(username=username)
                mapping, created = UserMacMapping.objects.get_or_create(
                    user=user,
                    defaults={'mac_address': mac, 'device_info': f"Detectado via RADIUS: {sessao.nasipaddress}"}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"MAC {mac} vinculado ao Colaborador {username} (RADIUS Sync)"))
                    sync_count += 1
            except User.DoesNotExist:
                # --- TENTATIVA 2: VOUCHERS (VISITANTES) ---
                try:
                    voucher = Voucher.objects.get(code=username) # Username do RADIUS no voucher é o próprio código
                    if not voucher.mac_address:
                        voucher.mac_address = mac
                        voucher.used_at = sessao.acctstarttime # Retroativo
                        voucher.save()
                        self.stdout.write(self.style.SUCCESS(f"MAC {mac} vinculado ao Voucher {username} (RADIUS Sync)"))
                        sync_count += 1
                except Voucher.DoesNotExist:
                    continue

        if sync_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Sincronização concluída. {sync_count} MACs vinculados automaticamente."))
        else:
            self.stdout.write(self.style.NOTICE("Nenhum novo MAC para sincronizar."))
