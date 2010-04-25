#!/usr/bin/env python2.6

"""
Tracer for python-csp generating a process graph with graphviz.

Some source from pycallgraph.py is used here.  pycallgraph is
published under the GNU General Public License.
U{http://pycallgraph.slowchop.com/} (C) Gerald Kaszuba 2007

Copyright (C) Sarah Mount, 2009.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program; if not, write to the Free Software
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Sarah Mount, Gerald Kaszuba'
__date__ = 'June 2009'


import csp.cspprocess

import inspect
#import linecache
import os
import sys
import types

from distutils import sysconfig
from stack import Stack


DEBUG = True

tracer = None

ignore = ('tracer.stop_trace',
          'Synchronized.getvalue',
          'Synchronized.setvalue',
          'csp.cspprocess._call',
          'csp.cspprocess._debug',
          'csp.cspprocess.CSPProcess.__init__',          
          'csp.cspprocess.Par.__init__',          
          'csp.cspprocess.Seq.__init__',          
          'csp.cspprocess.Alt.__init__',          
          'csp.cspprocess.Channel.__del__',
          'csp.cspprocess.Channel.__init__',
          'csp.cspprocess.Channel.put',
          'csp.cspprocess.Channel.get',
          'csp.cspprocess.Channel.enable',
          'csp.cspprocess.Channel.disable',
          'csp.cspprocess.Channel.checkpoison'
          )


processes = Stack()


def reset_trace():
    """Reset any globals here.

    TODO: Writeme!
    """
    return


def start_trace():
    """Start the tracer.
    Required to be overridden by sys.
    """
    global tracer
    tracer = Tracer()
    sys.settrace(tracer.trace)
    reset_trace()
    return


def stop_trace():
    """Stop the tracer.
    Required to be overridden by sys.
    """
    sys.settrace(None)
    return


class memoized(object):
    """Decorator that caches a function's return value each time it is
    called.  If called later with the same arguments, the cached value
    is returned, and not re-evaluated.

    From the Python decorator library:
    U{http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize}
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache.setdefault(args,self.func(*args))
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
  

@memoized
def is_safe_type(ttype):
    """Test if a type is a "safe" type that we can print and
    process. Functions and classes are not, in general, simple types
    as they can contain side effecting code.

    TODO: Strictly, sequence types can contain objects which
    side-effect, although for now we call them safe. A better thing
    would be to look inside each sequence and decide whether or not
    its members are safe types.
    """
    safe = (types.NoneType,
            types.TypeType,
            types.BooleanType,
            types.IntType,
            types.LongType,
            types.FloatType,
            types.ComplexType,
            types.StringType,
            types.UnicodeType,
            types.TupleType, 
            types.ListType,
            types.DictType,
            types.DictionaryType,
            # Note that lambdas are forbidden from side-effecting
            # by the language specification.
            types.LambdaType, 
            types.GeneratorType,
            types.CodeType,
            types.ModuleType,
            types.XRangeType,
            types.SliceType,
            types.EllipsisType,
            types.BufferType,
            types.DictProxyType,
            types.NotImplementedType,
            types.StringTypes)
    if ttype in safe: return True
    return False
               

@memoized
def _is_module_stdlib(file_name):
    """Returns True if the file_name is in the lib directory.

    Source adapted from pycallgraph.py
    U{http://pycallgraph.slowchop.com/} Copyright (GPLv2) Gerald
    Kaszuba 2007
    """
    lib_path = sysconfig.get_python_lib(standard_lib=True)
    path = os.path.split(lib_path)
    if path[1] == 'site-packages':
        lib_path = path[0]
    return file_name.lower().startswith(lib_path.lower())


def _pprint_arg(argname, value):
    """Pretty-print an argument to a function, including its type.

    A special case here is the arguments to some csp types which are
    lists of CSPProcess objects.
    """
    if argname: output = argname + '='
    else: output = ''
    
    # Case 1: csp type with a list of processes as an argument.
    if value[0] is not None and hasattr(value[0], '__iter__'):
        output += '['
        for val in value:
            output += _pprint_arg('', val) + ', '
        output = output[:-2] + ']'

    # Case 2: single argument with original name with type.    
    elif value[0] is not None:
        output += repr(value[0]) + ':' + str(value[1])

    # Case 3: single anonymous argument with type.
    else:
        output += ':' + str(value[1])
    return output


def _pprint_func(func_name, args):
    """Pretty print a function call.

    Used for debugging.
    """
    output = func_name + '('

    # Case 1: No arguments.
    if not args:
        return output + ')'

    for arg in args:
        output += _pprint_arg(arg, args[arg]) + ', '
    # Remove trailing comma.
    return output[:-2] + ')'


@memoized
def _get_key(value, dictionary):
    """Reverse lookup for dictionaries.
    Given a value returns the key indexing that value in dictionary, or None.
    """
    for key in dictionary:
        if dictionary[key] == value: return key
    return None


def _find_name_in_outer_scope(bound_value, frame):
    """Given a name in the current stack frame, find the name of that
    value, where it was defined in an outer scope (or stack frame).
    """
    defined_name = ''
    while frame:
        try:
            val = _get_key(bound_value, frame.f_locals)
            if val is not None: defined_name = val
        except AttributeError:
            pass
        try:
            val = _get_key(bound_value, frame.f_globals)
            if val is not None: defined_name = val
        except AttributeError:
            pass
        finally:
            frame = frame.f_back

    return defined_name


