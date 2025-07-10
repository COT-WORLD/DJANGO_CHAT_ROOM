import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client
from chat.forms import UserForm
from chat.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
UserModel = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        user = UserModel.objects.create_user(
            username="johndoe",
            email="john@example.com",
            password="securepassword123"
        )
        assert user.email == "john@example.com"
        assert user.check_password("securepassword123")

    def test_unique_email(self):
        UserModel.objects.create_user(
            username="user1", email="unique@example.com", password="pass")
        with pytest.raises(Exception):
            UserModel.objects.create_user(
                username="user2", email="unique@example.com", password="pass")

    def test_username_field_is_email(self):
        assert UserModel.USERNAME_FIELD == "email"

    def test_user_avatar_and_bio(self):
        user = UserModel.objects.create_user(
            username="bioavatar",
            email="ba@example.com",
            password="pass",
            bio="Hello <script>alert('XSS')</script> world!"
        )
        assert "script" in user.bio


@pytest.mark.django_db
class TestUserForm:

    def test_valid_user_form(self):
        avatar_file = SimpleUploadedFile(
            "avatar.png", b"imagecontent", content_type="image/png")
        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "bio": "<b>Hello</b>"
        }
        form = UserForm(data=form_data, files={"avatar": avatar_file})
        assert form.is_valid()

    def test_avatar_size_validation(self):
        large_file = SimpleUploadedFile(
            "large.png", b"a" * (2 * 1024 * 1024 + 1), content_type="image/png")
        form_data = {"email": "avatar@big.com"}
        form = UserForm(data=form_data, files={"avatar": large_file})
        assert not form.is_valid()
        assert "avatar" in form.errors

    def test_avatar_type_validation(self):
        invalid_file = SimpleUploadedFile(
            "file.txt", b"textcontent", content_type="text/plain")
        form = UserForm(data={"email": "bad@type.com"},
                        files={"avatar": invalid_file})
        assert not form.is_valid()
        assert "avatar" in form.errors

    def test_bio_is_sanitized(self):
        form = UserForm(data={
            "email": "clean@bio.com",
            "bio": '<script>alert("XSS")</script><b>bold</b>'
        })
        form.is_valid()
        cleaned_bio = form.clean_bio()
        assert "<script>" not in cleaned_bio
        assert "<b>" in cleaned_bio


@pytest.mark.django_db
class TestUserViews:

    def setup_method(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="testpassword"
        )

    def test_update_user_get_authenticated(self):
        self.client.login(email="tester@example.com", password="testpassword")
        response = self.client.get(reverse("update-user"), secure=True)
        assert response.status_code == 200
        assert "form" in response.context

    def test_update_user_post_valid(self):
        self.client.login(email="tester@example.com", password="testpassword")

        avatar_file = SimpleUploadedFile(
            name="avatar.png",
            content=b"fakeimagedata",
            content_type="image/png"
        )

        data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "tester@example.com",
            "bio": "<p>Updated bio</p>",
        }

        response = self.client.post(
            reverse("update-user"),
            data,
            format="multipart",
            files={"avatar": avatar_file}, secure=True
        )

        self.user.refresh_from_db()
        assert response.status_code == 302
        assert self.user.first_name == "Updated"

    def test_update_user_post_invalid(self):
        self.client.login(email="tester@example.com", password="testpassword")
        data = {
            "first_name": "",
            "last_name": "",
            "email": "bad-email"
        }
        response = self.client.post(reverse("update-user"), data, secure=True)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_profile_view_authenticated(self):
        self.client.login(email="tester@example.com", password="testpassword")
        response = self.client.get(
            reverse("user-profile", args=[self.user.pk]), secure=True)
        assert response.status_code == 200
        assert "user" in response.context
        assert response.context["user"].email == "tester@example.com"

    def test_update_requires_authentication(self):
        response = self.client.get(reverse("update-user"), secure=True)
        assert response.status_code == 302


@pytest.mark.django_db
class TestUserWorkflow:

    def test_signup_login_update_logout_flow(self, client):
        user = UserModel.objects.create_user(
            username="workflow",
            email="flow@example.com",
            password="flowpass"
        )

        login = client.login(email="flow@example.com", password="flowpass")
        assert login is True

        response = client.get(reverse("update-user"), secure=True)
        assert response.status_code == 200

        data = {
            "first_name": "Flow",
            "last_name": "Updated",
            "email": "flow@example.com",
            "bio": "Clean <script>alert(1)</script>"
        }
        client.post(reverse("update-user"), data, secure=True)
        user.refresh_from_db()
        assert user.first_name == "Flow"

        response = client.get(reverse("logout"), secure=True)
        assert response.status_code == 302
        assert response.url == reverse("home")
