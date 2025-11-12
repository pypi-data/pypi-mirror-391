from plonegovbr.socialmedia import PACKAGE_NAME
from Products.CMFPlone.TypesTool import TypesTool

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self, installer):
        """Test if plonegovbr.socialmedia is uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer_not_registered(self, browser_layers):
        """Test that IBrowserLayer is not registered."""
        from plonegovbr.socialmedia.interfaces import IBrowserLayer

        assert IBrowserLayer not in browser_layers


class TestSetupBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self, portal_class, installer_class):
        installer_class.uninstall_product(PACKAGE_NAME)
        self.types_tool: TypesTool = portal_class.portal_types

    @pytest.mark.parametrize(
        "portal_type,behavior",
        [
            ("Plone Site", "plonegovbr.socialmedia.settings"),
        ],
    )
    def test_behavior_not_present(self, portal_type: str, behavior: str):
        """Test if a behavior was removed from a fti."""
        fti = self.types_tool.getTypeInfo(portal_type)
        assert behavior not in fti.behaviors
