from tests.unit.base import BaseUnitTestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from urllib.parse import quote
from http import HTTPStatus
from faker import Faker

from classes.models import ClassStruct
from classes.constants import ProductsConsts, ProdClassConsts

from ei.models import Ei

from products.models import Prod
from products.constants import ProdConsts

from specifications.views import ProdComponentFormSet
from specifications.models import ProdComponent, SpecificationLogs


class GetTotalCostRatioViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
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

        cls.url = reverse("specifications:total_cost_ratio", args=[cls.parent_prod.pk])

    def test_get_total_cost_ratio_returns_ok_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_total_cost_ratio_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )

    def test_get_total_cost_ratio_filename(self):
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
        cls.fake = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
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

        cls.url = reverse("specifications:changelog", args=[cls.parent_prod.pk])

    def test_get_product_changelog_returns_ok_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_product_changelog_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )        

    def test_get_product_changelog_filename(self):
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
        cls.fake = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.another_component = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
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

        cls.url = reverse("specifications:edit", args=[cls.parent_prod.pk])
        cls.invalid_url = reverse("specifications:edit", args=[404])
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

    def test_edit_specification_view_returns_not_found_error_is_product_is_invalid(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_specification_view_renders_prodcomponent_edit_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/prodcomponent_edit.html")

    def test_edit_specification_view_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_edit_specification_view_has_product_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("product", response.context)

    def test_edit_specification_view_has_edit_mode_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("edit_mode", response.context)

    def test_edit_specification_view_edit_mode_is_false(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("edit_mode"), False)

    def test_edit_specification_view_edit_mode_is_true(self):
        response = self.client.get(self.url, data={"edit": "1"})
        self.assertEqual(response.context.get("edit_mode"), True)

    def test_edit_specification_view_renders_formset(self):
        response = self.client.get(self.url, data={"edit": "1"})
        self.assertIn("formset", response.context)

    def test_edit_specification_view_can_save_a_POST_request(self):
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


    def test_edit_specification_view_redirects_after_POST_request(self):
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

    def test_edit_specification_view_can_add_new_component(self):
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

    def test_edit_specification_view_can_delete_existing_component(self):
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
