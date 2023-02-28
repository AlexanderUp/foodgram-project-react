from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TestUserAPI(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_credentials = {
            "username": "test",
            "email": "test@example.com",
            "first_name": "test",
            "last_name": "test",
            "password": "qwerty1990",
        }
        cls.user = User.objects.create_user(  # type:ignore
            **cls.user_credentials)
        token_obj, _ = Token.objects.get_or_create(user=cls.user)
        cls.token = token_obj.key

    def setUp(self):
        headers = {"HTTP_AUTHORIZATION": f"Token {TestUserAPI.token}"}
        self.guest_user = APIClient()
        self.auth_user = APIClient()
        self.auth_user.credentials(**headers)

    def testUserList(self):
        for client in (self.guest_user, self.auth_user):
            with self.subTest(client=client):
                response = client.get("/api/users/")
                self.assertEqual(response.status_code,  # type:ignore
                                 status.HTTP_200_OK)

    def testUserCreation(self):
        new_user_data_template = {
            "username": "test_test_{index}",
            "email": "test_test_{index}@example.com",
            "first_name": "test_test_{index}",
            "last_name": "test_test_{index}",
            "password": "test_test_{index}",
        }
        url = "/api/users/"
        initial_user_count = User.objects.count()
        for index, client in enumerate((self.auth_user, self.guest_user)):
            with self.subTest(index=index, client=client, url=url):
                new_user_data = {}
                for key, value in new_user_data_template.items():
                    new_user_data[key] = value.format(index=index)
                response = client.post(url, {**new_user_data}, format="json")
                self.assertEqual(response.status_code,  # type:ignore
                                 status.HTTP_201_CREATED)
                self.assertNotEqual(initial_user_count, User.objects.count())
                new_user_data.pop("first_name")
                response = client.post(url, {**new_user_data}, format="json")
                self.assertEqual(response.status_code,  # type:ignore
                                 status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), initial_user_count + 2)

    def testUserDetail(self):
        another_user = User.objects.create_user(  # type:ignore
            username="test2",
            email="test2@example.com",
            first_name="test2",
            last_name="test2",
            password="qwerty1990"
        )
        url = f"/api/users/{another_user.pk}/"
        guest_response = self.guest_user.get(url)
        self.assertEqual(guest_response.status_code,  # type:ignore
                         status.HTTP_401_UNAUTHORIZED)
        auth_response = self.auth_user.get(url)
        self.assertEqual(auth_response.status_code,  # type:ignore
                         status.HTTP_200_OK)
        unexisted_url = "/api/users/100000/"
        guest_unexisted_url_response = self.guest_user.get(unexisted_url)
        self.assertEqual(
            guest_unexisted_url_response.status_code,  # type:ignore
            status.HTTP_401_UNAUTHORIZED)
        auth_user_unexisted_url_response = self.auth_user.get(unexisted_url)
        self.assertEqual(
            auth_user_unexisted_url_response.status_code,  # type:ignore
            status.HTTP_404_NOT_FOUND)

    def testCurrentUserDetail(self):
        url = "/api/users/me/"
        guest_response = self.guest_user.get(url)
        self.assertEqual(guest_response.status_code,  # type:ignore
                         status.HTTP_401_UNAUTHORIZED)
        auth_response = self.auth_user.get(url)
        self.assertEqual(auth_response.status_code,  # type:ignore
                         status.HTTP_200_OK)

    def testPasswordChange(self):
        url = "/api/users/set_password/"
        current_password = "qwerty1990"
        new_password = "1990qwerty1990"
        password_data = {
            "current_password": current_password,
            "new_password": new_password,
        }
        guest_response = self.guest_user.post(
            url, {**password_data}, format="json")
        self.assertEqual(guest_response.status_code,  # type:ignore
                         status.HTTP_401_UNAUTHORIZED)
        auth_response = self.auth_user.post(
            url, {**password_data}, format="json")
        self.assertEqual(auth_response.status_code,  # type:ignore
                         status.HTTP_204_NO_CONTENT)
        auth_response = self.auth_user.post(
            url, {"current_password": new_password,
                  "new_password": current_password},
            format="json"
        )
        self.assertEqual(auth_response.status_code,  # type:ignore
                         status.HTTP_204_NO_CONTENT)
        password_data.pop("current_password")
        auth_incomplete_data_response = self.auth_user.post(
            url, {**password_data}, format="json")
        self.assertEqual(
            auth_incomplete_data_response.status_code,  # type:ignore
            status.HTTP_400_BAD_REQUEST)

    def testLogin(self):
        url = "/api/auth/token/login/"
        credentials = {
            "email": TestUserAPI.user_credentials.get("email"),
            "password": TestUserAPI.user_credentials.get("password"),
        }
        Token.objects.all().delete()
        self.assertEqual(Token.objects.count(), 0)
        guest_response = self.guest_user.post(
            url, {**credentials}, format="json")
        self.assertEqual(
            guest_response.status_code, status.HTTP_201_CREATED)  # type:ignore
        self.assertEqual(Token.objects.count(), 1)

        token = guest_response.json().get("auth_token")  # type:ignore
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        self.guest_user.credentials(**headers)
        guest_auth_response = self.guest_user.post(
            url, {**credentials}, format="json")
        self.assertEqual(guest_auth_response.status_code,  # type:ignore
                         status.HTTP_201_CREATED)

    def testLogout(self):
        url = "/api/auth/token/logout/"
        guest_response = self.guest_user.post(url)
        self.assertEqual(guest_response.status_code,  # type:ignore
                         status.HTTP_401_UNAUTHORIZED)
        auth_response = self.auth_user.post(url)
        self.assertEqual(
            auth_response.status_code,  # type:ignore
            status.HTTP_204_NO_CONTENT)
