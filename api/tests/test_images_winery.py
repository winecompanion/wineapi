from django.core.files.base import ContentFile

from api.serializers import FileSerializer


class TestImagesWinary():
    def setUp(self):
        file_test = ContentFile(b"Some file content")
        file_test.name = 'myfile.jpg'
        self.valid_file = file_test
        self.valid_images_simple_upload_data = {
                'id': 1,
                'filefield': [self.valid_file],
                }
        self.valid_images_multi_upload_data = {
                'id': 1,
                'filefield': [self.valid_file, self.valid_file, self.valid_file],
                }
        self.invalid_images_simple_upload_data_without_dict = {
                'id': 1,
                'filefield': self.valid_file,
                }

        self.invalid_images_simple_upload_data_without_id = {
                'filefield': [self.valid_file],
                }

    def test_file_serializer_simple_upload(self):
        serializer = FileSerializer(data=self.valid_images_simple_upload_data)
        self.assertTrue(serializer.is_valid())
        upload_fields = ['id', 'filefield']
        self.assertEqual(set(serializer.data.keys()), set(upload_fields))

    def test_file_serializer_multi_upload(self):
        serializer = FileSerializer(data=self.valid_images_multi_upload_data)
        self.assertTrue(serializer.is_valid())
        upload_fields = ['id', 'filefield']
        self.assertEqual(set(serializer.data.keys()), set(upload_fields))

    def test_invalid_file_serializer_without_dict(self):
        serializer = FileSerializer(data=self.invalid_images_simple_upload_data_without_dict)
        self.assertFalse(serializer.is_valid())

    def test_invalid_file_serializer_without_id(self):
        serializer = FileSerializer(data=self.invalid_images_simple_upload_data_without_id)
        self.assertFalse(serializer.is_valid())
        upload_id_field = {'id'}
        self.assertEqual(set(serializer.errors), upload_id_field)
