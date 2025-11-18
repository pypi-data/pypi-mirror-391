import logging
from urllib.parse import urlparse

from requests import Session, Response

from zapp.features.core.sessions import AuthSession, assert_http_status, soup

log = logging.getLogger(__name__)


class KeyCloakFrontSession(AuthSession):
    """Сессия для работы с API UI при авторизации через KeyCloak"""

    def _parse_login_url(self, response: Response) -> str:
        bs = soup(response.text)
        kc_login_form = bs.select_one("#kc-form-login")
        if not kc_login_form:
            raise AttributeError(
                "Форма логина KeyCloak должна присутствовать на странице"
            )

        url = kc_login_form.attrs["action"]
        if url.startswith("/"):
            base_url = urlparse(response.url)
            url = f"{base_url.scheme}://{base_url.netloc}{url}"
        return url

    def _login(
        self,
        response: Response,
        username: str,
        password: str,
        allow_redirects: bool,
    ) -> Session:
        login_url = self._parse_login_url(response)
        login_data = {
            "username": username,
            "password": password,
            "credentialId": "",
        }
        login_response = self.session.post(
            login_url, data=login_data, allow_redirects=allow_redirects
        )
        assert_http_status(login_response)
