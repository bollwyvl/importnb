# coding: utf-8
"""# A reloadable remote notebook importer
"""

"""        # Run this cell to use on binder then re run the notebook
        !importnb-install
"""

"""    >>> with remote("https://gist.githubusercontent.com/tonyfast/e7fb55934168744926961f02f6171c6a/raw/*.ipynb"):
    ...     import black_formatter  #doctest: +ELLIPSIS

    >>> with black_formatter.__loader__:
    ...     importlib.reload(black_formatter) #doctest: +ELLIPSIS

    >>> black_formatter2 = Remote().from_filename(black_formatter.__file__)

    >>> with black_formatter.__loader__:
    ...    importlib.reload(black_formatter2) #doctest: +ELLIPSIS
"""

"""    >>>  Remote(exceptions=BaseException).from_filename(
    "https://raw.githubusercontent.com/jakevdp/PythonDataScienceHandbook/master/notebooks/06.00-Figure-Code.ipynb")

    >>> with Remote(path="https://raw.githubusercontent.com/bloomberg/bqplot/master/examples/Marks/Object%20Model/{}.ipynb"):
    ...     import Hist

    >>> Hist.Figure(marks=[Hist.hist], axes=[Hist.ax_x, Hist.ax_y], padding_y=0)
    
"""

'''    >>> with remote("""https://raw.githubusercontent.com/deathbeds/importnb/master/src/importnb/tests/*.ipynb"""):
    ...     import test_importnb
'''

try:
    from .loader import Notebook
except:
    from loader import Notebook
try:
    from importlib._bootstrap import _init_module_attrs
except:
    # python 3.4
    from importlib._bootstrap import _SpecMethods

    def _init_module_attrs(spec, module):
        return _SpecMethods(spec).init_module_attrs(module)


import importlib.util, importlib.machinery, inspect, sys, types, urllib.error, urllib.request

_REMOTE_IMPORT_CACHE = {}


def urlopen(path):
    try:
        return urllib.request.urlopen(path)
    except urllib.error.HTTPError as Exception:
        ...


class RemoteMixin:

    def get_data(self, path):
        global _REMOTE_IMPORT_CACHE
        return _REMOTE_IMPORT_CACHE.pop(path, urlopen(path)).read()

    def __enter__(self):
        super().__enter__()
        sys.meta_path.append(self)
        return self

    def __exit__(self, *args):
        sys.meta_path.pop(sys.meta_path.index(self))
        super().__exit__(*args)

    def find_spec(self, fullname, path=None, *args, **kwargs):
        global _REMOTE_IMPORT_CACHE
        if "." in fullname and fullname.split(".", 1)[0] in sys.modules:
            return

        url = self.path.replace("*", fullname)
        if url not in _REMOTE_IMPORT_CACHE or fullname in sys.modules:
            _REMOTE_IMPORT_CACHE[url] = urlopen(url)
            if _REMOTE_IMPORT_CACHE[url]:
                spec = importlib.machinery.ModuleSpec(
                    fullname, type(self)(fullname, url), origin=url
                )
                spec._set_fileattr = True
                return spec


class Remote(RemoteMixin, Notebook):
    ...


def remote(path, loader=Notebook):
    """A remote notebook finder.  Place a `*` into a url
    to generalize the finder.  It returns a context manager
    """

    class Remote(RemoteMixin, loader):
        ...

    return Remote(path=path)


if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("remote.ipynb", "../remote.py")