def _get_arguments(param, frame):
    """Given a formal parameter name and a stack frame, return the
    variable name and type of the formal parameter where it was first
    defined (or, if the argument is a constant, return the constant if
    it is safe to do so and '' otherwise).
    """
    arg, ty = None, None
    code = frame.f_code

    if param not in code.co_freevars:
        bound_value = frame.f_locals[param]
    else:
        bound_value = frame.f_globals[param]

    # Deal separately with core csp classes.
    if isinstance(bound_value, csp.cspprocess.CSPProcess):
        arg, ty = (bound_value._target.__name__, type(bound_value))

    # Deal with PARallel processes.
    elif isinstance(bound_value, csp.cspprocess.Par):
        targets = []
        for proc in bound_value.procs:
            targets.append((proc._target.__name__, type(proc)))
        return targets
    elif isinstance(bound_value, csp.cspprocess.Seq):
        targets = []
        for proc in bound_value.procs:
            targets.append((proc._target.__name__, type(proc)))
        return targets
    elif isinstance(bound_value, csp.cspprocess.Alt):
        targets = []
        for guard in bound_value.guards:
            targets.append((guard._target.__name__, type(guard)))
        return targets

    # Deal with types defined outside the csp library.
    elif (bound_value is not None and
          bound_value in frame.f_locals.values()):
        if is_safe_type(type(bound_value)):
            arg, ty = (bound_value, type(bound_value))
        else:
            arg, ty = (_find_name_in_outer_scope(bound_value, frame),
                                type(bound_value))
    elif (bound_value is not None and
          bound_value in frame.f_globals.values()):
        if is_safe_type(type(bound_value)):
            arg, ty = (bound_value, type(bound_value))
        else:
            arg, ty = (_find_name_in_outer_scope(bound_value, frame),
                       type(bound_value))
    else:
        arg, ty = (_find_name_in_outer_scope(bound_value, frame),
                   type(bound_value))

    return (arg, ty)


class Tracer(object):
    """
    """

    def __init__(self):
        pass
    
    def trace(self, frame, event, arg):
        if event == 'line':
            self.trace_line(frame, event, arg)
        elif event == 'exception':
            self.trace_exn(frame, event, arg)
        elif event == 'return':
            self.trace_return(frame, event, arg)
        elif event == 'call':
            self.trace_call(frame, event, arg)
                            
    
    def trace_line(self, frame, event, arg):
        """Trace a line of source code.
        """
        pass

    def trace_exn(self, frame, event, arg):
        """Trace an exception.
        """
        pass

    def trace_return(self, frame, event, arg):
        """Trace a return value from a function.
        """
        pass

    def trace_call(self, frame, event, arg):
        """Trace a function call.
        """
        code = frame.f_code

        # Stores all the parts of a human readable name of the current call.
        full_name_list = []

        # Work out the module name
        module = inspect.getmodule(code)
        if module:
            module_name = module.__name__
            module_path = module.__file__
            # Ignore function calls from the standard library.
            if _is_module_stdlib(module_path):
                return self
            if module_name == '__main__':
                module_name = ''
        else:
            module_name = ''

        if module_name:
            full_name_list.append(module_name)

        # Work out the class name.
        try:
            class_name = frame.f_locals['self'].__class__.__name__
            full_name_list.append(class_name)
        except (KeyError, AttributeError):
            class_name = ''

        # Work out the current function or method
        func_name = code.co_name
        if func_name == '?':
            func_name = '__main__'

        full_name_list.append(func_name)

        # Create a readable representation of the current call
        full_name = '.'.join(full_name_list)

        # Ignore some internal method calls from the csp library.
        if full_name in ignore:
            return self

        # Create a list of all arguments passed to the function,
        # including defaults, with names as defined in outer scopes
        # (rather than the formal parameter list) and types.
        # func_args has pattern:
        #    formal_parameter : (defined_name, type)
        func_args = {}

        # Gather formal parameter names, their values and types.
        for i in xrange(code.co_argcount):
            func_args[code.co_varnames[i]] = None
        for param in func_args:
            func_args[param] = _get_arguments(param, frame)

        if DEBUG: print _pprint_func(full_name, func_args)

        return self

# def write_dotfile(filename='procgraph.dot'):
#     global nodes
#     global arcs
#     dot = "graph pythoncsp {\n  node [shape=ellipse];"
#     for proc in nodes:
#         dot += " " + str(proc) + ";"
#     dot += "\n"
#     for channel in arcs:
#         for i in xrange(len(arcs[channel])):
#             for j in xrange(i+1, len(arcs[channel])):
#                 dot += (str(arcs[channel][i]) + " -- " +
#                         str(arcs[channel][j]) +
#                         "  [ label=" + str(channel) + " ];\n")
#     dot += '  label = "\\n\\nCSP Process Relationships\\n";\n'
#     dot += "  fontsize=20;\n}"
#     fh = open(filename)
#     fh.write(dot)
#     fh.close()
#     return


# def write_png(infile='procgraph.dot', outfile='procgraph.png'):
#     os.system('neato -v -Goverlap=-1 -Gsplines=true -Gsep=.1 -Gstart=-1000 Gepsilon=.0000000001 -Tpng ' + infile + ' -o' + outfile)
