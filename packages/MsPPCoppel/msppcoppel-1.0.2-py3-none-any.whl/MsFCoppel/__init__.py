from .microservices import Microservices
from .ms_base import KafkaBase
from .loggs import Loggs
from .types import Types, TypesActions, Actions, HttpError
from .options import Options
from .ErrorMs import ErrorMs
from .version_framework import version
from .HttpResponse import HttpResponse
from .HttpErrors import BadRequest
from .loggs import Loggs

name = 'MsFCoppel'

__all__ = [
    'Microservices',
    'KafkaBase',
    'Loggs',
    'Types',
    'Options',
    'MsManager',
    'TypesActions',
    'ErrorMs',
    'Actions',
    'HttpResponse',
    'HttpError',
    'BadRequest',
]

__version__ = version
