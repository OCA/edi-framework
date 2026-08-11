# Copyright 2020 ACSONE SA/NV
# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from lxml import etree

_logger = logging.getLogger(__name__)


def xml_purge_nswrapper(xml_content):
    """Purge `nswrapper` elements.

    .. deprecated::
        The `nswrapper` trick is deprecated. Declare namespaces directly
        on a `<t>` element instead, as `t` is never rendered to output:

            <t xmlns:foo="http://www.unece.org/cefact/Foo">
                <foo:LovelyNamespacedElement />
            </t>

        This function is kept only for backward compatibility with
        templates still using the old `nswrapper` element.

    QWeb template does not allow parsing namespaced elements
    without declaring namespaces on the root element.

    Hence, by default you cannot define smaller re-usable templates
    if the have namespaced elements.

    The (deprecated) trick was to wrap your reusable template with an
    `nswrapper` element which holds the namespace for that particular
    sub template. For instance:

        <nswrapper xmlns:foo="http://www.unece.org/cefact/Foo">
            <foo:LovelyNamespacedElement />
        </nswrapper>

    Then this method is going to purge these unwanted elements from the result.
    """
    if not (xml_content and xml_content.strip()):
        return xml_content
    root = etree.XML(xml_content)
    # Deeper elements come after, keep the root element at the end (if any).
    # Use `name()` because the real element could be namespaced on render.
    nswrappers = root.xpath("//*[name() = 'nswrapper']")
    if nswrappers:
        _logger.warning(
            "Deprecated `nswrapper` element found. "
            "Use a `<t>` element to declare namespaces instead."
        )
    for nswrapper in reversed(nswrappers):
        parent = nswrapper.getparent()
        if parent is None:
            # fmt:off
            return "".join(
                [etree.tostring(child, encoding="unicode")
                    for child in nswrapper.getchildren()]
            )
            # fmt:on
        parent.extend(nswrapper.getchildren())
        parent.remove(nswrapper)
    return etree.tostring(root)
