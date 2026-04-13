from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .forms import ColaboradorForm
from .models import UserMacMapping


class ColaboradorFormIntegrationTests(TestCase):
    def test_create_colaborador_syncs_radius_password_and_mac(self):
        form = ColaboradorForm(
            data={
                'first_name': 'Ana',
                'last_name': 'Silva',
                'username': 'ana.silva',
                'password': 'SenhaForte@123',
                'mac_address': 'AA:BB:CC:DD:EE:FF',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        with patch('core.signals.RadCheck.objects.update_or_create') as mock_radius, patch(
            'core.signals.AuditLog.objects.create'
        ) as mock_audit:
            user = form.save()

        self.assertTrue(user.check_password('SenhaForte@123'))
        self.assertFalse(hasattr(user, '_radius_password'))

        mapping = UserMacMapping.objects.get(user=user)
        self.assertEqual(mapping.mac_address, 'AA:BB:CC:DD:EE:FF')

        mock_radius.assert_called_once_with(
            username='ana.silva',
            attribute='Cleartext-Password',
            defaults={'op': ':=', 'value': 'SenhaForte@123'},
        )
        mock_audit.assert_any_call(
            admin=None,
            action_type='RADIUS_ACCOUNT_CREATED',
            target_object='RADIUS User: ana.silva',
            details='Credenciais sincronizadas com FreeRADIUS a partir do fluxo do formulário.',
        )

    def test_update_colaborador_refreshes_radius_password_and_mac(self):
        user = User.objects.create_user(
            username='joao.souza',
            password='SenhaAntiga@123',
            first_name='Joao',
            last_name='Souza',
        )
        UserMacMapping.objects.create(user=user, mac_address='11:22:33:44:55:66')

        form = ColaboradorForm(
            data={
                'first_name': 'Joao',
                'last_name': 'Souza',
                'username': 'joao.souza',
                'password': 'SenhaNova@456',
                'mac_address': 'AA:11:BB:22:CC:33',
            },
            instance=user,
        )

        self.assertTrue(form.is_valid(), form.errors)

        with patch('core.signals.RadCheck.objects.update_or_create') as mock_radius, patch(
            'core.signals.AuditLog.objects.create'
        ) as mock_audit:
            updated_user = form.save()

        self.assertEqual(updated_user.pk, user.pk)
        self.assertTrue(updated_user.check_password('SenhaNova@456'))
        self.assertFalse(hasattr(updated_user, '_radius_password'))

        mapping = UserMacMapping.objects.get(user=updated_user)
        self.assertEqual(mapping.mac_address, 'AA:11:BB:22:CC:33')

        mock_radius.assert_called_once_with(
            username='joao.souza',
            attribute='Cleartext-Password',
            defaults={'op': ':=', 'value': 'SenhaNova@456'},
        )
        mock_audit.assert_any_call(
            admin=None,
            action_type='RADIUS_ACCOUNT_UPDATED',
            target_object='RADIUS User: joao.souza',
            details='Credenciais sincronizadas com FreeRADIUS a partir do fluxo do formulário.',
        )

    def test_update_existing_mac_mapping_reuses_single_record(self):
        user = User.objects.create_user(
            username='maria.oliveira',
            password='SenhaOriginal@123',
            first_name='Maria',
            last_name='Oliveira',
        )
        existing_mapping = UserMacMapping.objects.create(
            user=user,
            mac_address='00:11:22:33:44:55',
        )

        form = ColaboradorForm(
            data={
                'first_name': 'Maria',
                'last_name': 'Oliveira',
                'username': 'maria.oliveira',
                'password': 'SenhaOriginal@123',
                'mac_address': '66:77:88:99:AA:BB',
            },
            instance=user,
        )

        self.assertTrue(form.is_valid(), form.errors)

        with patch('core.signals.RadCheck.objects.update_or_create') as mock_radius, patch(
            'core.signals.AuditLog.objects.create'
        ):
            form.save()

        self.assertEqual(UserMacMapping.objects.count(), 1)
        updated_mapping = UserMacMapping.objects.get(user=user)
        self.assertEqual(updated_mapping.pk, existing_mapping.pk)
        self.assertEqual(updated_mapping.mac_address, '66:77:88:99:AA:BB')
        mock_radius.assert_called_once_with(
            username='maria.oliveira',
            attribute='Cleartext-Password',
            defaults={'op': ':=', 'value': 'SenhaOriginal@123'},
        )
