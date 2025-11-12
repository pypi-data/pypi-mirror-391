from plonegovbr.socialmedia import PACKAGE_NAME
from Products.CMFPlone.PloneControlPanel import PloneControlPanel
from Products.CMFPlone.TypesTool import TypesTool

import pytest


class TestSetupInstall:
    def test_addon_installed(self, installer):
        """Test if plonegovbr.socialmedia is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from plonegovbr.socialmedia.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1000"

    def test_configlet_disabled(self, portal):
        """Test if socialmedia control panel is disabled."""
        controlpanel: PloneControlPanel = portal.portal_controlpanel
        actions = {a.getAction(portal)["id"]: a for a in controlpanel.listActions()}
        assert "socialmedia" in actions
        assert bool(actions["socialmedia"].visible) is False


class TestSetupBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self, portal_class):
        self.portal = portal_class
        self.types_tool: TypesTool = portal_class.portal_types

    @pytest.mark.parametrize(
        "portal_type,behavior",
        [
            ("Plone Site", "plonegovbr.socialmedia.settings"),
        ],
    )
    def test_behavior_present(self, portal_type: str, behavior: str):
        """Test if a behavior is added to a fti."""
        fti = self.types_tool.getTypeInfo(portal_type)
        assert behavior in fti.behaviors
