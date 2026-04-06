from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ---------------------------------------------------------
# FREE RADIUS MODELS (Managed=False)
# ---------------------------------------------------------

class RadCheck(models.Model):
    """
    Tabela nativa do FreeRADIUS para autenticação.
    """
    username = models.CharField(max_length=64, db_index=True)
    attribute = models.CharField(max_length=64, default='Cleartext-Password')
    op = models.CharField(max_length=2, default=':=')
    value = models.CharField(max_length=253)

    class Meta:
        managed = False
        db_table = 'radcheck'
        verbose_name = 'RADIUS Check'
        verbose_name_plural = 'RADIUS Checks'

    def __str__(self):
        return f"{self.username} ({self.attribute})"


class RadAcct(models.Model):
    """
    Tabela nativa do FreeRADIUS para logs de accounting.
    """
    radacctid = models.BigAutoField(primary_key=True)
    acctsessionid = models.CharField(max_length=64, db_index=True)
    acctuniqueid = models.CharField(max_length=32, unique=True)
    username = models.CharField(max_length=64, db_index=True)
    groupname = models.CharField(max_length=64, default='')
    realm = models.CharField(max_length=64, default='')
    nasipaddress = models.GenericIPAddressField(db_index=True)
    nasportid = models.CharField(max_length=15, blank=True, null=True)
    nasporttype = models.CharField(max_length=32, blank=True, null=True)
    acctstarttime = models.DateTimeField(null=True, blank=True, db_index=True)
    acctupdatetime = models.DateTimeField(null=True, blank=True)
    acctstoptime = models.DateTimeField(null=True, blank=True, db_index=True)
    acctinterval = models.IntegerField(null=True, blank=True)
    acctsessiontime = models.BigIntegerField(null=True, blank=True)
    acctauthentic = models.CharField(max_length=32, blank=True, null=True)
    connectinfo_start = models.CharField(max_length=50, blank=True, null=True)
    connectinfo_stop = models.CharField(max_length=50, blank=True, null=True)
    acctinputoctets = models.BigIntegerField(null=True, blank=True)
    acctoutputoctets = models.BigIntegerField(null=True, blank=True)
    calledstationid = models.CharField(max_length=50, blank=True, null=True)
    callingstationid = models.CharField(max_length=50, blank=True, null=True, db_index=True) # Geralmente o MAC
    acctterminatecause = models.CharField(max_length=32, blank=True, null=True)
    servicetype = models.CharField(max_length=32, blank=True, null=True)
    framedprotocol = models.CharField(max_length=32, blank=True, null=True)
    framedipaddress = models.GenericIPAddressField(null=True, blank=True, db_index=True)

    class Meta:
        managed = False
        db_table = 'radacct'
        verbose_name = 'RADIUS Accounting'
        verbose_name_plural = 'RADIUS Accounting'

    def __str__(self):
        return f"Session {self.acctsessionid} - {self.username}"


# ---------------------------------------------------------
# VIPOSA CUSTOM MODELS (Managed=True)
# ---------------------------------------------------------

class UserMacMapping(models.Model):
    """
    Vínculo fixo entre um colaborador (Django User) e um dispositivo (MAC Address).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mac_mapping')
    mac_address = models.CharField(max_length=17, unique=True, db_index=True, help_text="Formato XX:XX:XX:XX:XX:XX")
    device_info = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} -> {self.mac_address}"


class Voucher(models.Model):
    """
    Gestão de acesso temporário para visitantes.
    """
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('expired', 'Expirado'),
        ('revoked', 'Revogado'),
        ('used', 'Utilizado'),
    ]

    code = models.CharField(max_length=12, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    mac_address = models.CharField(max_length=17, blank=True, null=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def status(self):
        if self.is_revoked:
            return 'revoked'
        if self.mac_address and self.used_at:
            return 'used'
        if timezone.now() > self.expires_at:
            return 'expired'
        return 'active'

    def __str__(self):
        return f"Voucher {self.code} ({self.status})"


class AuditLog(models.Model):
    """
    Rastro de auditoria de ações administrativas.
    """
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=100) # ex: CRUD, REVOKE, MAC_RESET
    target_object = models.CharField(max_length=255) # ex: Colaborador João, Voucher A1B2
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.admin} - {self.action_type}"
