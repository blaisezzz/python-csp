Part 5 - Choosing between channel reads with Alt
================================================

python-csp process will often have access to several different channels, or other guard types such as timer guards, and will have to choose one of them to read from. For example, in a producer/consumer or worker/farmer model, many producer or worker processes will be writing values to channels and one consumer or farmer process will be aggregating them in some way. It would be inefficient for the consumer or farmer to read from each channel in turn, as some channels might take longer than others. Instead, python-csp provides support for ALTing (or ALTernating), which enables a process to read from the first channel (or timer, or other guard) in a list to become ready.


Using the choice operator
-------------------------

The simplest way to choose between channels (or other guards) is to use choice operator: ``|`` as in the example below:

::

    >>> @process
    ... def send_msg(chan, msg):
    ...     chan.write(msg)
    ... 
    >>> @process
    ... def choice(chan1, chan2):
    ...     # Choice chooses a channel on which to call read()
    ...     print chan1 | chan2
    ...     print chan1 | chan2
    ... 
    >>> c1, c2 = Channel(), Channel()
    >>> choice(c1, c2) // (send_msg(c1, 'yes'), send_msg(c2, 'no'))
    yes
    no
    <Par(Par-8, initial)>
    >>>


Alt objects
^^^^^^^^^^^

Secondly, you can create an ``Alt`` object explicitly, and call its ``select()`` method to perform a channel read on the next available channel. If more than one channel is available to read from, then an available channel is chosen at random (for this reason, ALTing is sometimes called *non-deterministic choice*:

::

    >>> @process
    ... def send_msg(chan, msg):
    ...     chan.write(msg)
    ... 
    >>> @process
    ... def alt_example(chan1, chan2):
    ...     alt = Alt(chan1, chan2)
    ...     print alt.select()
    ...     print alt.select()
    ... 
    >>> c1, c2 = Channel(), Channel()
    >>> Par(send_msg(c1, 'yes'), send_msg(c2, 'no'), alt_example(c1, c2)).start()
    yes
    no
    >>>


Alternatives to the select method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the ``select()`` method, which chooses an available guard at random, ``Alt`` provides two similar methods, ``fair_select()`` and ``pri_select()``. ``fair_select()`` will choose not to select the previously selected guard, unless it is the only guard available. This ensures that no guard will be starved twice in a row. ``pri_select()`` will select available channels in the order in which they were passed to the ``Alt()`` constructor, giving a simple implementation of guard priority.

Lastly, ``Alt()`` can be used with the repetition operator ``*`` to create a generator:

::

    >>> @process
    ... def send_msg(chan, msg):
    ...     chan.write(msg)
    ... 
    >>> @process
    ... def gen_example(chan1, chan2):
    ...     gen = Alt(chan1, chan2) * 2
    ...     print gen.next()
    ...     print gen.next()
    ... 
    >>> c1, c2 = Channel(), Channel()
    >>> Par(send_msg(c1, 'yes'), send_msg(c2, 'no'), gen_example(c1, c2)).start()
    yes
    no
    >>> 



Fixing the Mandelbrot generator
-------------------------------

In :doc:`../part03/tutorial3` we described a producer/consumer architecture for generating pictures of the Mandelbrot set. There, we used a crude ``for`` loop for the consumer process to iterate over input channels and read from them. We can now improve this code and, using ``Alt``, make sure that channel reads are serviced when the reads are ready to complete:


::
    
    @process
    def consume(size, cins):
        # Set-up PyGame.
        pixmap = ... # Blit buffer.
        gen = len(cins) * Alt(*cins)
        for i in range(len(cins)):
            xcoord, column = gen.next()
            # Update column of blit buffer
            pixmap[xcoord] = column
            # Update image on screen.


A larger example
----------------

Writeme!


Exercises
---------

Writeme!


Next in the tutorial
--------------------

:doc:`../part07/tutorial7`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

