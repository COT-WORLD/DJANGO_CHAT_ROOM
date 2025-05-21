import pytest
from django.urls import reverse
from chat.models import User, Topic, Room, Message
from django.utils.html import escape


@pytest.mark.django_db
class TestMessageModel:
    def test_message_creation_and_str(self):
        user = User.objects.create_user(
            username="msguser", email="msg@example.com", password="testpass")
        topic = Topic.objects.create(name="General")
        room = Room.objects.create(name="Message Room", topic=topic, host=user)

        message = Message.objects.create(
            user=user, room=room, body="Hello, world!")
        assert str(message) == "Hello, world!"
        assert message.created_at is not None
        assert message.updated_at is not None

    def test_message_ordering_latest_first(self):
        user = User.objects.create_user(
            username="orderuser", email="order@example.com", password="testpass")
        topic = Topic.objects.create(name="OrderTopic")
        room = Room.objects.create(name="OrderRoom", topic=topic, host=user)

        msg1 = Message.objects.create(user=user, room=room, body="First")
        msg2 = Message.objects.create(user=user, room=room, body="Second")

        messages = list(Message.objects.all())
        assert messages[0] == msg2
        assert messages[1] == msg1

    def test_model_indexes(self):
        fields = [tuple(index.fields) for index in Message._meta.indexes]
        assert ("room_id",) in fields
        assert ("created_at",) in fields


@pytest.mark.django_db
class TestMessageViews:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="user1", email="user1@example.com", password="testpass")

    @pytest.fixture
    def other_user(self):
        return User.objects.create_user(username="user2", email="user2@example.com", password="testpass")

    @pytest.fixture
    def topic(self):
        return Topic.objects.create(name="TopicForMessages")

    @pytest.fixture
    def room(self, user, topic):
        return Room.objects.create(name="Room For Messages", host=user, topic=topic)

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(email="user1@example.com", password="testpass")
        return client

    def test_post_message_sanitized_and_added(self, client_logged_in, room, user):
        url = reverse("room", args=[room.id])
        response = client_logged_in.post(url, {
            "body": "<script>alert('x')</script><p>Hello there!</p>"
        }, secure=True)
        assert response.status_code in [302, 301]
        message = Message.objects.filter(room=room).first()
        assert "<script>" not in message.body
        assert "<p>Hello there!</p>" in message.body
        assert user in room.participants.all()

    def test_post_empty_message_does_not_create(self, client_logged_in, room):
        response = client_logged_in.post(reverse("room", args=[room.id]), {
            "body": ""
        }, secure=True)
        assert response.status_code in [302, 301]
        assert Message.objects.filter(room=room).count() == 0

    def test_delete_message_by_owner(self, client_logged_in, room, user):
        message = Message.objects.create(
            user=user, room=room, body="Deletable message")
        response = client_logged_in.post(
            reverse("delete-message", args=[message.id]), secure=True)
        assert response.status_code in [302, 301]
        assert not Message.objects.filter(id=message.id).exists()

    def test_delete_message_by_other_user_forbidden(self, client, other_user, user, room):
        message = Message.objects.create(
            user=user, room=room, body="Should not delete")

        client.login(email="user2@example.com", password="testpass")
        response = client.post(
            reverse("delete-message", args=[message.id]), secure=True)
        assert response.status_code == 403
        assert Message.objects.filter(id=message.id).exists()

    def test_room_view_message_rendering(self, client_logged_in, room, user):
        Message.objects.create(user=user, room=room, body="Displayed message")
        response = client_logged_in.get(
            reverse("room", args=[room.id]), secure=True)
        assert response.status_code == 200
        assert "Displayed message" in response.content.decode()
