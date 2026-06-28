from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from classes.models import ClassStruct
from ..models import Prod


class ProdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.main_class = ClassStruct.objects.create(
            name="main_class",
            short_name="main_cl",
            base_ei=None,
            main_class=None,
        )

    def test_create_with_minimal_requirements(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertIsNotNone(prod.pk)

    def test_string_representation(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertEqual(str(prod), "test")

    def test_image_field_path(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertTrue(prod.image.name.startswith("product_images/"))

    def test_class_field_relation(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertEqual(prod.class_field, self.main_class)
        self.assertIn(prod, self.main_class.class_products.all())
