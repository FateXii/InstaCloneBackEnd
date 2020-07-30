from django.urls import reverse
from userprofile.models import Profile


def login(client, username, password):
    url = reverse('login')
    user_details = {
        'username': username,
        'password': password
    }

    return client.post(url, user_details, format='json')


def get_profile(username):
    return Profile.objects.get(
        user__username=username
    )


def get_user_token(username):
    return get_profile(username).user.auth_token.key


def set_auth_header(client, username=None):
    if not username:
        client.credentials()
    else:
        client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(
                get_user_token(username)
            ))


def set_auth(client, username=None):
    if not username:
        client.credentials()
    else:
        client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(
                get_user_token(username)
            ))
