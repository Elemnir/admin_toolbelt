__version__     = "0.1.0"

__title__       = "admin_toolbelt"
__description__ = "A collection of tools for administering systems."
__uri__         = "https://github.com/Elemnir/django-duo-auth"

__author__      = "Adam Howard"
__email__       = "ahoward0920@gmail.com"

__license__     = "BSD 3-clause"
__copyright__   = "Copyright (c) 2019 Adam Howard"


from dramatiq.broker import global_broker, set_broker
from dramatiq.brokers.stub import StubBroker

if global_broker is None:
    set_broker(StubBroker())
