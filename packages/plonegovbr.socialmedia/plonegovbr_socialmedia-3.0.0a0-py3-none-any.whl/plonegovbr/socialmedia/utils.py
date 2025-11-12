import re


PATTERNS = {
    "facebook": re.compile(
        r"^(http:|https:|)\/\/(m.|www.)?(facebook)\.com\/(?P<username>[A-Za-z0-9._-]*)$"
    ),
    "x": re.compile(
        r"^(http:|https:|)\/\/(m.|www.)?(x|twitter)\.com\/(?P<username>[A-Za-z0-9._-]*)$"
    ),
}


def filter_social_links(social_links: list[dict], network_id: str) -> dict | None:
    """Given a list of social links, filter the first one with the given network_id."""
    for network in social_links:
        if network["id"] == network_id:
            return network
    return None


def extract_username_from_profile(profile: str, network_id: str) -> str:
    """Extract the username from a profile url."""
    pattern = PATTERNS.get(network_id)
    if pattern and (match := re.match(pattern, profile)):
        username = match.groupdict()["username"]
        return username
    return ""


def extract_username_from_social_links(
    social_links: list[dict], network_id: str
) -> str:
    """Given a list of social links, filter the first one with the given network_id."""
    network_info = filter_social_links(social_links, network_id)
    if network_info:
        profile_url = network_info["href"][0]["@id"]
        return extract_username_from_profile(profile_url, network_id)
    return ""
