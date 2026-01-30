from __future__ import annotations

from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class DjRestAuthOAuth2Client(OAuth2Client):
    """Compatibility shim for dj-rest-auth + django-allauth.

    dj-rest-auth's SocialLoginSerializer calls client_class with:
        (request, client_id, secret, method, token_url, callback_url, scope,
         scope_delimiter=..., headers=..., basic_auth=...)

    Newer django-allauth OAuth2Client.__init__ signature does NOT accept a
    positional `scope` argument, which results in:
        TypeError: got multiple values for argument 'scope_delimiter'

    This subclass accepts `scope` positionally and forwards the correct args to
    django-allauth's OAuth2Client.
    """

    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        scope=None,
        *,
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
        **kwargs,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter=scope_delimiter,
            headers=headers,
            basic_auth=basic_auth,
        )
