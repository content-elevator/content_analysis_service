from django.test import TestCase

# Create your tests here.


class PostTestCase(TestCase):
    def setUp(self):
        self.something = True

    def test_post_is_posted(self):

        self.assertTrue(self.something)