
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User, Group
from inventory.models import Product
from inventory import views


# Model Tests
class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Product",
            product_id="12345",
            description="A sample product",
            amount=100,
            location="Warehouse 1"
        )
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.name, "Test Product")

    def test_delete_product(self):
        product = Product.objects.create(
            name="Test Product",
            product_id="12345",
            description="A sample product",
            amount=100,
            location="Warehouse 1"
        )
        product_id = product.id
        product.delete()
        self.assertEqual(Product.objects.count(), 0)
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=product_id)


# View Tests
class ProductViewsTest(TestCase):
    def setUp(self):
        self.manager_user = User.objects.create_user(username='manager', password='password')
        self.employee_user = User.objects.create_user(username='employee', password='password')
        self.manager_group = Group.objects.create(name='manager')
        self.employee_group = Group.objects.create(name='employee')
        self.manager_user.groups.add(self.manager_group)
        self.employee_user.groups.add(self.employee_group)

    def test_add_product_manager(self):
        self.client.login(username='manager', password='password')
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 200)

    def test_add_product_employee(self):
        self.client.login(username='employee', password='password') 
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 302)  


# URL Tests
class TestUrls(TestCase):
    def test_add_product_url(self):
        url = reverse('add_product')
        self.assertEqual(resolve(url).func, views.add_product)

    def test_remove_product_url(self):
        url = reverse('remove_product')
        self.assertEqual(resolve(url).func, views.remove_product)

    def test_edit_product_url(self):
        url = reverse('edit_product', args=[1]) 
        self.assertEqual(resolve(url).func, views.edit_product)

    def test_landing_page_url(self):
        url = reverse('landing')
        self.assertEqual(resolve(url).func, views.landing_page)

    def test_dashboard_url(self):
        url = reverse('dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

# Non Functional Tests
# Security Tests
class SecurityTests(TestCase):
    def test_login_required(self):
        url = reverse('add_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_logout_required(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_signup_required(self):
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    
# usability tests
class UsabilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        manager_group = Group.objects.create(name='manager')
        self.user.groups.add(manager_group)
        self.client.login(username='testuser', password='12345')

        self.product = Product.objects.create(
            name="Test Product",
            product_id="12345",
            description="A sample product",
            amount=100,
            location="Warehouse 1"
        )

    def test_add_product_page(self):
        url = reverse('add_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/add_product.html')

    def test_edit_product_page(self):
        url = reverse('edit_product', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/edit_product.html')

    def test_remove_product_page(self):
        url = reverse('remove_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/remove_product.html')