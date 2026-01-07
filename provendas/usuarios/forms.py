# provendas/usuarios/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from .models import Perfil

class UsuarioForm(forms.ModelForm):
    # Campos de senha
    nova_senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova Senha'}),
        label='Nova Senha'
    )
    confirmar_senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Senha'}),
        label='Confirmar Senha'
    )

    # Campo de Grupos com Checkbox (para aparecer as opções Admin/Atendente)
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Permissões / Cargos"
    )

    # Campo de Foto de Perfil
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Foto de Perfil'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'grupos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if nova_senha or confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError("As senhas não correspondem. Por favor, verifique.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        foto = self.cleaned_data.get('foto_perfil')

        # Se uma nova senha for fornecida, define a senha
        if nova_senha:
            user.set_password(nova_senha)

        if commit:
            user.save()
            self.save_m2m()  # Salva os grupos (relação ManyToMany)

            # Lógica para salvar a foto no modelo Perfil
            if foto:
                # Tenta pegar o perfil existente ou cria um novo se não existir
                perfil, created = Perfil.objects.get_or_create(user=user)
                perfil.foto_perfil = foto
                perfil.save()

        return user