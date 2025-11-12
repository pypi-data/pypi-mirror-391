# plonegovbr.socialmedia

**Social media components for Plone and Volto**

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)
[![PyPI - License](https://img.shields.io/pypi/l/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)
[![PyPI - Status](https://img.shields.io/pypi/status/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)
[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/plonegovbr.socialmedia)](https://pypi.org/project/plonegovbr.socialmedia/)

[![CI](https://github.com/plonegovbr/social-media/actions/workflows/main.yml/badge.svg)](https://github.com/plonegovbr/social-media/actions/workflows/main.yml)
[![GitHub contributors](https://img.shields.io/github/contributors/plonegovbr/social-media)](https://github.com/plonegovbr/social-media)
[![GitHub Repo stars](https://img.shields.io/github/stars/plonegovbr/social-media?style=social)](https://github.com/plonegovbr/social-media)

</div>


## Overview 📚

`plonegovbr.socialmedia` provides behaviors for managing social media metadata and links in Plone sites.
It can be used both with the Volto frontend.


## Features ✨

This package provides two Dexterity behaviors:

### `plonegovbr.socialmedia.settings`

Designed for **navigation root objects** (e.g., the Plone Site itself), it **replaces** the classic Social Media control panel, providing:

- `share_social_data`: Enable/disable sharing social metadata for content.
- `facebook_app_id`: Populate the `fb:app_id` meta tag.
- `social_links`: List of social media profile URLs.
- `facebook_username`: Auto-calculated to populate `og:article:publisher`.
- `x_username`: Auto-calculated to populate `twitter:site`.


### `plonegovbr.socialmedia.links`

Designed for **content types** that require listing social network profiles (e.g., Speaker Profiles on a conference site).

- `social_links`: List of social media profile URLs.


## Installation 🛠️

Add `plonegovbr.socialmedia` to your project dependencies.

### Using `setup.py` 🐍

In your `setup.py`:

```python
install_requires = [
    ...
    "plonegovbr.socialmedia",
]
```

Then install:

```bash
pip install -e .
```


### Using `pyproject.toml` 📜

In your `pyproject.toml`:

```toml
dependencies = [
    ...
    "plonegovbr.socialmedia",
]
```

Then install:

```bash
pip install .
```


## Usage 📖

After installation:

1. Go to the **Plone Control Panel** and enable the `plonegovbr.socialmedia.settings` behavior for your **Plone Site**.
2. Edit the root object to configure social media settings.

To use the `plonegovbr.socialmedia.links` behavior on other content types:

1. Go to **Control Panel → Content Types**.
2. Select the content type (e.g., Event).
3. In the **Behaviors** tab, enable **Social Media: Links**.
4. Save the changes.


## Volto Support ⚡

For Volto frontend integration, install [`@plonegovbr/social-media`](https://www.npmjs.com/package/@plonegovbr/social-media) in your Volto project.

This package provides Volto widgets that integrate seamlessly with the fields provided by `plonegovbr.socialmedia`.

```bash
pnpm add @plonegovbr/social-media
# or
npm install @plonegovbr/social-media
```

## Compatibility ✅

- **Plone**: 6.1+
- **Python**: 3.10+
- **Volto**: 18+


## Contributing 🤝

Contributions are welcome!

- [Source Code](https://github.com/plonegovbr/social-media) 💻
- [Issue Tracker](https://github.com/plonegovbr/social-media/issues) 🐛

Before submitting a pull request, please make sure your code passes tests and follows project guidelines.


## License 📜

This project is licensed under the **GPLv2**.


## Credits & Acknowledgements 🙏

Maintained by the [PloneGov-Br Community](https://plone.org.br/gov) 🇧🇷❤️.
