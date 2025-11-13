from traceroot.logger import get_logger
from traceroot.tracer import init, shutdown, trace

__version__ = '0.0.7a1'

init()

__all__ = [
    'init',
    'trace',
    'get_logger',
    'shutdown',
]
