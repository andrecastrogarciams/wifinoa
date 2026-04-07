from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserMacMapping, RadCheck, AuditLog

@receiver(post_save, sender=UserMacMapping)
def sync_user_to_radius(sender, instance, created, **kwargs):
    """
    Sincroniza o colaborador com a tabela radcheck do FreeRADIUS.
    Nota: A senha sincronizada aqui é um placeholder ou deve ser gerada/capturada.
    """
    username = instance.user.username
    
    # Busca ou cria a entrada no RADIUS
    rad_user, rad_created = RadCheck.objects.get_or_create(
        username=username,
        attribute='Cleartext-Password',
        defaults={'op': ':=', 'value': 'mudar123'} # Senha padrão inicial
    )

    action = "RADIUS_SYNC_CREATE" if rad_created else "RADIUS_SYNC_UPDATE"
    
    AuditLog.objects.create(
        admin=None,
        action_type=action,
        target_object=f"RADIUS User: {username}",
        details=f"Usuário sincronizado com FreeRADIUS após alteração no vínculo de MAC."
    )

@receiver(post_delete, sender=UserMacMapping)
def remove_user_from_radius(sender, instance, **kwargs):
    """
    Remove o usuário do RADIUS se o vínculo de MAC for excluído.
    """
    username = instance.user.username
    RadCheck.objects.filter(username=username).delete()
    
    AuditLog.objects.create(
        admin=None,
        action_type="RADIUS_SYNC_DELETE",
        target_object=f"RADIUS User: {username}",
        details=f"Usuário removido do FreeRADIUS após exclusão do vínculo de MAC."
    )
