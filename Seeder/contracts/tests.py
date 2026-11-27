from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from contracts.models import Contract, EmailNegotiation
from publishers.models import Publisher
from source.models import Category, Source


class ContractDeleteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='curator')
        cls.publisher = Publisher.objects.create(name='Publisher')
        cls.category = Category.objects.create(name='Category')
        cls.contract = Contract.objects.create(publisher=cls.publisher)

    def setUp(self):
        self.client = Client(
            enforce_csrf_checks=True, HTTP_HOST='127.0.0.1',
            HTTP_ACCEPT_LANGUAGE='en',
        )
        self.client.force_login(self.user)
        self.delete_url = reverse('contracts:delete', args=[self.contract.pk])
        self.detail_url = self.contract.get_absolute_url()
        self.list_url = reverse('contracts:list')

    def create_source(self, name, active=True):
        source = Source.objects.create(
            name=name, active=active, category=self.category,
            owner=self.user, created_by=self.user,
        )
        self.contract.sources.add(source)
        return source

    def delete_contract(self, follow=False):
        self.client.get(reverse('login'))
        token = self.client.cookies['csrftoken'].value
        return self.client.post(
            self.delete_url, {'csrfmiddlewaretoken': token}, follow=follow,
        )

    def assert_contract_exists(self):
        self.assertTrue(Contract.objects.filter(pk=self.contract.pk).exists())

    def test_deletes_contract_without_sources_and_shows_confirmation(self):
        response = self.delete_contract(follow=True)

        self.assertRedirects(response, self.list_url)
        self.assertContains(response, 'Contract deleted.', count=1)
        self.assertNotContains(self.client.get(self.list_url), 'Contract deleted.')
        self.assertFalse(Contract.objects.filter(pk=self.contract.pk).exists())

    def test_deletes_contract_with_deactivated_source(self):
        source = self.create_source('Deactivated source', active=False)

        response = self.delete_contract()

        self.assertRedirects(response, self.list_url, fetch_redirect_response=False)
        self.assertFalse(Contract.objects.filter(pk=self.contract.pk).exists())
        self.assertFalse(Contract.sources.through.objects.filter(
            contract_id=self.contract.pk,
        ).exists())
        self.assertFalse(Source._base_manager.get(pk=source.pk).active)

    def test_redirects_to_first_active_source(self):
        self.create_source('First active source')
        self.create_source('Deactivated source', active=False)
        self.create_source('Second active source')
        first_active = self.contract.sources.first()

        response = self.delete_contract()

        self.assertRedirects(
            response, first_active.get_absolute_url(), fetch_redirect_response=False,
        )
        self.assertFalse(Contract.objects.filter(pk=self.contract.pk).exists())
        self.assertTrue(Source.objects.filter(pk=first_active.pk).exists())

    def test_preserves_numbered_contract(self):
        Contract.objects.filter(pk=self.contract.pk).update(contract_number=730)

        response = self.delete_contract(follow=True)

        self.assertRedirects(response, self.detail_url)
        self.assertContains(response, 'delete contract with number')
        self.assert_contract_exists()

    def test_preserves_contract_with_inactive_subcontract(self):
        child = Contract.objects.create(
            publisher=self.publisher, parent_contract=self.contract, active=False,
        )

        response = self.delete_contract(follow=True)

        self.assertRedirects(response, self.detail_url)
        self.assertContains(response, 'This contract has subcontracts or negotiation emails')
        self.assert_contract_exists()
        child.refresh_from_db()
        self.assertEqual(child.parent_contract_id, self.contract.pk)

    def test_preserves_contract_with_waiting_or_sent_negotiation_email(self):
        for sent in (False, True):
            with self.subTest(sent=sent):
                email = EmailNegotiation.objects.create(
                    contract=self.contract, sent=sent, scheduled_date=date.today(),
                    to_email='publisher@example.invalid',
                )

                response = self.delete_contract(follow=True)

                self.assertRedirects(response, self.detail_url)
                self.assertContains(response, 'This contract has subcontracts or negotiation emails')
                self.assert_contract_exists()
                email.refresh_from_db()
                self.assertEqual(email.contract_id, self.contract.pk)
                self.assertEqual(email.sent, sent)
                email.delete()

    def test_does_not_treat_self_reference_as_a_subcontract(self):
        Contract.objects.filter(pk=self.contract.pk).update(
            parent_contract_id=self.contract.pk,
        )

        response = self.delete_contract()

        self.assertRedirects(response, self.list_url, fetch_redirect_response=False)
        self.assertFalse(Contract.objects.filter(pk=self.contract.pk).exists())

    def test_requires_login_even_with_valid_csrf(self):
        self.client.logout()

        response = self.delete_contract()

        login_url = '{}?next={}'.format(reverse('login'), self.delete_url)
        self.assertRedirects(response, login_url, fetch_redirect_response=False)
        self.assert_contract_exists()

    def test_rejects_post_without_csrf(self):
        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 403)
        self.assert_contract_exists()

    def test_get_does_not_delete_contract(self):
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 405)
        self.assert_contract_exists()

    def test_repeated_post_returns_not_found(self):
        self.assertEqual(self.delete_contract().status_code, 302)

        self.assertEqual(self.delete_contract().status_code, 404)
