from plone.base.utils import get_installer
from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView
from Products.CMFPlone.Portal import PloneSite
from zope.component.hooks import site

import pytest


@pytest.fixture(scope="class")
def portal_class(integration_class):
    if hasattr(integration_class, "testSetUp"):
        integration_class.testSetUp()
    portal = integration_class["portal"]
    with site(portal):
        yield portal
    if hasattr(integration_class, "testTearDown"):
        integration_class.testTearDown()


@pytest.fixture(scope="class")
def installer_class(portal_class: PloneSite) -> InstallerView:
    """Portal helper for managing add-ons using GenericSetup.

    Example usage:
    ```python
    PACKAGE_NAME = "collective.person"

    class TestSetupUninstall:
        @pytest.fixture(autouse=True)
        def uninstalled(self, installer):
            installer.uninstall_product(PACKAGE_NAME)
    ```
    """
    return get_installer(portal_class)
