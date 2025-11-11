"""This module centralizes detection, path computation, and attribute application
for OLX "pointer" tags used by XBlocks during import/export.
Also provides helpers to load definition XML files referenced by pointer tags.

Note: The functionality has been taken from the edx-platform's XmlMixin class.
https://github.com/openedx/edx-platform/blob/18d5abb2f641db7f364f7566187e57bebdae9fe9/xmodule/xml_block.py
"""

import datetime
import json
from typing import Any, TextIO

from django.core.serializers.json import DjangoJSONEncoder
from fs.osfs import OSFS
from lxml import etree
from lxml.etree import _Element as Element
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import BlockUsageLocator
from xblock.core import XBlock
from xblock.fields import Field, Scope
from xblock.runtime import Runtime

# Assume all XML files are persisted as utf-8.
EDX_XML_PARSER = etree.XMLParser(dtd_validation=False, load_dtd=False, remove_blank_text=True, encoding="utf-8")

filename_extension = "xml"


class EdxJSONEncoder(DjangoJSONEncoder):
    """
    Custom JSONEncoder that handles ``Location`` and ``datetime.datetime`` objects.
    Encodes ``Location`` as its URL string form, and ``datetime.datetime`` as an ISO 8601 string.
    """

    def default(self, o):
        if isinstance(o, (CourseKey, UsageKey)):
            return str(o)
        elif isinstance(o, datetime.datetime):
            if o.tzinfo is not None:
                if o.utcoffset() is None:
                    return o.isoformat() + "Z"
                else:
                    return o.isoformat()
            else:
                return o.isoformat()
        else:
            return super().default(o)


def name_to_pathname(name: str) -> str:
    """
    Convert a location name for use in a path: replace ':' with '/'.
    This allows users of the xml format to organize content into directories
    """
    return name.replace(":", "/")


def is_pointer_tag(xml_obj: Element) -> bool:
    """
    Check if xml_obj is a pointer tag: <blah url_name="something" />.
    No children, one attribute named url_name, no text.

    Special case for course roots: the pointer is
      <course url_name="something" org="myorg" course="course">

    xml_obj: an etree Element

    Returns a bool.
    """
    if xml_obj.tag != "course":
        expected_attr = {"url_name"}
    else:
        expected_attr = {"url_name", "course", "org"}

    actual_attr = set(xml_obj.attrib.keys())

    has_text = xml_obj.text is not None and len(xml_obj.text.strip()) > 0

    return len(xml_obj) == 0 and actual_attr == expected_attr and not has_text


def serialize_field(value: Any) -> str:
    """
    Return a string version of the value (where value is the JSON-formatted, internally stored value).

    If the value is a string, then we simply return what was passed in.
    Otherwise, we return json.dumps on the input value.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, datetime.datetime):
        if value.tzinfo is not None and value.utcoffset() is None:
            return value.isoformat() + "Z"
        return value.isoformat()

    return json.dumps(value, cls=EdxJSONEncoder)


def deserialize_field(field: Field, value: str) -> Any:
    """
    Deserialize the string version to the value stored internally.

    Note that this is not the same as the value returned by from_json, as model types typically store
    their value internally as JSON. By default, this method will return the result of calling json.loads
    on the supplied value, unless json.loads throws a TypeError, or the type of the value returned by json.loads
    is not supported for this class (from_json throws an Error). In either of those cases, this method returns
    the input value.
    """
    try:
        deserialized = json.loads(value)
        if deserialized is None:
            return deserialized
        try:
            field.from_json(deserialized)
            return deserialized
        except (ValueError, TypeError):
            # Support older serialized version, which was just a string, not result of json.dumps.
            # If the deserialized version cannot be converted to the type (via from_json),
            # just return the original value. For example, if a string value of '3.4' was
            # stored for a String field (before we started storing the result of json.dumps),
            # then it would be deserialized as 3.4, but 3.4 is not supported for a String
            # field. Therefore field.from_json(3.4) will throw an Error, and we should
            # actually return the original value of '3.4'.
            return value

    except (ValueError, TypeError):
        # Support older serialized version.
        return value


def own_metadata(block: XBlock) -> dict[str, Any]:
    """
    Return a JSON-friendly dictionary that contains only non-inherited field
    keys, mapped to their serialized values
    """
    return block.get_explicitly_set_fields_by_scope(Scope.settings)


def apply_pointer_attributes(node: Element, block: XBlock) -> None:
    """Apply required pointer attributes to the relevant node for a block.

    Sets "url_name" for all blocks. For course blocks, additionally assigns
    "org" and "course" attributes.
    """
    if not node.get("url_name"):
        node.set("url_name", block.url_name)

    if getattr(block, "category", None) == "course":
        # These attributes are required on course pointers
        node.set("org", block.location.org)
        node.set("course", block.location.course)


def format_filepath(category: str, name: str) -> str:
    """Formats a path to an XML definition file."""
    return f"{category}/{name}.{filename_extension}"


def file_to_xml(file_object: TextIO) -> Element:
    """
    Used when this module wants to parse a file object to xml
    that will be converted to the definition.

    Returns an lxml Element
    """
    return etree.parse(file_object, parser=EDX_XML_PARSER).getroot()


def load_file(filepath: str, fs: OSFS, def_id: BlockUsageLocator) -> Element:
    """
    Open the specified file in fs, and call `file_to_xml` on it,
    returning the lxml object.

    Add details and reraise on error.
    """
    try:
        with fs.open(filepath) as xml_file:
            return file_to_xml(xml_file)
    except Exception as err:
        # Add info about where we are, but keep the traceback
        raise Exception(f"Unable to load file contents at path {filepath} for item {def_id}: {err}") from err


def load_definition_xml(node: Element, runtime: Runtime, def_id: BlockUsageLocator) -> tuple[Element, str]:
    """
    Loads definition_xml stored in a dedicated file
    """
    url_name = node.get("url_name")
    filepath = format_filepath(node.tag, name_to_pathname(url_name))
    definition_xml = load_file(filepath, runtime.resources_fs, def_id)
    return definition_xml, filepath
