from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PortalIndexView.as_view(), name='portal_index'),
    path('colaborador/', views.LoginColaboradorView.as_view(), name='login_colaborador'),
    path('visitante/', views.LoginVisitanteView.as_view(), name='login_visitante'),
    path('sucesso/', views.SuccessView.as_view(), name='success'),
    
    # Custom Admin
    path('gestao/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('gestao/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('gestao/colaboradores/', views.AdminColaboradoresView.as_view(), name='admin_colaboradores'),
    path('gestao/colaboradores/novo/', views.AdminColaboradorCreateView.as_view(), name='admin_colaborador_create'),
    path('gestao/vouchers/', views.AdminVouchersView.as_view(), name='admin_vouchers'),
    path('gestao/vouchers/gerar/', views.AdminVoucherBatchCreateView.as_view(), name='admin_voucher_batch_create'),
    path('gestao/sessoes/', views.AdminSessoesView.as_view(), name='admin_sessoes'),
    path('gestao/relatorios/', views.AdminRelatoriosView.as_view(), name='admin_relatorios'),
    path('gestao/relatorios/exportar/', views.AdminRelatoriosExportView.as_view(), name='admin_relatorios_export'),
]
