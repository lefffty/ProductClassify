from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from urllib.parse import quote
from http import HTTPStatus
from faker import Faker

from tests.unit.base import BaseUnitTestCase

from classes.models import ClassStruct
from classes.constants import ProductsConsts, ProdClassConsts

from accounts.models import Role
from accounts.constants import UserConsts, RoleCodes

from ei.models import Ei

from products.models import Prod
from products.constants import ProdConsts

from specifications.views import ProdComponentFormSet
from specifications.models import ProdComponent, SpecificationLogs

User = get_user_model()


class GetTotalCostRatioViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.parent_prod,
            component=cls.component_prod,
            num=1,
            quantity=200,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.BUILDER)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_USER)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.url = reverse("specifications:total_cost_ratio", args=[cls.parent_prod.pk])

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_content_type(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )

    def test_filename(self):
        self.client.force_login(self.allowed_user)
        filename = f"Спецификация_изделия_{self.parent_prod.name}.pdf"
        encoded_filename = quote(filename, safe="")
        response = self.client.get(self.url)
        self.assertIn(
            f"filename*=utf-8''{encoded_filename}",
            response["Content-Disposition"]
        )


class GetProductChangelogViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.parent_prod,
            component=cls.component_prod,
            num=1,
            quantity=200,
        )
        cls.log = SpecificationLogs.objects.create(
            pair=cls.prodcomponent,
            old_quantity=100,
            new_quantity=200,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.BUILDER)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_USER)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.url = reverse("specifications:changelog", args=[cls.parent_prod.pk])

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_content_type(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )        

    def test_filename(self):
        self.client.force_login(self.allowed_user)
        filename = f"История_изменений_спецификации_изделия_{self.parent_prod.name}.pdf"
        encoded_filename = quote(filename, safe="")        
        response = self.client.get(self.url)
        self.assertIn(
            f"filename*=utf-8''{encoded_filename}",
            response["Content-Disposition"]
        )


class EditSpecificationViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.another_component = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.parent_prod,
            component=cls.component_prod,
            num=1,
            quantity=200,
        )

        cls.prefix_name = ProdComponentFormSet.get_default_prefix()

        cls.allowed_role = Role.objects.get(code=RoleCodes.BUILDER)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_USER)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.url = reverse("specifications:edit", args=[cls.parent_prod.pk])
        cls.invalid_url = reverse("specifications:edit", args=[9999])
        cls.redirect_url = reverse("products:detail", args=[cls.parent_prod.pk])

    def _get_form_data(self, total_forms, initial_forms, forms_data):
        """
        Вспомогательный метод для сборки данных формы с правильным префиксом.
        """
        data = {
            f'{self.prefix_name}-TOTAL_FORMS': total_forms,
            f'{self.prefix_name}-INITIAL_FORMS': initial_forms,
            f'{self.prefix_name}-MIN_NUM_FORMS': 0,
            f'{self.prefix_name}-MAX_NUM_FORMS': 1000,
        }
        for idx, form_data in enumerate(forms_data):
            for key, value in form_data.items():
                data[f'{self.prefix_name}-{idx}-{key}'] = value
        return data

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_returns_not_found_error_is_product_is_invalid(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_renders_prodcomponent_edit_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/prodcomponent_edit.html")

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_has_product_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("product", response.context)

    def test_has_edit_mode_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("edit_mode", response.context)

    def test_edit_mode_is_false(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("edit_mode"), False)

    def test_edit_mode_is_true(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url, data={"edit": "1"})
        self.assertEqual(response.context.get("edit_mode"), True)

    def test_renders_formset(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url, data={"edit": "1"})
        self.assertIn("formset", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        initial_count = ProdComponent.objects.count()
        initial_log_count = SpecificationLogs.objects.count()

        forms_data = [
            {
                'id': self.prodcomponent.pk,
                'component': self.component_prod.pk,
                'quantity': 999,
                'DELETE': '',
            }
        ]

        data = self._get_form_data(total_forms=1, initial_forms=1, forms_data=forms_data)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(ProdComponent.objects.count(), initial_count)

        self.prodcomponent.refresh_from_db()
        self.assertEqual(self.prodcomponent.quantity, 999)

        self.assertEqual(SpecificationLogs.objects.count(), initial_log_count + 1)
        log = SpecificationLogs.objects.latest('updated_at')
        self.assertEqual(log.pair, self.prodcomponent)
        self.assertEqual(log.old_quantity, 200)
        self.assertEqual(log.new_quantity, 999)


    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        forms_data = [
            {
                'id': self.prodcomponent.pk,
                'component': self.component_prod.pk,
                'quantity': 500,
                'DELETE': '',
            }
        ]
        data = self._get_form_data(total_forms=1, initial_forms=1, forms_data=forms_data)
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, self.redirect_url)

    def test_can_add_new_component(self):
        self.client.force_login(self.allowed_user)
        initial_count = ProdComponent.objects.count()
        forms_data = [
            {
                'id': self.prodcomponent.pk,
                'component': self.component_prod.pk,
                'quantity': 200,
                'DELETE': '',
            },
            {
                'id': '',
                'component': self.another_component.pk,
                'quantity': 50,
                'DELETE': '',
            }
        ]
        data = self._get_form_data(total_forms=2, initial_forms=1, forms_data=forms_data)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProdComponent.objects.count(), initial_count + 1)
        new_component = ProdComponent.objects.exclude(pk=self.prodcomponent.pk).first()
        self.assertEqual(new_component.component, self.another_component)
        self.assertEqual(new_component.quantity, 50)
        log = SpecificationLogs.objects.filter(pair=new_component).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.old_quantity, 0)
        self.assertEqual(log.new_quantity, 50)

    def test_can_delete_existing_component(self):
        self.client.force_login(self.allowed_user)
        initial_count = ProdComponent.objects.count()

        forms_data = [
            {
                'id': self.prodcomponent.pk,
                'component': self.component_prod.pk,
                'quantity': 200,
                'DELETE': 'on',
            }
        ]
        data = self._get_form_data(total_forms=1, initial_forms=1, forms_data=forms_data)

        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, self.redirect_url)

        self.assertEqual(ProdComponent.objects.count(), initial_count - 1)
