import pytest


@pytest.fixture
def social_links() -> list[dict]:
    return [
        {
            "@id": "7e90497e-3ef4-473c-b781-7d7767ab9f1a",
            "href": [{"@id": "https://x.com/ploneorgbr", "title": "x.com/ploneorgbr"}],
            "id": "x",
            "title": "X",
        },
        {
            "@id": "3892d3a9-6c9c-4f04-bee0-5d56b1f5523c",
            "href": [
                {
                    "@id": "https://bsky.app/profile/plone.org.br",
                    "title": "bsky.app/profile/plone.org.br",
                }
            ],
            "id": "bluesky",
            "title": "BlueSky",
        },
        {
            "@id": "3822d3a9-6c9c-4f04-bee0-5d56b1f5523c",
            "href": [
                {
                    "@id": "https://facebook.com/PloneBr",
                    "title": "https://facebook.com/PloneBr",
                }
            ],
            "id": "facebook",
            "title": "Facebook",
        },
        {
            "@id": "3827d3a9-6c9c-4f04-bee0-5d56b1f5523c",
            "href": [
                {
                    "@id": "https://instagram.com/plonebr",
                    "title": "https://instagram.com/plonebr",
                }
            ],
            "id": "instagram",
            "title": "Instagram",
        },
    ]
