from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from plonegovbr.socialmedia import PACKAGE_NAME
from Products.GenericSetup.tool import SetupTool
from zope.component.hooks import site

import pytest
import transaction


@pytest.fixture()
def portal(functional):
    portal = functional["portal"]
    with site(portal):
        st: SetupTool = api.portal.get_tool("portal_setup")
        st.runAllImportStepsFromProfile(f"profile-{PACKAGE_NAME}:demo")
        transaction.commit()
        yield portal


@pytest.fixture()
def http_request(functional):
    return functional["request"]


@pytest.fixture()
def request_factory(portal):
    def factory():
        url = portal.absolute_url()
        api_session = RelativeSession(url)
        api_session.headers.update({"Accept": "application/json"})
        return api_session

    return factory


@pytest.fixture()
def anon_request(request_factory):
    return request_factory()


@pytest.fixture()
def manager_request(request_factory):
    request = request_factory()
    request.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield request
    request.auth = ()


@pytest.fixture()
def request_roles(anon_request, manager_request):
    factories = {
        "anonymous": anon_request,
        "manager": manager_request,
    }

    def func(role: str):
        return factories[role]

    return func
