from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from plonegovbr.socialmedia import _
from plonegovbr.socialmedia.behaviors import base
from zope.interface import provider


@provider(IFormFieldProvider)
class ISocialLinks(model.Schema):
    """Social links used for content types."""

    model.fieldset(
        "social_media",
        label=_("Social Media"),
        fields=[
            "social_links",
        ],
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
