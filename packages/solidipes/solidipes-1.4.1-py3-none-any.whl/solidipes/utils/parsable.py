#!/usr/bin/env python

from abc import ABC


################################################################
class parameter(property):
    def __init__(self, func, optional=False, last=False) -> None:
        self.optional = optional
        self.key = func.__name__
        self.name_var = "_" + self.key
        self.func = func
        self.last = last
        super().__init__(self.foo, self.foo_setter)
        self.__doc__ = func.__doc__

    def foo(self, obj, *args, **kwargs):
        if not hasattr(obj, self.name_var):
            value = self.func(*args, **kwargs)
            if value is None:
                raise ValueError(f"{self.key} has no default parameter")
            self.foo_setter(obj, value)

        return getattr(obj, self.name_var)

    def foo_setter(self, obj, value, *args, **kwargs) -> None:
        setattr(obj, self.name_var, value)


class optional_parameter(parameter):
    def __init__(self, func) -> None:
        super().__init__(func, optional=True)


class last_parameter(parameter):
    def __init__(self, func) -> None:
        super().__init__(func, last=True)


class last_parameter_with_default(last_parameter):
    def __init__(self, func) -> None:
        super().__init__(func)


################################################################


def populate_parser(cls, parser) -> None:
    _parameters = dict()
    _groups = dict()
    import typing

    def _register(key, _cls, v):
        if key not in _parameters:
            _parameters[key] = (_cls, v)
        if _cls not in _groups:
            _groups[_cls] = parser.add_argument_group(_cls.__name__)

    cls.apply_to_parameters(_register)

    for key, (_cls, v) in _parameters.items():
        func = getattr(_cls, key)
        type_hints = typing.get_type_hints(func.func)
        arg_name = func.key
        if func.optional:
            arg_name = "--" + arg_name

        try:
            ret_type = type_hints["return"]
        except KeyError:
            raise RuntimeError(f"Parameter {cls.__name__}.{key} was not annotated with a return type")

        _parser = _groups[_cls]
        if ret_type is bool:
            if func.func():
                action = "store_false"
            else:
                action = "store_true"

            _parser.add_argument(arg_name, help=func.__doc__, action=action)
        elif isinstance(v, last_parameter_with_default):
            _parser.add_argument(
                arg_name,
                nargs="?",
                default="TBD",
                help=func.__doc__,
                type=type_hints["return"],
            )
        else:
            _parser.add_argument(arg_name, help=func.__doc__, type=type_hints["return"])


################################################################


def get_key_to_parsables(name, cls):
    from solidipes.plugins.discovery import (
        get_subclasses_from_plugins,
        plugin_package_names,
    )

    parsable_subclasses = get_subclasses_from_plugins(plugin_package_names, name, cls)
    key_to_parsable = {}
    for e in parsable_subclasses:
        if e.parser_key is None:
            continue
        if not isinstance(e.parser_key, list):
            e.parser_key = [e.parser_key]
        for k in e.parser_key:
            key_to_parsable[k] = e

    return key_to_parsable


################################################################


class Parsable(ABC):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v == "TBD":
                continue
            if v is not None:
                setattr(self, k, v)

    @classmethod
    def populate_parser(cls, parser) -> None:
        populate_parser(cls, parser)

    @classmethod
    def run_and_check_return(cls, command, **kwargs) -> None:
        from solidipes.utils.utils import run_and_check_return

        return run_and_check_return(command, **kwargs)

    @classmethod
    def apply_to_parameters(cls, func) -> None:
        _parameters = set()
        last_parameters = dict()

        _groups = dict()

        from ..plugins.discovery import apply_to_object_parent_classes

        def filter_parameters(_cls) -> None:
            for key, v in _cls.__dict__.items():
                if key in _parameters:
                    continue
                _parameters.add(key)
                if isinstance(v, parameter):
                    if v.last:
                        last_parameters[key] = (_cls, v)
                        continue
                    func(key, _cls, v)

        apply_to_object_parent_classes(cls, filter_parameters)

        for k, (_cls, v) in last_parameters.items():
            func(k, _cls, v)

    @classmethod
    def streamlit_widget(cls, name=None, defaults=None, **kwargs):
        if name is None:
            name = cls.parser_key

        import streamlit as st

        option_list = []
        params = {}

        cls.apply_to_parameters(lambda *args: option_list.append(args))

        with st.form(name):
            st.markdown(f"*{cls.__doc__}*")
            parameters = st.container()
            options = st.expander("options")
            for name, downloader, param_type in option_list:
                if name in kwargs:
                    params[name] = kwargs.get(name)
                    continue
                from solidipes.utils.parsable import optional_parameter

                if isinstance(param_type, optional_parameter):
                    layout = options
                else:
                    layout = parameters

                params[name] = make_input_from_parameter(
                    name,
                    downloader,
                    param_type,
                    layout=layout,
                    default=defaults.get(name, None),
                )

            submitted = st.form_submit_button("Submit")
            if defaults.get("submit", False):
                submitted = True
                # st.write(params)
        if submitted:
            # st.write(params)
            params = {k: v for k, v in params.items() if v is not None and v != ""}
            # st.write(params)
            return params

        return False


################################################################
def make_input_from_parameter(name, parsable, param_type, layout=None, default=None):
    import streamlit as st

    if layout is None:
        layout = st
    func = getattr(parsable, name)
    import typing

    type_hints = typing.get_type_hints(func.func)
    ret_type = type_hints["return"]

    if ret_type is str:
        return layout.text_input(name, key=f"{parsable.__name__}-{name}", value=default)
    elif ret_type is bool:
        if default is None:
            default = func.func()
        return layout.toggle(name, value=default)

    layout.write(f"unknown type: {name}->{ret_type}")
