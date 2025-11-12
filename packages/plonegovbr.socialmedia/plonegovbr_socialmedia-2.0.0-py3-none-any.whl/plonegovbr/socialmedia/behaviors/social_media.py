from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import DexterityContent
from plone.schema import JSONField
from plone.supermodel import model
from plonegovbr.socialmedia import _
from plonegovbr.socialmedia import utils
from plonegovbr.socialmedia.behaviors import base
from zope import schema
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class ISocialMedia(Interface):
    """Marker for content that has social media settings."""


@provider(IFormFieldProvider)
class ISocialMediaSettings(model.Schema):
    """Site/Subsite social media settings."""

    model.fieldset(
        "social_media",
        label=_("Social Media"),
        fields=[
            "share_social_data",
            "facebook_app_id",
            "social_links",
        ],
    )

    share_social_data = schema.Bool(
        title=_("Share social data"),
        description=_(
            "Include meta tags on pages to give hints to "
            "social media on how to better render your pages "
            "when shared"
        ),
        default=True,
        required=False,
    )

    x_username = schema.TextLine(
        title=_("X username"),
        readonly=True,
    )

    facebook_app_id = schema.ASCIILine(
        title=_("Facebook App ID"),
        description=_("To be used with some integrations like Open Graph data"),
        required=False,
        default="",
    )

    facebook_username = schema.TextLine(
        title=_("Facebook username"),
        readonly=True,
    )

    directives.widget(
        "social_links",
        frontendOptions={
            "widget": "object_list",
            "widgetProps": {"schemaName": "socialMedia"},
        },
    )
    social_links = JSONField(
        title=_("Profiles"),
        schema=base.OBJECT_LIST,
        default=base.OBJECT_LIST_DEFAULT_VALUE,
        required=False,
        widget="",
    )


@implementer(ISocialMediaSettings)
class SocialMediaSettings:
    def __init__(self, context: DexterityContent):
        self.context = context

    @property
    def share_social_data(self) -> bool:
        """Getter, read from context and return back"""
        return self.context.share_social_data

    @share_social_data.setter
    def share_social_data(self, value: bool):
        """Setter, called by the form, set on context."""
        self.context.share_social_data = value

    @property
    def facebook_app_id(self) -> str:
        """Getter, read from context and return back"""
        return self.context.facebook_app_id

    @facebook_app_id.setter
    def facebook_app_id(self, value: str):
        """Setter, called by the form, set on context."""
        self.context.facebook_app_id = value

    @property
    def x_username(self) -> str:
        """X username extracted from social_links."""
        return utils.extract_username_from_social_links(self.social_links, "x")

    @property
    def facebook_username(self) -> str:
        """Facebook username extracted from social_links."""
        return utils.extract_username_from_social_links(self.social_links, "facebook")

    @property
    def social_links(self) -> list[dict]:
        """Getter, read from context and return back"""
        return self.context.social_links

    @social_links.setter
    def social_links(self, value: list[dict]):
        """Setter, called by the form, set on context."""
        self.context.social_links = value
