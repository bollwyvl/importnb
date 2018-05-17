__IPYTHON__ = False

try:
    from IPython import get_ipython
    if not get_ipython(): ...
    else: __IPYTHON__ = True
except: ...

from pathlib import Path

try:
    from ..compiler_python import ScriptExporter

except:
    from importnb.compiler_python import ScriptExporter

def export(src, dst):
    Path(dst).write_text(ScriptExporter().from_filename(src)[0])

if __name__ ==  '__main__':

    export('__init__.ipynb', '../../importnb/utils/__init__.py')
    export('__init__.ipynb', '__init__.py')