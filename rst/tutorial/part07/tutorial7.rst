Part 7 - Builtin guards
=======================

So far, we have only used channels to ``read()`` and ``write()`` from/to and pass to ``Alt`` objects. Other objects can be used in these ways too, and in CSP these sorts of objects are all called *guards*. The modules ``csp.guards`` and ``csp.builtins`` contain a number of basic guards and processes which can be used as building blocks for larger rograms. These are largely based on a similar library in JCSP called "plugNplay" and can be useful for quickly bootstraping programs. 

It is best to import the modules and look through their documentation, but this tutorial page covers a few of the more useful or unusual builtins with some examples.


Timer
-----

Guard which only commits to synchronisation when a timer has expired. A ``Timer`` can also be used to *sleep* a process without importing the Python ``time`` module. For example:

::

    from csp.builtins import Timer
    from csp.csp import *
    
    @process
    def foobar():
        timer = Timer()
        print '1, 2, 3, 4, ...'
        timer.sleep(2) # 2 seconds.
        print '5'


To use a timer to execute code after a specified amount of time you need to set it's ``alarm`` to trigger after a number of seconds and then pass the timer to an ``Alt``. The ``Alt`` will be able to select the timer when its alarm has triggered, like this:

::
    
    from csp.builtins import Timer
    from csp.csp import *
    
    @process
    def foobar():
        timer = Timer()
        alt = Alt(timer)
        timer.set_alarm(5)
        alt.select() # Wait 5 seconds here.
        print '5 seconds is up!'


Skip
----

Guard which will always return ``True``. Useful in ``Alt`` where the programmer wants to ensure that ``Alt.select`` will always synchronise with at least one guard.


Builtin processes
-----------------

Skip
^^^^

As well as being a guard, ``Skip`` can be used as a process which does nothing. Think of it as the CSP equivalent of ``None``:

::
    
    >>> Skip().start()
    >>> 


Blackhole
^^^^^^^^^

Read values from ``cin`` and do nothing with them.

    
Clock
^^^^^

Send ``None`` object down output channel every ``resolution`` seconds.
    

Generate
^^^^^^^^

Generate successive (+ve) `int`s and write to ``cout``. There is a similar process with the signature ``GenerateFloats(outchan, epsilon=0.1)`` which generates `float`s rather than ``int``. The argument ``epsilon`` says how far apart each floating point number should be. So the call ``GenerateFloats(outchan, epsilon=0.1)`` will write the numbers ``0.1, 0.2, 0.3, ...`` down the channel ``outchan``. 
    
    
Mux2
^^^^

Mux2 provides a fair multiplex between two input channels.

Printer
^^^^^^^

Print all values read from ``cin`` to standard out or ``out``.
    
Zeroes
^^^^^^

Writes out a stream of zeroes.


Larger examlple: a basic oscilloscope
-------------------------------------

.. image:: oscilloscope.png

The full code for the oscilloscope can be found here: :download:`here<oscilloscope.py>`. You will also need the traces code, :download:`here<traces.py>`. 


Next in the tutorial
--------------------

:doc:`../part08/tutorial8`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

