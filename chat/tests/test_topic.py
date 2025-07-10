import pytest
from django.urls import reverse
from chat.models import Topic, User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestTopicModel:
    def test_create_topic(self):
        topic = Topic.objects.create(name="Django Testing")
        assert topic.name == "Django Testing"
        assert topic.created_at is not None
        assert topic.updated_at is not None

    def test_topic_str_representation(self):
        topic = Topic.objects.create(name="APIs")
        assert str(topic) == "APIs"

    def test_topic_name_index_exists(self):
        index_fields = [index.fields for index in Topic._meta.indexes]
        assert ['name'] in index_fields

    def test_blank_topic_name_raises_error(self):
        with pytest.raises(ValidationError):
            topic = Topic(name="")
            topic.full_clean()

    def test_duplicate_topic_name_allowed(self):
        Topic.objects.create(name="Duplicate")
        Topic.objects.create(name="Duplicate")
        assert Topic.objects.filter(name="Duplicate").count() == 2


@pytest.mark.django_db
class TestTopicViews:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(email="testuser@example.com", password="testpassword")
        return client

    @pytest.fixture
    def topics(self):
        return [
            Topic.objects.create(name="Python"),
            Topic.objects.create(name="Django"),
            Topic.objects.create(name="Pytest"),
        ]

    def test_topics_page_displays_all(self, client, topics):
        url = reverse("topics")
        response = client.get(url, secure=True)
        assert response.status_code == 200
        for topic in topics:
            assert topic.name in response.content.decode()

    def test_topics_page_filtered_by_query(self, client):
        Topic.objects.create(name="Machine Learning")
        Topic.objects.create(name="Deep Learning")

        response = client.get(reverse("topics"), {"q": "Deep"}, secure=True)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Deep Learning" in content
        assert "Machine Learning" not in content


@pytest.mark.django_db
class TestTopicWorkflow:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="hostuser",
            email="host@example.com",
            password="hostpass"
        )

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(email="host@example.com", password="hostpass")
        return client

    def test_topic_is_created_via_create_room(self, client_logged_in):
        url = reverse("create-room")
        response = client_logged_in.post(url, {
            "name": "New Room",
            "description": "This is a test room.",
            "topic": "Test Topic"
        }, secure=True)
        assert response.status_code in [301, 302]
        assert Topic.objects.filter(name="Test Topic").exists()

    def test_existing_topic_is_reused(self, client_logged_in):
        Topic.objects.create(name="Existing Topic")

        response = client_logged_in.post(reverse("create-room"), {
            "name": "Another Room",
            "description": "Reusing a topic",
            "topic": "Existing Topic"
        }, secure=True)

        assert response.status_code in [301, 302]
        assert Topic.objects.filter(name="Existing Topic").count() == 1

    def test_topic_editable_via_update_room(self, client_logged_in):
        topic = Topic.objects.create(name="Original Topic")
        room_response = client_logged_in.post(reverse("create-room"), {
            "name": "Room to Update",
            "description": "Original description",
            "topic": topic.name
        }, secure=True)

        from chat.models import Room
        room = Room.objects.get(name="Room to Update")

        response = client_logged_in.post(reverse("update-room", args=[room.id]), {
            "name": "Room to Update",
            "description": "Changed description",
            "topic": "Edited Topic"
        }, secure=True)

        assert response.status_code in [301, 302]
        assert Topic.objects.filter(name="Edited Topic").exists()
        assert Topic.objects.filter(name="Original Topic").exists()

    def test_topic_deletion_model_only(self):
        topic = Topic.objects.create(name="Temporary Topic")
        topic.delete()
        assert not Topic.objects.filter(name="Temporary Topic").exists()
