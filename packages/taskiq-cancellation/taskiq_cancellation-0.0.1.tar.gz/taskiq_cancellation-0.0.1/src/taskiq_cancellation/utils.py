import typing
import inspect
import functools
import logging
from collections import OrderedDict


def combines(
    wrapped: typing.Callable, add_var_parameters: bool = False
) -> typing.Callable:
    """
    Combines wrapped and wrapper functions signatures and type hints

    In cases of parameter collision wrapper parameters will be used

    Example:
    '''
    import inspect

    def decorator(func):
        @combines(func)
        def wrapper(c: int, *args, **kwargs):
            return foo(*args, **kwargs) * c
        return wrapper

    @decorator
    def foo(a: int, b = "lol"):
        return b * a

    print(inspect.signature(foo))
    # (a: int, c: int, b='lol', *args, **kwargs)
    '''

    :param wrapped: function to be wrapped
    :type wrapped: Callable
    :param add_var_parameters: add *args and **kwargs from wrapper to new signature
    :type add_var_parameters: bool
    """
    wrapped_signature: inspect.Signature = inspect.signature(wrapped)
    wrapped_type_hints: typing.Dict[str, str] = typing.get_type_hints(wrapped)

    def decorator(wrapper):
        wrapper_signature = inspect.signature(wrapper)
        wrapper_type_hints = typing.get_type_hints(wrapper)

        for param_name in wrapped_signature.parameters.keys():
            if param_name in wrapper_signature.parameters.keys():
                logging.warning(
                    f"Parameter {param_name} will be overwritten by wrapper function"
                )

        wrapper_parameters = OrderedDict()
        for name, parameter in wrapper_signature.parameters.items():
            if not add_var_parameters:
                if any(
                    (
                        parameter.kind is inspect.Parameter.VAR_POSITIONAL,
                        parameter.kind is inspect.Parameter.VAR_KEYWORD,
                    )
                ):
                    continue
            wrapper_parameters[name] = parameter

        parameters = OrderedDict(wrapped_signature.parameters, **wrapper_parameters)
        parameters = sorted(
            parameters.values(),
            key=lambda p: p.kind + (0.5 if p.default != inspect.Parameter.empty else 0),
        )

        new_return_annotation: inspect.Signature
        if wrapper_signature.return_annotation is not None:
            new_return_annotation = wrapper_signature.return_annotation
        else:
            new_return_annotation = wrapped_signature.return_annotation

        new_signature = inspect.Signature(
            parameters=parameters, return_annotation=new_return_annotation
        )
        new_annotations = dict(wrapped_type_hints, **wrapper_type_hints)

        wrapper = functools.wraps(wrapped)(wrapper)
        wrapper.__annotations__ = new_annotations
        wrapper.__signature__ = new_signature

        return wrapper

    return decorator


class StopTaskGroupException(Exception):
    pass


__all__ = ["combines"]
