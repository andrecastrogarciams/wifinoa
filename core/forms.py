from django import forms
from django.contrib.auth.models import User
from .models import UserMacMapping

class ColaboradorForm(forms.ModelForm):
    mac_address = forms.CharField(
        max_length=17, 
        required=False, 
        label="Vincular Endereço MAC",
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white border border-outline-variant/20 rounded-md px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-primary/10 transition-all',
            'placeholder': '00:00:00:00:00:00'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-primary transition-all',
            'placeholder': 'Senha Provisória'
        }),
        label="Senha"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-primary transition-all', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-primary transition-all', 'placeholder': 'Sobrenome'}),
            'username': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-primary transition-all', 'placeholder': 'Login de Acesso'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        user.set_password(password)
        # Passa a senha em texto plano apenas durante este save para o signal
        # atualizar o RADIUS sem persistir fallback inseguro.
        user._radius_password = password
        if commit:
            user.save()

            # 1. Vincular MAC Address se fornecido
            mac = self.cleaned_data.get('mac_address')
            if mac:
                UserMacMapping.objects.update_or_create(
                    user=user, 
                    defaults={'mac_address': mac}
                )
        return user

class VoucherBatchForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, max_value=100, initial=10,
        label="Quantidade",
        widget=forms.NumberInput(attrs={'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-secondary transition-all'})
    )
    validity_days = forms.IntegerField(
        min_value=1, max_value=365, initial=1,
        label="Validade (Dias)",
        widget=forms.NumberInput(attrs={'class': 'w-full bg-surface-container-low border-none rounded-md px-4 py-3 text-sm focus:ring-0 focus:border-b-2 focus:border-secondary transition-all'})
    )

