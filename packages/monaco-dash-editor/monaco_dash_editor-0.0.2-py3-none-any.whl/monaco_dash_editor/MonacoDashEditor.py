# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class MonacoDashEditor(Component):
    """A MonacoDashEditor component.


Keyword arguments:

- id (dict; optional):
    The ID used to identify this component in Dash callbacks. Can be a
    string or a dictionary with additional data attributes.

    `id` is a string | dict with keys:

    - id (string; required)

    - __extras__ (dict with strings as keys and values of type string; optional)

- className (string; default ''):
    Additional CSS class for the container Allows custom styling of
    the editor container Defaults to an empty string.

- height (string; default '300px'):
    Height of the editor Defaults to '300px'.

- language (string; default 'javascript'):
    The programming language for syntax highlighting Supports various
    languages like 'javascript', 'python', 'json', etc. Defaults to
    'javascript'.

- options (dict; optional):
    Additional Monaco Editor configuration options Allows fine-tuning
    of editor behavior and appearance Defaults to an empty object.

- readOnly (boolean; default False):
    Make editor read-only Prevents user from modifying the content
    Defaults to False.

- theme (string; default 'vs-light'):
    Editor theme Supports 'vs-light', 'vs-dark', 'hc-black' Defaults
    to 'vs-light'.

- value (string; default ''):
    Current content/value of the editor Defaults to an empty string."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'monaco_dash_editor'
    _type = 'MonacoDashEditor'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        height: typing.Optional[str] = None,
        language: typing.Optional[str] = None,
        value: typing.Optional[str] = None,
        theme: typing.Optional[str] = None,
        readOnly: typing.Optional[bool] = None,
        options: typing.Optional[dict] = None,
        className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'className', 'height', 'language', 'options', 'readOnly', 'style', 'theme', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'height', 'language', 'options', 'readOnly', 'style', 'theme', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(MonacoDashEditor, self).__init__(**args)

setattr(MonacoDashEditor, "__init__", _explicitize_args(MonacoDashEditor.__init__))
