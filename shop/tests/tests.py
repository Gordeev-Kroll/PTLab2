from django.test import Client, TestCase
from django.urls import reverse

from shop.models import Product, PromoCode


class PromoCodeTests(TestCase):
    def setUp(self):
        self.promo = PromoCode.objects.create(code="GAMER")

        self.normal_product = Product.objects.create(
            name="Базовый ноутбук", price=50000
        )

        self.hidden_product = Product.objects.create(
            name="Игровой ПК RTX", price=150000, promo_code=self.promo
        )

        self.client = Client()

    def test_index_without_promo_code(self):
        response = self.client.get(reverse("index"))
        products = response.context["products"]

        self.assertIn(self.normal_product, products)
        self.assertNotIn(self.hidden_product, products)

    def test_index_with_valid_promo_code(self):
        session = self.client.session
        session["promo_code"] = "GAMER"
        session.save()

        response = self.client.get(reverse("index"))
        products = response.context["products"]

        self.assertIn(self.normal_product, products)
        self.assertIn(self.hidden_product, products)

    def test_index_with_invalid_promo_code(self):
        session = self.client.session
        session["promo_code"] = "WRONG"
        session.save()

        response = self.client.get(reverse("index"))
        products = response.context["products"]

        self.assertIn(self.normal_product, products)
        self.assertNotIn(self.hidden_product, products)

    def test_apply_promo_code(self):
        response = self.client.post(reverse("apply_promo"), {"code": "GAMER"})
        self.assertRedirects(response, reverse("index"))

        self.assertEqual(self.client.session.get("promo_code"), "GAMER")

        response = self.client.post(reverse("apply_promo"), {"code": "BADCODE"})
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session.get("promo_code"), "GAMER")

    def test_multiple_promo_codes(self):
            promo_office = PromoCode.objects.create(code="OFFICE")
            office_product = Product.objects.create(
                name="Офисный ноутбук", price=60000, promo_code=promo_office
            )

            self.client.post(reverse("apply_promo"), {"code": "GAMER"})
            response = self.client.get(reverse("index"))
            products = response.context["products"]

            self.assertIn(self.hidden_product, products)
            self.assertNotIn(office_product, products)

            self.client.post(reverse("apply_promo"), {"code": "OFFICE"})
            response = self.client.get(reverse("index"))
            products = response.context["products"]

            self.assertNotIn(self.hidden_product, products)
            self.assertIn(office_product, products)

    def test_promo_code_with_no_products(self):
            PromoCode.objects.create(code="EMPTY")

            self.client.post(reverse("apply_promo"), {"code": "EMPTY"})
            response = self.client.get(reverse("index"))
            products = response.context["products"]

            self.assertIn(self.normal_product, products)
            self.assertNotIn(self.hidden_product, products)