import pytest
from django.urls import reverse
from chat.models import User, Room, Message
from django.utils.html import escape
from django.middleware.csrf import CsrfViewMiddleware
from django.test import RequestFactory
from chat.views import room_view
from django.http import HttpResponseForbidden


def apply_csrf_middleware(view_func, request, *args, **kwargs):
    """Utility to simulate Django CSRF middleware behavior."""
    middleware = CsrfViewMiddleware(lambda r: view_func(r, *args, **kwargs))
    return middleware.process_view(request, view_func, args, kwargs)


@pytest.mark.django_db
class TestSecurity:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="secureuser", email="secure@example.com", password="securepass")

    @pytest.fixture
    def other_user(self):
        return User.objects.create_user(username="attacker", email="attacker@example.com", password="hackerpass")

    @pytest.fixture
    def room(self, user):
        return Room.objects.create(name="Secure Room", host=user)

    @pytest.fixture
    def client_logged_in(self, client, user):
        client.login(email=user.email, password="securepass")
        return client

    def test_sql_injection_like_input_stored_as_text(self, client_logged_in, room, user):
        malicious_input = "' OR 1=1 --"
        response = client_logged_in.post(reverse("room", args=[room.id]), {
                                         "body": malicious_input}, secure=True)
        assert response.status_code in [301, 302]
        assert Message.objects.filter(body__icontains="OR 1=1").exists()

    def test_xss_is_sanitized_by_bleach(self, client_logged_in, room):
        xss_input = "<script>alert('XSS')</script><b>Bold</b>"
        client_logged_in.post(
            reverse("room", args=[room.id]), {"body": xss_input}, secure=True)
        message = Message.objects.latest('created_at')
        assert "<script>" not in message.body
        assert "<b>Bold</b>" in message.body

    def test_csrf_protection_enforced(self, room, user):
        factory = RequestFactory()
        request = factory.post(
            f"/room/{room.id}/", {"body": "CSRF test"}, secure=True)
        request.user = user

        response = apply_csrf_middleware(room_view, request, pk=room.id)

        assert isinstance(response, HttpResponseForbidden)
        assert response.status_code == 403

    def test_broken_access_control_prevented(self, client, other_user, user, room):
        client.login(email=other_user.email, password="hackerpass")
        response = client.post(
            reverse("delete-room", args=[room.id]), secure=True)
        assert response.status_code == 403

    def test_security_headers_present(self, client, room, user):
        client.login(email=user.email, password="securepass")
        url = reverse("room", args=[room.id])

        response = client.get(url, secure=True)
        assert response.headers.get(
            "X-Frame-Options") in ["DENY", "SAMEORIGIN"]
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert "Strict-Transport-Security" in response.headers

    def test_no_sensitive_info_leaked_in_response(self, client_logged_in, room):
        response = client_logged_in.get(
            reverse("room", args=[room.id]), secure=True)
        content = response.content.decode()
        assert "password" not in content
        assert "secret" not in content
        assert "Authorization" not in content

    # def test_redirect_with_next_param_not_open_redirect(self, client, user):
    #     client.login(email=user.email, password="securepass")

    #     response = client.get(reverse('account_login') +
    #                           '?next=http://evil.com', secure=True)

    #     assert response.status_code in [302, 301]

    #     assert "evil.com" not in response.headers.get("Location", "")
    #     assert "evil.com" not in response.content.decode()

    #     response = client.get(reverse('account_login'))
    #     assert response.status_code in [302, 301]
    #     assert response.url == '/'
