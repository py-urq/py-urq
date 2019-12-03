import pkg_resources

__version__ = pkg_resources.resource_string(__name__, 'py_urq.version').decode('utf-8').strip()

