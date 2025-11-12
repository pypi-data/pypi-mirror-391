import pytest


class TestBehaviorLinks:
    @pytest.mark.parametrize("role,path", (["manager", "/profiles"],))
    def test_added_to_content(self, request_roles, role: str, path: str):
        request = request_roles(role)
        response = request.get(path)
        assert response.status_code == 200
        data = response.json()
        assert len(data["social_links"]) == 4

    @pytest.mark.parametrize("portal_type", ("Document",))
    def test_types_endpoint(self, manager_request, portal_type: str):
        url = f"/@types/{portal_type}"
        response = manager_request.get(url)
        assert response.status_code == 200
        data = response.json()
        fieldsets = {f["id"]: f for f in data["fieldsets"]}
        assert "social_media" in fieldsets
        fields = fieldsets["social_media"]["fields"]
        assert "social_links" in fields
