from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib import messages
from .models import UserMacMapping, Voucher, RadCheck, AuditLog

class PortalIndexView(View):
    def get(self, request):
        return render(request, 'core/index.html')

class LoginColaboradorView(View):
    def get(self, request):
        mac = request.GET.get('mac', '')
        return render(request, 'core/login_colaborador.html', {'mac': mac})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        mac = request.POST.get('mac')

        # 1. Autenticação Básica (Django/RADIUS Sync)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 2. Verificação de MAC (Story 1.1 / Story 3.1)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            mapping, created = UserMacMapping.objects.get_or_create(
                user=user,
                defaults={'mac_address': mac, 'device_info': user_agent}
            )

            if not created and mapping.mac_address != mac:
                messages.error(request, "Este usuário já está vinculado a outro dispositivo.")
                return render(request, 'core/login_colaborador.html', {'mac': mac})
            
            # Se já existe o mapping mas o device_info está vazio, vamos atualizar
            if not created and not mapping.device_info:
                mapping.device_info = user_agent
                mapping.save()

            # 3. Auditoria de Acesso (Story 4.2)
            AuditLog.objects.create(
                admin=None, # Não é ação administrativa
                action_type="PORTAL_LOGIN_COLABORADOR",
                target_object=f"Usuário: {username}",
                details=f"Login realizado via Portal Cativo. MAC: {mac}"
            )
            
            login(request, user)
            return redirect('core:success')
        
        messages.error(request, "Usuário ou senha inválidos.")
        return render(request, 'core/login_colaborador.html', {'mac': mac})

class LoginVisitanteView(View):
    def get(self, request):
        code = request.GET.get('code', '') # Suporte ao QR Code (Story 1.2)
        mac = request.GET.get('mac', '')
        return render(request, 'core/login_visitante.html', {'code': code, 'mac': mac})

    def post(self, request):
        code = request.POST.get('code')
        mac = request.POST.get('mac')

        try:
            voucher = Voucher.objects.get(code=code, is_revoked=False)
            
            if voucher.status == 'expired':
                messages.error(request, "Este voucher expirou.")
            elif voucher.status == 'used' and voucher.mac_address != mac:
                messages.error(request, "Este voucher já foi utilizado em outro dispositivo.")
            else:
                # Sucesso
                voucher.mac_address = mac
                voucher.used_at = timezone.now()
                voucher.save()

                # Auditoria de Acesso (Story 4.2)
                AuditLog.objects.create(
                    admin=None,
                    action_type="PORTAL_LOGIN_VISITANTE",
                    target_object=f"Voucher: {code}",
                    details=f"Login realizado via Voucher/QR Code. MAC: {mac}"
                )
                
                return redirect('core:success')
                
        except Voucher.DoesNotExist:
            messages.error(request, "Voucher inválido.")

        return render(request, 'core/login_visitante.html', {'code': code, 'mac': mac})

class SuccessView(View):
    def get(self, request):
        return render(request, 'core/success.html')

