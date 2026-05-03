import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.analytics.models import DailyStat
from apps.customers.models import Customer
from apps.ingredients.models import Ingredient
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Recipe


class OrderFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin12345',
        )
        self.client.force_login(self.admin, backend='django.contrib.auth.backends.ModelBackend')

        self.customer = Customer.objects.create(
            name='Customer A',
            phone='0900000001',
        )

        self.ingredient = Ingredient.objects.create(
            name='Coffee Bean',
            unit='g',
            quantity=Decimal('100'),
            min_quantity=Decimal('10'),
            price_per_unit=Decimal('2.5'),
        )

        self.product = Product.objects.create(
            name='Latte',
            price_small=Decimal('30000'),
            price_medium=Decimal('35000'),
            price_large=Decimal('40000'),
            is_available=True,
        )

        Recipe.objects.create(
            product=self.product,
            ingredient=self.ingredient,
            quantity_small=Decimal('2'),
            quantity_medium=Decimal('3'),
            quantity_large=Decimal('4'),
        )

    def test_create_order_rejects_invalid_payment_method(self):
        payload = {
            'customer_id': self.customer.id,
            'items': [
                {
                    'product_id': self.product.id,
                    'size': 'M',
                    'quantity': 1,
                    'customizations': [],
                }
            ],
            'discount': 0,
            'payment_method': 'transfer',
        }

        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.assertIn('Phuong thuc thanh toan khong hop le', response.json().get('message', ''))

    def test_update_order_status_enforces_valid_transition(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('35000'),
            discount=Decimal('0'),
            final_amount=Decimal('35000'),
            status='pending',
            order_date=timezone.now(),
        )

        complete_response = self.client.post(
            reverse('api-update-status', kwargs={'order_id': order.id}),
            data=json.dumps({'status': 'completed'}),
            content_type='application/json',
        )
        self.assertEqual(complete_response.status_code, 200)

        back_response = self.client.post(
            reverse('api-update-status', kwargs={'order_id': order.id}),
            data=json.dumps({'status': 'pending'}),
            content_type='application/json',
        )
        self.assertEqual(back_response.status_code, 400)

    def test_completion_signal_is_applied_once(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('20000'),
            discount=Decimal('0'),
            final_amount=Decimal('20000'),
            status='pending',
            order_date=timezone.now(),
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            size='M',
            quantity=2,
            price=Decimal('10000'),
            customizations=[],
            subtotal=Decimal('20000'),
        )

        order.status = 'completed'
        order.save(update_fields=['status'])

        self.customer.refresh_from_db()
        self.ingredient.refresh_from_db()
        stat = DailyStat.objects.get(stat_date=timezone.localdate(order.order_date))

        self.assertEqual(self.customer.points, 2)
        self.assertEqual(self.ingredient.quantity, Decimal('94'))
        self.assertEqual(stat.total_orders, 1)
        self.assertEqual(stat.total_revenue, Decimal('20000'))

        order.final_amount = Decimal('20000')
        order.save(update_fields=['final_amount'])

        self.customer.refresh_from_db()
        self.ingredient.refresh_from_db()
        stat.refresh_from_db()

        self.assertEqual(self.customer.points, 2)
        self.assertEqual(self.ingredient.quantity, Decimal('94'))
        self.assertEqual(stat.total_orders, 1)
        self.assertEqual(stat.total_revenue, Decimal('20000'))


class OrderStatusPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='staff1',
            email='staff1@example.com',
            password='staff12345',
        )
        self.client.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')

        self.order = Order.objects.create(
            total_amount=Decimal('10000'),
            discount=Decimal('0'),
            final_amount=Decimal('10000'),
            status='pending',
            order_date=timezone.now(),
        )

    def test_non_authorized_user_cannot_update_order_status(self):
        response = self.client.post(
            reverse('api-update-status', kwargs={'order_id': self.order.id}),
            data=json.dumps({'status': 'completed'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
