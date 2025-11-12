from plonegovbr.socialmedia import PACKAGE_NAME

import pytest


class TestBehaviorSettings:
    name: str = f"{PACKAGE_NAME}.settings"

    @pytest.mark.parametrize("role,path", (["anonymous", "/"], ["manager", "/"]))
    def test_inherit_endpoint(self, request_roles, role: str, path: str):
        request = request_roles(role)
        url = f"{path}?expand=inherit&expand.inherit.behaviors={self.name}"
        response = request.get(url)
        assert response.status_code == 200
        data = response.json()
        inherit = data["@components"]["inherit"]
        assert self.name in inherit
        behavior_info = inherit[self.name]
        assert "data" in behavior_info
        assert "from" in behavior_info
        behavior_data = behavior_info["data"]
        assert behavior_data["share_social_data"] is True
        assert behavior_data["facebook_app_id"] == ""
        assert behavior_data["facebook_username"] == "PloneBr"
        assert behavior_data["x_username"] == "ploneorgbr"
        assert len(behavior_data["social_links"]) == 4

    @pytest.mark.parametrize("portal_type", ("Plone Site",))
    def test_types_endpoint(self, manager_request, portal_type: str):
        url = f"/@types/{portal_type}"
        response = manager_request.get(url)
        assert response.status_code == 200
        data = response.json()
        fieldsets = {f["id"]: f for f in data["fieldsets"]}
        assert "social_media" in fieldsets
        fields = fieldsets["social_media"]["fields"]
        assert "share_social_data" in fields
        assert "facebook_app_id" in fields
        assert "social_links" in fields
        # Not in the schema
        assert "facebook_username" not in fields
        assert "x_username" not in fields
