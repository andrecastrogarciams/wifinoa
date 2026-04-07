import csv
from django.contrib import admin
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from .models import UserMacMapping, Voucher, AuditLog, RadCheck, RadAcct, ActiveSession
from .utils import generate_vouchers_pdf, send_radius_coa_disconnect
from .dashboard import get_dashboard_metrics

# ---------------------------------------------------------
# DASHBOARD INJECTION
# ---------------------------------------------------------

original_index = admin.site.index

def admin_index_with_metrics(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    extra_context['metrics'] = get_dashboard_metrics()
    return original_index(request, extra_context=extra_context)

admin.site.index = admin_index_with_metrics

# ---------------------------------------------------------
# VIPOSA CUSTOM ADMINS
# ---------------------------------------------------------

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('username', 'callingstationid', 'framedipaddress', 'acctstarttime', 'session_duration')
    search_fields = ('username', 'callingstationid', 'framedipaddress')
    list_filter = ('acctstarttime',)
    
    actions = ['disconnect_users']

    @admin.action(description="Encerrar sessões selecionadas (CoA)")
    def disconnect_users(self, request, queryset):
        success_count = 0
        error_count = 0
        
        for session in queryset:
            success, message = send_radius_coa_disconnect(
                username=session.username,
                nas_ip=session.nasipaddress,
                session_id=session.acctsessionid
            )
            
            if success:
                success_count += 1
                # Registro em Auditoria (Story 4.2)
                AuditLog.objects.create(
                    admin=request.user,
                    action_type="RADIUS_COA_DISCONNECT",
                    target_object=f"Usuário: {session.username} (Session: {session.acctsessionid})",
                    details=f"Comando de desconexão enviado para NAS {session.nasipaddress}."
                )
            else:
                error_count += 1
        
        if success_count:
            self.message_user(request, f"{success_count} comandos de desconexão enviados com sucesso.")
        if error_count:
            self.message_user(request, f"Falha ao enviar {error_count} comandos.", level='error')

    def session_duration(self, obj):
        if obj.acctstarttime:
            diff = timezone.now() - obj.acctstarttime
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{diff.days}d {hours}h {minutes}m"
        return "N/A"
    
    session_duration.short_description = "Duração"

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(UserMacMapping)
class UserMacMappingAdmin(admin.ModelAdmin):
    list_display = ('user', 'mac_address', 'created_at', 'updated_at')
    search_fields = ('user__username', 'mac_address')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user',)

    actions = ['reset_mac_address']

    @admin.action(description="Resetar MAC Address (Permitir novo dispositivo)")
    def reset_mac_address(self, request, queryset):
        for mapping in queryset:
            user_name = mapping.user.username
            old_mac = mapping.mac_address
            
            # Registro em Auditoria ANTES de deletar (Story 4.2)
            AuditLog.objects.create(
                admin=request.user,
                action_type="MAC_RESET",
                target_object=f"Colaborador: {user_name}",
                details=f"Vínculo de MAC resetado. MAC anterior: {old_mac}. O usuário poderá registrar um novo dispositivo no próximo login."
            )
            
            mapping.delete()
        
        self.message_user(request, f"Vínculo de MAC resetado para {queryset.count()} colaborador(es).")

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'expires_at', 'mac_address', 'used_at')
    list_filter = ('is_revoked', 'expires_at')
    search_fields = ('code', 'mac_address')
    readonly_fields = ('used_at',)
    
    actions = ['revoke_selected_vouchers', 'export_vouchers_pdf']

    @admin.action(description="Revogar vouchers selecionados")
    def revoke_selected_vouchers(self, request, queryset):
        queryset.update(is_revoked=True)
        self.message_user(request, "Vouchers revogados com sucesso.")

    @admin.action(description="Exportar vouchers selecionados para PDF")
    def export_vouchers_pdf(self, request, queryset):
        buffer = generate_vouchers_pdf(queryset)
        return FileResponse(buffer, as_attachment=True, filename="vouchers_viposa.pdf")

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

    actions = ['export_access_log_csv']

    @admin.action(description="Exportar registros selecionados para CSV")
    def export_access_log_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="historico_acesso_viposa.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID Sessão', 'Usuário', 'MAC Address', 'IP', 'Início', 'Fim', 'Duração (s)', 'Input Octets', 'Output Octets'])
        
        for record in queryset:
            writer.writerow([
                record.acctsessionid,
                record.username,
                record.callingstationid,
                record.framedipaddress,
                record.acctstarttime,
                record.acctstoptime,
                record.acctsessiontime,
                record.acctinputoctets,
                record.acctoutputoctets,
            ])
            
        return response

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
