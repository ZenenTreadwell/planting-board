from django.urls import reverse, resolve
from django.test import TestCase
from django.contrib.auth.models import User

from ..views import home, board_topics, new_topic
from ..models import Board, Topic, Post
from ..forms import NewTopicForm

class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name="Django", description='Django board.')
        User.objects.create_user(username='Zen', email="zenen52@gmail.com", password='foo')
        self.client.login(username='Zen', password='foo')

    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={"pk":1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={"pk": 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_has_link_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        self.assertContains(response,'href="{0}"'.format(board_topics_url))

    def csrf_token(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': "Molerat Buttholes",
            'message': "More common than you think!"
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        # Upon submitting with no valid data, show the form again
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data(self):
        # Upon submitting with no valid data, show the form again
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {}
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_empty_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': "",
            'message': ""
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name="Django", description='Django board.')
        self.url = reverse('new_topic', kwargs={"pk": 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
