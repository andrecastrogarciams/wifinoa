from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib import messages
from .models import UserMacMapping, Voucher, RadCheck

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
            mapping, created = UserMacMapping.objects.get_or_create(
                user=user,
                defaults={'mac_address': mac}
            )

            if not created and mapping.mac_address != mac:
                messages.error(request, "Este usuário já está vinculado a outro dispositivo.")
                return render(request, 'core/login_colaborador.html', {'mac': mac})

            # 3. Sucesso: Liberar no RADIUS (Simulado via DB)
            # RadCheck.objects.get_or_create(username=username, attribute='Cleartext-Password', value=password)
            
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
                
                # Liberar no RADIUS (Simulado)
                # RadCheck.objects.get_or_create(username=code, attribute='Auth-Type', value='Accept')
                
                return redirect('core:success')
                
        except Voucher.DoesNotExist:
            messages.error(request, "Voucher inválido.")

        return render(request, 'core/login_visitante.html', {'code': code, 'mac': mac})

class SuccessView(View):
    def get(self, request):
        return render(request, 'core/success.html')