class AdminLoginView(View):
    def get(self, request):
        return render(request, 'core/admin_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('core:admin_dashboard') # Próxima tela a ser implementada
        
        messages.error(request, "Acesso negado. Verifique suas credenciais de administrador.")
        return render(request, 'core/admin_login.html')

class AdminDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        from .dashboard import get_dashboard_metrics
        metrics = get_dashboard_metrics()
        
        return render(request, 'core/admin_dashboard.html', {'metrics': metrics})

class AdminColaboradoresView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        # Buscar usuários que não são staff (colaboradores) e seus vínculos de MAC
        from django.contrib.auth.models import User
        from .forms import ColaboradorForm
        colaboradores = User.objects.filter(is_staff=False).prefetch_related('mac_mapping').order_by('-date_joined')
        form = ColaboradorForm()
        
        return render(request, 'core/admin_colaboradores.html', {
            'colaboradores': colaboradores,
            'form': form
        })

class AdminColaboradorCreateView(View):
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        from .forms import ColaboradorForm
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auditoria (Story 4.2)
            AuditLog.objects.create(
                admin=request.user,
                action_type="COLABORADOR_CREATE",
                target_object=f"Usuário: {user.username}",
                details=f"Colaborador criado via interface de gestão customizada."
            )
            messages.success(request, f"Colaborador {user.username} criado com sucesso.")
        else:
            for error in form.errors.values():
                messages.error(request, error)
        
        return redirect('core:admin_colaboradores')

class AdminVouchersView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        from .models import Voucher
        from .forms import VoucherBatchForm
        vouchers = Voucher.objects.all().order_by('-created_at')
        form = VoucherBatchForm()
        
        return render(request, 'core/admin_vouchers.html', {
            'vouchers': vouchers,
            'form': form
        })

class AdminVoucherBatchCreateView(View):
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        import string
        import random
        from .forms import VoucherBatchForm
        from .models import Voucher
        
        form = VoucherBatchForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            days = form.cleaned_data['validity_days']
            expires_at = timezone.now() + timezone.timedelta(days=days)
            
            created_count = 0
            for _ in range(qty):
                # Gerar código único: XXXX-XXXX
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                formatted_code = f"{code[:4]}-{code[4:]}"
                
                Voucher.objects.create(
                    code=formatted_code,
                    expires_at=expires_at
                )
                created_count += 1
            
            # Auditoria
            AuditLog.objects.create(
                admin=request.user,
                action_type="VOUCHER_BATCH_CREATE",
                target_object=f"Lote: {qty} vouchers",
                details=f"Geração de {qty} vouchers com validade de {days} dias."
            )
            messages.success(request, f"Lote de {created_count} vouchers gerado com sucesso.")
        
        return redirect('core:admin_vouchers')

class AdminSessoesView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        from .models import ActiveSession
        sessoes = ActiveSession.objects.all().order_by('-acctstarttime')
        
        return render(request, 'core/admin_sessoes.html', {'sessoes': sessoes})

class AdminRelatoriosView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
        
        from .models import AuditLog
        from django.db.models import Q
        
        query = request.GET.get('q', '')
        action_type = request.GET.get('type', '')
        date_from = request.GET.get('from', '')
        date_to = request.GET.get('to', '')
        
        logs = AuditLog.objects.all()
        
        if query:
            logs = logs.filter(
                Q(target_object__icontains=query) | 
                Q(details__icontains=query) |
                Q(admin__username__icontains=query)
            )
            
        if action_type:
            logs = logs.filter(action_type=action_type)
            
        if date_from:
            logs = logs.filter(timestamp__date__gte=date_from)
            
        if date_to:
            logs = logs.filter(timestamp__date__lte=date_to)
            
        # Tipos de ação para o filtro
        action_types = AuditLog.objects.values_list('action_type', flat=True).distinct()
        
        return render(request, 'core/admin_relatorios.html', {
            'logs': logs[:500], # Limite para performance
            'action_types': action_types,
            'filters': {
                'q': query,
                'type': action_type,
                'from': date_from,
                'to': date_to
            }
        })

class AdminRelatoriosExportView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('core:admin_login')
            
        import csv
        from django.http import HttpResponse
        from .models import AuditLog
        
        logs = AuditLog.objects.all().order_by('-timestamp')
        
        # Aplicar mesmos filtros da view de listagem
        query = request.GET.get('q', '')
        action_type = request.GET.get('type', '')
        date_from = request.GET.get('from', '')
        date_to = request.GET.get('to', '')
        
        if query:
            from django.db.models import Q
            logs = logs.filter(Q(target_object__icontains=query) | Q(details__icontains=query) | Q(admin__username__icontains=query))
        if action_type:
            logs = logs.filter(action_type=action_type)
        if date_from:
            logs = logs.filter(timestamp__date__gte=date_from)
        if date_to:
            logs = logs.filter(timestamp__date__lte=date_to)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_log_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Data/Hora', 'Admin', 'Ação', 'Alvo', 'Detalhes'])
        
        for log in logs:
            writer.writerow([
                log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                log.admin.username if log.admin else "Sistema",
                log.action_type,
                log.target_object,
                log.details
            ])
            
        return response
