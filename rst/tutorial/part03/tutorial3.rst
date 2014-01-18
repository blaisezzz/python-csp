Part 3 - Channels
=================

So far, all the example programs in this tutorial have shown processes running independently of one another. For most applications this is too naive, we need a way for processes to communicate with one another to exchange data. In CSP programming this is done with **message passing** over *channels*. It's a good idea to try and think of channels as being pipes which you can use to transport information between processes and remember that process cannot share any data directly.

A CSP channel can be created with the ``Channel`` class:

::

    >>> c = Channel()
    >>>


Each ``Channel`` object should have a unique name:

::

    >>> print c.name
    1ca98e40-5558-11df-8e5b-002421449824
    >>> 


The ``Channel`` object can then be passed as an argument to any CSP process and then be used either to read (using the ``.read()`` method) or to write (using the `.write()` method). The code below is the simplest *Hello world!* with channels that shows how they can be used:

::

    >>> @process
    ... def send(cout, data):
    ...     cout.write(data)
    ... 
    >>> @process
    ... def recv(cin):
    ...     print 'Got:', cin.read()
    ... 
    >>> c = Channel()
    >>> send(c, 100) & recv(c)
    Got: 100
    <Par(Par-3, initial)>
    >>> 


To understand how channels work, think of them as being analagous to making a telephone call. If you ring someone, you are offering to communicate with them. If they accept that offer, they pick up their own phone and talk to you. Both of you are talking at the same time (sychronously) and you both have to end the call at the same time and carry on with your day. This is exactly how CSP channels work, a writer process makes an offer to exchange some data with a reader process, and when a reader process accepts that offer, the data is passed along the channel, sychronously, then both processes complete and carry on with their computation.


A larger example: Mandelbrot set
--------------------------------

.. image:: mandelbrot.png

The *producer/consumer* or *worker/farmer* model is a common pattern in concurrent and parallel programming. The idea is to split a large, time consuming task into smaller, quicker tasks, each handled by a separate process. In CSP terms, this usually means having one "consumer" process each of which is connected via a channel to many "producer" processes which perform some computation. The consumer must then gather the data sent by each producer and put it together to produce the final result of the program.


Generating the Mandelbrot set is a common example of the producer/consumer pattern. In the example below, we split the image into columns of pixels and each producer process will send back a column of RGB image data to the consumer. The consumer will then need to collate all the image data and draw it with PyGame. 


The full code for the mandelbrot generator can be found :download:`here <mandelbrot.py>` but in this tutorial page we will concentrate on the parts of the program
that relate to CSP.


So, the producer process needs to know which column of data it is producing image data for, the width and height of that column and it needs a channel to write its result to:


::

    @process 
    def mandelbrot(xcoord, (width, height), cout):
        # Create a list of black RGB triples.
        imgcolumn = [0. for i in range(height)]
        for ycoord in range(height):
            # Do some maths!
        cout.write((xcoord, imgcolumn))
        return
    

And the consumer needs to read the data from every one of these channels and combine them to create the whole image. Here, ``size`` is the size of the image that is being produced and ``cins`` is the list of channels that connect this consumer to the producer processes:


::

    @process
    def consume(size, cins):
        # Set-up PyGame.
        pixmap = ... # Blit buffer.
        for i in range(len(cins)):
    	    xcoord, column = cins[i].read()
            # Update column of blit buffer
            pixmap[xcoord] = column
            # Update image on screen.


Next, we need to run all these processes in parallel. In the code below ``size`` is the width and height of the image we want to create:

::

    @process
    def main(size):
        channels, processes = [], []
        for x in range(size[0]):
            channels.append(Channel())
            processes.append(mandelbrot(x, size, channels[x]))
        processes.insert(0, consume(size, channels))
        mandel = Par(*processes).start()
        return
    

Problems with servicing channels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It might occur to you that when we iterated over all the read channels in a ``for`` loop like this:

::

    for chan in cins:
        xcoord, column = chan.read()


that this might be unnecessarily inefficient. Some of the producer processes might finish faster than others, but still be waiting for the ``for`` loop to service them. In TutorialPage5 we will see how python-csp provides facilities to solve this problem.


Exercises
---------

Writeme!


Next in the tutorial
--------------------

:doc:`../part04/tutorial4`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

