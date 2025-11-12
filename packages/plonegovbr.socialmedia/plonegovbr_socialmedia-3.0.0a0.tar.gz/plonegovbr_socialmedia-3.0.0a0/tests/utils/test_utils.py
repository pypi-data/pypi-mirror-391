from plonegovbr.socialmedia import utils

import pytest


@pytest.mark.parametrize(
    "profile,network_id,expected",
    [
        ("https://x.com/ploneorgbr", "x", "ploneorgbr"),
        ("https://twitter.com/ploneorgbr", "x", "ploneorgbr"),
        ("https://facebook.com/plonecms", "facebook", "plonecms"),
        ("https://facebook.com/PloneBr", "facebook", "PloneBr"),
    ],
)
def test_extract_username_from_profile(profile: str, network_id: str, expected: str):
    func = utils.extract_username_from_profile
    result = func(profile, network_id)
    assert result == expected


@pytest.mark.parametrize(
    "network_id,expected",
    [
        ("x", "ploneorgbr"),
        ("facebook", "PloneBr"),
    ],
)
def test_extract_username_from_social_links(
    social_links, network_id: str, expected: str
):
    func = utils.extract_username_from_social_links
    result = func(social_links, network_id)
    assert result == expected
