from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserMacMapping, RadCheck, AuditLog

@receiver(post_save, sender=User)
def sync_user_credentials_to_radius(sender, instance, created, **kwargs):
    """
    Sincroniza as credenciais do Django User com o RADIUS (radcheck) quando a senha
    em texto plano é fornecida pelo fluxo do formulário.
    """
    if instance.is_staff:
        return # Não sincroniza administradores com o RADIUS de acesso Wi-Fi
    password = getattr(instance, '_radius_password', None)
    if not password:
        return

    RadCheck.objects.update_or_create(
        username=instance.username,
        attribute='Cleartext-Password',
        defaults={'op': ':=', 'value': password},
    )

    action_type = "RADIUS_ACCOUNT_CREATED" if created else "RADIUS_ACCOUNT_UPDATED"
    AuditLog.objects.create(
        admin=None,
        action_type=action_type,
        target_object=f"RADIUS User: {instance.username}",
        details="Credenciais sincronizadas com FreeRADIUS a partir do fluxo do formulário."
    )

    # Evita reuso acidental do valor em memória em chamadas subsequentes.
    delattr(instance, '_radius_password')

@receiver(post_save, sender=UserMacMapping)
def sync_mac_mapping_to_radius(sender, instance, created, **kwargs):
    """
    Ações adicionais quando um MAC é vinculado.
    """
    username = instance.user.username
    
    action = "MAC_VINCULO_CREATE" if created else "MAC_VINCULO_UPDATE"
    
    AuditLog.objects.create(
        admin=None,
        action_type=action,
        target_object=f"Colaborador: {username}",
        details=f"Vínculo de MAC {'criado' if created else 'atualizado'}: {instance.mac_address}"
    )

@receiver(post_delete, sender=UserMacMapping)
def remove_user_from_radius(sender, instance, **kwargs):
    """
    Quando o vínculo de MAC é removido, opcionalmente removemos o usuário do RADIUS
    ou apenas limpamos o MAC. Aqui, manteremos o usuário mas o RADIUS não terá mais o MAC para validar
    se a política de 'um dispositivo por usuário' for aplicada no nível do RADIUS.
    """
    username = instance.user.username
    # Se quisermos impedir o acesso totalmente ao remover o MAC:
    # RadCheck.objects.filter(username=username).delete()
    
    AuditLog.objects.create(
        admin=None,
        action_type="MAC_VINCULO_DELETE",
        target_object=f"Colaborador: {username}",
        details=f"Vínculo de MAC removido. O usuário precisará vincular um novo dispositivo."
    )
