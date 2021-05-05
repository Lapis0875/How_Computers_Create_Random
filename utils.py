from functools import wraps
from typing import _GenericAlias, Final, Dict, Any, TypeVar
from sys import stdout
import logging

logger = logging.getLogger('random_impl.utils')
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(
    logging.Formatter(
        style='{',
        fmt='[{asctime}] [{levelname}] {name} > {message}'
    )
)
logger.addHandler(consoleHandler)


__all__ = (
    'int_32',
    'Const',
    'Deprecated',
    'COLLECT_CLASS_CONSTANTS',
    'GET_CLASS_CONSTANTS'
)

# Types


def int_32(number):
    return int(number & 0xFFFFFFFF)  # unsigned int


Const = TypeVar('Const', int, float)


# Annotations

def Deprecated(o):
    @wraps(o.__call__)
    def wrapped_call(*args, **kwargs):
        print('{} is deprecated. You should consider using other ways.'.format(o))
        return o.__call__(*args, **kwargs)

    return wrapped_call


# Type Checker


def _CHECK_TYPEHINT_FINAL(hint) -> bool:
    return hint == Final or (isinstance(hint, _GenericAlias) and hint.__origin__ == Final)


# Utility decorators : Make class constants (Final[T]) can be accessed as method parameters (make them accessible without member call)

@Deprecated
def _COLLECT_CLASS_CONSTANTS(cls) -> Dict[str, Any]:
    logger.debug(f'Constant value cache of class {cls.__name__} is empty! Parsing...')
    constants = [
        const
        for const, typeHint in cls.__annotations__.items()
        if _CHECK_TYPEHINT_FINAL(typeHint)
    ]
    logger.debug(f'Parsed constants names : {constants}')
    mapping = {var: cls.__dict__[var] for var in constants}
    logger.debug(f'Parsed name-value mapping of constant attributes : {mapping}')
    return mapping


@Deprecated
def ACCESS_CLASS_CONSTANTS(func):
    """
    Hacky decorator to make the use of class constant values more easy.
    Decorated methods can retrieve class attributes as normal function parameter.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        this_cache = getattr(ACCESS_CLASS_CONSTANTS, '__cache__', None)
        if this_cache is None:
            logger.debug(f'ACCESS_CLASS_CONSTANTS.cache is empty! Creating...')
            setattr(ACCESS_CLASS_CONSTANTS, '__cache__', {self.__class__: _COLLECT_CLASS_CONSTANTS(self.__class__)})
            logger.debug(f'Stored name-value mapping of constant attributes for class {self.__class__.__name__}')
        else:
            logger.debug(f'ACCESS_CLASS_CONSTANTS.cache is not empty. Searching for class `{self.__class__.__name__}`')
        try:
            mapping = ACCESS_CLASS_CONSTANTS.__cache__[self.__class__]
        except KeyError:
            mapping = ACCESS_CLASS_CONSTANTS.__cache__[self.__class__] = _COLLECT_CLASS_CONSTANTS(self.__class__)

            logger.debug(f'Found Constant value cache of class {self.__class__.__name__}!')

        required_consts = {
            var: mapping[var]
            for var, typeHint in func.__annotations__.items()
            if typeHint == int and var != 'return'
        }
        logger.debug(f'Parsed required class constatns : {required_consts}')
        logger.debug(f'Patching for method `{func.__name__}` in object `{self}`')
        return func(self, *args, **required_consts, **kwargs)

    return wrapper


def COLLECT_CLASS_CONSTANTS(cls):
    cls.__constants__ = {
        var: cls.__dict__[var]
        for var, type in cls.__annotations__.items()
        if _CHECK_TYPEHINT_FINAL(type)
    }
    return cls


def GET_CLASS_CONSTANTS(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        required_consts = {
            var: self.__class__.__constants__[var]
            for var, typeHint in method.__annotations__.items()
            if typeHint == Const and var != 'return'
        }
        logger.debug(f'Parsed required class constants : {required_consts}')
        logger.debug(f'Patching for method `{method.__name__}` in object `{self}`')
        return method(self, *args, **required_consts, **kwargs)

    return wrapped
