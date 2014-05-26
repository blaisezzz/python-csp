Part 2 - CSP as a process algebra
=================================

Just like there  are different ways to combine  numbers with operators such as  ``+``, ``-``, ``*``  and ``/``, there  are different ways  to combine python-csp processes.


Running processes in sequence
-----------------------------

There are two ways to run processes in sequence.  Firstly, given two (or more) processes you can sequence them with the ``>`` operator, like this:

::

    >>> @process
    ... def foo(n):
    ... import time
    ... print n
    ... time.sleep(0.2)
    ... print n + 1
    ... time.sleep(0.2)
    ... print n + 2
    ... 
    >>> foo(100) > foo(200) > foo(300)
    n: 100
    n: 101
    n: 102
    n: 200
    n: 201
    n: 202
    n: 300
    n: 301
    n: 302
    <Seq(Seq-14, initial)>
    >>> 
    >>> 


Secondly, you can create a ``Seq`` object which is a sort of CSP process and start that process manually:

::

    >>> s = Seq(foo(400), foo(500), foo(600))
    >>> s.start()
    n: 400
    n: 401
    n: 402
    n: 500
    n: 501
    n: 502
    n: 600
    n: 601
    n: 602
    >>> 


Parallel processes
------------------

There are two ways to run processes in parallel.  Firstly, given two (or more) processes you can parallelize them with the ``//`` operator, like this:

::

    >>> @process
    ... def foo(n):
    ... import time
    ... print n
    ... time.sleep(0.2)
    ... print n + 1
    ... time.sleep(0.2)
    ... print n + 2
    ... 
    >>> foo(100) // (foo(200), foo(300))
    n: 100
    n: 200
    n: 300
    n: 101
    n: 201
    n: 301
    n: 102
    n: 202
    n: 302
    <Par(Par-5, initial)>
    >>> 

Notice that the ``//`` operator is a synthetic sugar that takes a CSPProcess on the left hand side and a sequence of processes on the right hand side.

Alternatively, you can create a ``Par`` object which is a sort of CSP process and start that process manually:

::

    >>> p = Par(foo(100), foo(200), foo(300))
    >>> p.start()
    n: 100
    n: 200
    n: 300
    n: 101
    n: 201
    n: 301
    n: 102
    n: 202
    n: 302
    >>> 

Repeated processes
------------------

If you want to a single process to run to completion many times, you can use the ``*`` operator:

::

    >>> @process
    ... def foo():
    ...     print 'hello world!'
    ... 
    >>> foo() * 3
    hello world!
    hello world!
    hello world!
    >>> 


You can also say:

::

    3 * foo()

with the same effect.


A larger example: Word counts on a whole directory
--------------------------------------------------

In this example we will use ``Par`` to concurrently process all files in a directory and print out their word counts. We just need two sorts of processes for this, one which counts all the words in a single file, and another which finds all the files in a given directory and runs the word count process on them. The first process is simple:

::

    @process
    def word_count(filename):
        fd = file(filename)
        words = [line.split() for line in fd]
        fd.close()
        print '%s contains %i words.' % (filename, len(words))


The second process is a bit more complicated. We want to know about every file in the given directory, but we don't want to know about directories and other things that aren't really files, so we need a bit of logic to do that. After that, we just need to use ``Par`` to process all our files in parallel:

::

    @process
    def directory_count(path):
        import glob
        import os.path
        import sys
        # Test if directory exists
        if not os.path.exists(path):
            print '%s does not exist. Exiting.' % path
            sys.exit(1)
        # Get all filenames in directory
        paths = glob.glob(path + '/*')
        files = [path for path in paths if not os.path.isdir(path) and os.path.isfile(path)]
        procs = [word_count(fd) for fd in files]
        Par(*procs).start()
 

This program gives output like this:

::

    $ python tutorial/part02/filecount.py .
    ./setup.py contains 37 words.
    ./MANIFEST.in contains 6 words.
    ./maketags.sh contains 3 words.
    ./setup.cfg contains 3 words.
    ./LICENSE contains 339 words.
    ./ChangeLog contains 40 words.
    ./Makefile contains 91 words.
    ./make.bat contains 112 words.
    ./TAGS contains 954 words.
    ./BUCKETS.pdf contains 616 words.
    ./README.html contains 92 words.
    ./README contains 72 words.
    $

    
This is a rather simplistic example for a couple of reasons. In most concurrent or parallel programming you really need processes to pass data between themselves. For example, a more sophisticated version of our program would have ``word_count`` processes and pass their word counts to a separate process which would print everything to the console. This relies on the operating system to print each line of our output separately, even though the processes who are printing are running concurrently and might interfere with each other. We will learn how to pass messages between processes and improve this code in :doc:`../part03/tutorial3`.


Exercises
---------

WRITEME!


Next in the tutorial
--------------------

:doc:`../part03/tutorial3`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

