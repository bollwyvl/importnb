# coding: utf-8
"""# `Parameterize` notebooks.

The execute importer maintains an attribute that includes the notebooks inputs and outputs.

    >>> f = Parameterize().from_filename('parameterize.ipynb', 'importnb.notebooks')
    >>> assert 'a_variable_to_parameterize' in f.__signature__.parameters
    >>> assert f(a_variable_to_parameterize=100)

"""

try:
    from .execute import Execute, loader_include_notebook
except:
    from importnb.execute import Execute, loader_include_notebook

import ast

from collections import ChainMap

from importlib._bootstrap import _new_module

try:
    from importlib._bootstrap import _init_module_attrs
except:
    # python 3.4
    from importlib._bootstrap import _SpecMethods

    def _init_module_attrs(spec, module):
        return _SpecMethods(spec).init_module_attrs(module)


__all__ = "Parameterize",

a_variable_to_parameterize = 42

if globals().get("show", None):
    print("I am tested.")


class AssignmentFinder(ast.NodeTransformer):
    """Find an ast assignments that ast.literal_eval
    
    >>> assert len(AssignmentFinder().visit(ast.parse("a = 10; print(a);")).body) == 1
    """
    visit_Module = ast.NodeTransformer.generic_visit

    def visit_Assign(self, node):
        if len(node.targets):
            try:
                if not getattr(node.targets[0], "id", "_").startswith("_"):
                    ast.literal_eval(node.value)
                    return node
            except:
                ...

    def generic_visit(self, node):
        ...


class AssignmentIgnore(AssignmentFinder):

    def visit_Assign(self, node):
        if isinstance(super().visit_Assign(node), ast.Assign):
            return
        return node

    def generic_visit(self, node):
        return node


def copy_module(module):
    new = type(module)(module.__name__)
    new.__dict__.update(module.__dict__)
    return new


class Parameterize(Execute):
    """Discover any literal ast expression and create parameters from them. 
            
    Parametize is a NodeTransformer that import any nodes return by Parameterize Node.
    """

    def create_module(self, spec):
        module = _new_module(spec.name)
        _init_module_attrs(spec, module)

        # Import the notebook when parameterize is imported
        loader_include_notebook(self, module)

        node = self.nb_to_ast(module._notebook)

        # Extra effort to supply a docstring
        doc = None
        if node.body:
            _node = node.body[0]
            if isinstance(_node, ast.Expr) and isinstance(_node.value, ast.Str):
                doc = _node

        # Discover the parameterizable nodes
        params = AssignmentFinder().visit(node)

        # Include the string in the compilation
        doc and params.body.insert(0, doc)

        # Supply the literal parameter values as module globals.
        exec(compile(params, "<parameterize>", "exec"), module.__dict__, module.__dict__)
        return module

    def from_filename(self, filename, path=None, **globals):
        module = super().from_filename(filename, path, exec=False)

        def recall(**kwargs):
            nonlocal module, globals
            module.__loader__.exec_module(module, **ChainMap(kwargs, globals))
            return copy_module(module)

        recall.__signature__ = vars_to_sig(
            **{k: v for k, v in module.__dict__.items() if not k.startswith("_")}
        )
        recall.__doc__ = module.__doc__
        return recall

    def _exec_cell(self, cell, node, module, prev=None):
        node = AssignmentIgnore().visit(node)

        super()._exec_cell(cell, node, module, prev=prev)


def vars_to_sig(**vars):
    """Create a signature for a dictionary of names."""
    from inspect import Parameter, Signature

    return Signature([Parameter(str, Parameter.KEYWORD_ONLY, default=vars[str]) for str in vars])


if __name__ == "__main__":
    f = Parameterize(exceptions=BaseException).from_filename("execute.ipynb", "importnb.notebooks")
    m = f(a_variable_to_parameterize=10)

"""# Developer
"""

if __name__ == "__main__":
    try:
        from utils.export import export
    except:
        from .utils.export import export
    export("parameterize.ipynb", "../parameterize.py")
    module = Execute().from_filename("parameterize.ipynb")
    __import__("doctest").testmod(module, verbose=2)