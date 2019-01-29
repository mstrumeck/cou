from django import test


class SocialTestHelper(test.TestCase):
    def save_all_ob_from(self, data):
        for i in data:
            i.save()
