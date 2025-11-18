from behave import step

from zapp.features.core.sessions.keycloak import KeyCloakFrontSession
from zapp.features.core.utils import get_from_variables


@step(
    'API: Я авторизовался через KeyCloak используя УЗ "{username}" и пароль "{password}"'
)
def login_in_keycloak_by_creds_with_redirect(context, username, password):
    open_session(
        context,
        username=username,
        password=password,
        allow_redirects=True,
    )


@step(
    'API: Я авторизовался через KeyCloak используя УЗ "{username}" и пароль "{password}" без редиректа'
)
def login_in_keycloak_by_creds_without_redirect(context, username, password):
    open_session(
        context,
        username=username,
        password=password,
        allow_redirects=False,
    )


@step(
    'API: Я авторизовался через KeyCloak используя значения переменных для УЗ "{username_var}" и пароля "{password_var}"'
)
def login_in_keycloak_by_cred_vars_with_redirect(context, username_var, password_var):
    open_session(
        context,
        username=get_from_variables(username_var),
        password=get_from_variables(password_var),
        allow_redirects=True,
    )


@step(
    'API: Я авторизовался через KeyCloak используя значения переменных для УЗ "{username_var}" и пароля "{password_var}" без редиректа'
)
def login_in_keycloak_by_cred_vars_without_redirect(
    context, username_var, password_var
):
    open_session(
        context,
        username=get_from_variables(username_var),
        password=get_from_variables(password_var),
        allow_redirects=True,
    )


def open_session(context, username, password, allow_redirects):
    context.keycloak_session = KeyCloakFrontSession(context.host).open(
        username, password, allow_redirects
    )
