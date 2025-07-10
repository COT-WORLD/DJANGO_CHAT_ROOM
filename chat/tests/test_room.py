import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from chat.models import Room, Topic, User
from chat.forms import RoomForm
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestRoomModel:
    def test_room_creation_and_str(self):
        user = User.objects.create_user(
            email="a@test.com", username="a", password="pass")
        topic = Topic.objects.create(name="TestTopic")
        room = Room.objects.create(
            name="Test Room",
            host=user,
            topic=topic,
            description="Test description"
        )
        assert str(room) == "Test Room"
        assert room.created_at is not None
        assert room.updated_at is not None

    def test_participant_relation(self):
        user = User.objects.create_user(
            email="b@test.com", username="b", password="pass")
        topic = Topic.objects.create(name="TestTopic2")
        room = Room.objects.create(name="Test", topic=topic, host=user)
        room.participants.add(user)
        assert room.participants.count() == 1
        assert user in room.participants.all()

    def test_room_model_indexes_exist(self):
        index_fields = [tuple(index.fields) for index in Room._meta.indexes]
        assert ('topic',) in index_fields
        assert ('name',) in index_fields
        assert ('description',) in index_fields


@pytest.mark.django_db
class TestRoomForm:
    def test_valid_form_sanitizes_description(self):
        topic = Topic.objects.create(name="Safe")
        form_data = {
            "name": "Room Title",
            "topic": topic.id,
            "description": "<script>alert('XSS')</script><p>safe</p>",
        }
        form = RoomForm(data=form_data)
        assert form.is_valid()
        cleaned_description = form.clean_description()
        assert "<script>" not in cleaned_description
        assert "<p>safe</p>" in cleaned_description

    def test_invalid_form_missing_name(self):
        topic = Topic.objects.create(name="Missing Name Topic")
        form_data = {
            "name": "",
            "topic": topic.id,
            "description": "Missing name",
        }
        form = RoomForm(data=form_data)
        assert not form.is_valid()


@pytest.mark.django_db
class TestRoomViews:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="host", email="host@test.com", password="testpass")

    @pytest.fixture
    def topic(self):
        return Topic.objects.create(name="General")

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(email="host@test.com", password="testpass")
        return client

    def test_create_room_view_get(self, client_logged_in):
        response = client_logged_in.get(reverse("create-room"), secure=True)
        assert response.status_code == 200
        assert "form" in response.context

    def test_create_room_view_post(self, client_logged_in):
        response = client_logged_in.post(reverse("create-room"), {
            "name": "New Room",
            "description": "This is a new room",
            "topic": "NewTopic"
        }, secure=True)
        assert response.status_code in [302, 301]
        assert Room.objects.filter(name="New Room").exists()
        assert Topic.objects.filter(name="NewTopic").exists()

    def test_update_room_view_get_and_post(self, client_logged_in, user, topic):
        room = Room.objects.create(name="Edit Room", host=user, topic=topic)
        url = reverse("update-room", args=[room.id])

        response = client_logged_in.get(url, secure=True)
        assert response.status_code == 200
        assert "form" in response.context

        response = client_logged_in.post(url, {
            "name": "Edited Room",
            "description": "Updated desc",
            "topic": "UpdatedTopic"
        }, secure=True)
        assert response.status_code in [302, 301]
        room.refresh_from_db()
        assert room.name == "Edited Room"
        assert room.topic.name == "UpdatedTopic"

    def test_update_room_forbidden_for_non_host(self, client, topic, user):
        other_user = User.objects.create_user(
            email="other@test.com", username="other", password="1234")
        room = Room.objects.create(name="Room", host=user, topic=topic)

        client.login(email="other@test.com", password="1234")
        response = client.post(reverse("update-room", args=[room.id]), {
            "name": "Hacked Room",
            "description": "Nope",
            "topic": "BadTopic"
        }, secure=True)
        assert response.status_code == 403

    def test_delete_room_authorized(self, client_logged_in, user, topic):
        room = Room.objects.create(name="Delete Room", host=user, topic=topic)
        response = client_logged_in.post(
            reverse("delete-room", args=[room.id]), secure=True)
        assert response.status_code in [302, 301]
        assert not Room.objects.filter(id=room.id).exists()

    def test_delete_room_unauthorized(self, client, topic, user):
        attacker = User.objects.create_user(
            email="attacker@test.com", username="attacker", password="hackme")
        room = Room.objects.create(name="Secure Room", host=user, topic=topic)

        client.login(email="attacker@test.com", password="hackme")
        response = client.post(
            reverse("delete-room", args=[room.id]), secure=True)
        assert response.status_code == 403
        assert Room.objects.filter(id=room.id).exists()

    def test_room_view_adds_participant_and_sanitizes_message(self, client_logged_in, user, topic):
        room = Room.objects.create(name="Chat Room", host=user, topic=topic)

        response = client_logged_in.post(reverse("room", args=[room.id]), {
            "body": "<script>alert(1)</script><p>hello</p>"
        }, secure=True)

        assert response.status_code in [302, 301]
        room.refresh_from_db()
        assert user in room.participants.all()
        assert room.message_set.count() == 1
        message = room.message_set.first()
        assert "<script>" not in message.body
        assert "<p>hello</p>" in message.body

    def test_room_view_get(self, client_logged_in, user, topic):
        room = Room.objects.create(
            name="Viewable Room", host=user, topic=topic)
        response = client_logged_in.get(
            reverse("room", args=[room.id]), secure=True)
        assert response.status_code == 200
        assert "room" in response.context
