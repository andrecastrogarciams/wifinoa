from django.contrib import admin
from .models import UserMacMapping, Voucher, AuditLog, RadCheck, RadAcct

# ---------------------------------------------------------
# VIPOSA CUSTOM ADMINS
# ---------------------------------------------------------

@admin.register(UserMacMapping)
class UserMacMappingAdmin(admin.ModelAdmin):
    list_display = ('user', 'mac_address', 'created_at', 'updated_at')
    search_fields = ('user__username', 'mac_address')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user',)

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'expires_at', 'mac_address', 'used_at')
    list_filter = ('is_revoked', 'expires_at')
    search_fields = ('code', 'mac_address')
    readonly_fields = ('used_at',)
    
    actions = ['revoke_selected_vouchers']

    @admin.action(description="Revogar vouchers selecionados")
    def revoke_selected_vouchers(self, request, queryset):
        queryset.update(is_revoked=True)
        self.message_user(request, "Vouchers revogados com sucesso.")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'admin', 'action_type', 'target_object')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('admin__username', 'target_object', 'details')
    readonly_fields = ('admin', 'action_type', 'target_object', 'details', 'timestamp')

    # Desabilitar edição e exclusão para manter a integridade dos logs
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

# ---------------------------------------------------------
# FREE RADIUS ADMINS (Read-Only Visualization)
# ---------------------------------------------------------

@admin.register(RadCheck)
class RadCheckAdmin(admin.ModelAdmin):
    list_display = ('username', 'attribute', 'op', 'value')
    search_fields = ('username', 'value')

@admin.register(RadAcct)
class RadAcctAdmin(admin.ModelAdmin):
    list_display = ('acctsessionid', 'username', 'callingstationid', 'acctstarttime', 'acctstoptime', 'framedipaddress')
    list_filter = ('acctstarttime', 'acctstoptime')
    search_fields = ('username', 'callingstationid', 'framedipaddress')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
