Part 1 - creating and using processes
=====================================

CSP processes
-------------

In an object-oriented programming language like Java or Python, "everything" is an object. In a functional language like Haskell, OCaml or Standard ML, "everything" is a function. In python-csp "everything" is a process. This part of the tutorial will take you through the basics of creating a python-csp process with some examples. We end with a rather large  (but useful!) example program -- a web server -- which you can also find :download:`here <webserver.py>`.

Importing the CSP libraries
---------------------------

There are currently two forms of the python-csp library, one based on threads and one based on processes. Each has pros and cons. The processes version allows you to take advantage of multicore, but some things will be a little slower with processes. We're working on something to speed things up in a later release ;)

To import the library import the module ``csp.csp``:

::

    from csp.csp import *


This will try to import the "best" available implementation of the library for your environment. If you which to explicitly choose one variation of the library over another, then set the environment variable ``CSP`` in your OS to either ``PROCESSES`` or ``THREADS``. For example, on UNIX systems such as Linux you can say:

::

    export CSP=PROCESSES


Note that we're using ``import *`` which PyLint and other tools will warn about. The reason is that python-csp is intended to be an internal `domain specific language (DSL) <http://en.wikipedia.org/wiki/Domain-specific_language>`_ built into Python. If you use python-csp, you will need to slightly change the style in  which you write your code. Hopefully, we've designed python-csp in such a way that it doesn't pollute your namespace too much, but if you don't like ``import *`` then just stick to something like:

::

    import csp.csp as csp

and prefix all names from package with ``csp``.


Processes
---------

We said above that in python-csp "everything" is a process, so what is a process? You can think of this in two ways. If you have written concurrent or parallel programs before, or you know about operating systems, then you can think of a CSP process as being just like an individual OS process -- that is, an individual program that has it's own bit of memory to work with.

If you're new to all this concurrency stuff, then think of each process as being a separate program. Each process runs independently from all the others, so in a typical python-csp program you will write many processes which are all running at the same time. Later on in this tutorial we'll look at different ways to combine processes and share information between them, but for now, we'll just look at how to create and run individual processes.


Creating a process with decorators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two ways to create a new CSP process. Firstly, you can use the ``@process`` decorator to convert an ordinary Python function definition into a CSP process, like this:

::

    >>> @process
    ... def hello():
    ...      print 'hello from python-csp'
    ... 


Once you have done that, you need to start the process running. For example, in the code above we create a function ``hello`` which is decorated by the ``@processs`` decorator to turn it into a CSP process. We can still call the function ``hello`` and when we do we get back a special object (actually an instance of the ``CSPProcess`` class) which represents the CSP process we have created:

::

    >>> h = hello() # h is an instance of CSPProcess


At this stage, when we have called ``hello()``, our process is not yet running, it's waiting for us to start it. This is a bit like having a link to a program on your desktop, the link is there so the program exists, but until you double-click on it the program isn't actually running. So, to run the CSP process, we need to do something else, we call the method ``start()``, either in two stages:

::

    >>> h = hello() # h is a CSPProcess object
    >>> h.start()
    hello from python-csp
    >>> 


or just by saying ``hello().start()``, like we do here:

::

    hello().start()
    hello from python-csp
    >>>


Creating a process with objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't want to use the ``@process`` decorator you can create a ``CSPProcess`` object directly and pass a function (and its arguments) to the ``CSPProcess`` constructor:

::

    >>> def foo(n):
    ...     print n
    ...     return
    ... 
    >>> p = CSPProcess(foo, 100)
    >>> p.start()
    100
    >>> 


A note on objects
^^^^^^^^^^^^^^^^^

At the top of this page we said that using python-csp would change your Python coding style. One aspect of this is your use of objects and classes. So far we have only seen processes created from Python functions. There is a very good reason for this -- the intention of python-csp (and all CSP systems) is to make concurrent and parallel programming **easier** by making it impossible to cause certain sorts of errors (in this case **race conditions**) and difficult to cause other sorts of errors (in this case **deadlocks**). The way that CSP does this is by restricting the ways in which processes can share information. To stick with the CSP way of doing things, you need to make sure that you don't try to share information between processes in any ad-hoc ways of your own. So, although methods in Python are, strictly speaking, really just functions *do not* be tempted to use a method to create a CSP process. *Always* use functions, then you won't be tempted to share data between processes via object and class fields. If you do try this, almost certainly your code will break in odd ways that are difficult to fix.


Server processes
----------------

A common idiom in CSP style programming is to have many processes which all run in infinite loops (we'll find out how to terminate such processes in :doc:`../part04/tutorial4`. The python-csp library has some convenient types for such "server" processes  to make this easy. Of course, you could just create a normal process with the ``@process`` decorator or the ``CSPProcess`` type, but the advantage of using server processes is that the facilities that python-csp provides for debugging can generate correct and useful information if you do. 

Like ordinary processes, server processes can be created using a decorator, ``@forever``, or a class ``CSPServer``. The function that is either decorated with ``@forever`` or passed to ``CSPServer`` should define generators, that is, they should ``yield`` every time they iterate. Some basic examples follow below:

Server processes using decorators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    >>> @forever
    ... def integers():
    ...     n = 0
    ...     while (n <= 1000000): # 1000000 numbers seem enough for all practical means
    ...             print n
    ...             n += 1
    ...             yield
    ... 
    >>> integers().start()
    >>> 0
    1
    2
    3
    4
    5
    ...
    KeyboardInterrupt
    >>>


Server processes using objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    >>> def integers():
    ...     n = 0
    ...     while (n <= 1000000):
    ...             print n
    ...             n += 1
    ...             yield
    ... 
    >>> i = CSPServer(integers)
    >>> i.start()
    >>> 0
    1
    2
    3
    4
    5
    ...
    KeyboardInterrupt
    >>>


Larger example: a basic web server
----------------------------------

So far we have only looked at toy examples of python-csp programs. In this section we will build a more useful program - a basic web server. We will assume here that you already know a bit about how sockets work. If not, read the `socket howto <http://docs.python.org/howto/sockets.html>`_ and come back...

HTTP basics
^^^^^^^^^^^

A web server is a very simple example of a concurrent or parallel system. It performs two simple functions: it listens to requests from clients (web browsers) and it sends back responses. Importantly, each request and response between a client and the server should be handled concurrently, but no two requests need to share any data, which keeps things simple.

Web servers and clients need to use a common language to structure their requests and responses and this is called HTTP (Hypertext Transfer Protocol). A typical request / response would look like this:

::

    GET /index.html HTTP/1.1
    User-Agent: Mozilla/5.0


This is a string sent by a web browser (or other client) and it tells us a couple of things. Firstly the ``GET`` at the front says that the client is asking to "get" an object. Usually this means that the client wants a file on the web server to be sent back to it. The next piece of text ``/index.html`` tells us which file is being requested, in this case ``index.html`` and where it is, in this case in the root directory of the web servers files. The rest of the text, and anything else that is sent, we don't really need to worry about, but if you want to know more `try here <http://www.w3.org/Protocols/>`_.

Next, the web server has to send a response. In the case of the example request above, we can make two responses, either we find the requested file and send it back (called a ``200 OK`` response) or we can't find the file (called a ``404 Not Found`` response). Either way we can send back a response line and some HTML (and for now, we will only worry about HTML files):

::

    HTTP/1.0 200 OK
    Content-Type: text/html
    Content-Length: 1024
    
    
    <html><head><title>My server</title></head>
    <body><h1>My CSP server!</h1></body></html>


This says we are using version 1.0 of the HTTP protocol, we are sending back an HTML file of length 1024 and we have given the contents of that file. Simple!


Writing the server loop
^^^^^^^^^^^^^^^^^^^^^^^

A web server is a simple creature, it just has to listen out for connections to new clients and send back a response. In  our python-csp web server, we will have one process to deal with accepting new client connections, and other processes to handle each individual response that is sent to the clients. 

First, the server loop. This accepts new TCP socket connections, reads the HTTP request line and creates a new CSP process to handle each response:

::

    import socket
    
    @process
    def server(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)    
        while True:
            conn_sock, conn_addr = sock.accept()
            request = conn_sock.recv(4096).strip()
            if request.startswith('GET'):
                handler_ok(request, conn_sock).start()
            else:
                handler_not_found(request, conn_sock).start()


We are cheating a little here, just to make the example simple, in that if the request line starts with ``GET`` we will send back a static HTML page. If not, we will send back a ``404 Not Found`` response. Strictly, this is not correct behaviour -- any ``GET`` request should be handled by replying with a file on disk (not a static HTML page) and that file might be of any MIME type (for example, it might be a JPEG image, not an HTML page). Also, the process that deals with finding files should be the one that chooses whether to respond with a ``404 Not Found`` error. However, the purpose of this tutorial is to teach python-csp, not HTTP, so we'll gloss over these details.


A helper function for constructing HTTP responses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now we have a server which deals with client connections, we will need to think about sending responses. Since we are going to deal with two sorts of response, it would be sensible to factor out the construction of simple responses into a function, like this:

::

    import time
    
    def response(code, reason, page):
        html = """
        <html>
        <head><title>%i %s</title></head>
        <body>
        %s
    	<hr/>
    	<p><strong>Date:</strong> %s</p>
        </body>
        </html>
        """ % (code, reason, page, time.ctime())
        template = """HTTP/1.0 %i %s
        Content-Type: text/html
    	Content-Length: %i
    
    
        %s
        """ % (code, reason, len(html), html)
        return template


This creates an HTTP response, with a given code (such as `200`) and reason (such as `OK` or `Not Found`) and some HTML to write in a web page. We have also appended the current time and date, this is really for debugging.

Handling a 200 OK response
^^^^^^^^^^^^^^^^^^^^^^^^^^

Next we need to handle a "success" response. This will also be done in a CSP process (so, many different browser requests can be handled concurrently). The only other thing to note is that we *must* correctly close the connection socket, otherwise bad things will happen:

::

    @process
    def handler_ok(request, conn_sock):
        page = '<h1>My python-csp web server!</h1>'
        page += '<p><strong>You asked for:</strong><pre>%s</pre></p>' % request
        conn_sock.send(response(200, 'OK', page))
        conn_sock.shutdown(socket.SHUT_RDWR)
        conn_sock.close()
        return


Handling a 404 Not Found response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Handling the ``Not Found`` case is much the same as the ``Success`` case, but we include it here for completeness:

::

    @process
    def handler_not_found(request, conn_sock):
        """Handle a single HTTP 404 Not Found request.
        """
        page = '<h1>Cannot find your file</h1>'
        page += '<p><strong>You asked for:</strong><pre>%s</pre></p>' % request
        conn_sock.send(response(404, 'Not Found', page))
        conn_sock.shutdown(socket.SHUT_RDWR)
        conn_sock.close()
        return


Putting it all together
^^^^^^^^^^^^^^^^^^^^^^^

So, that's it, a concurrent web server in around 50 lines of python-csp code. To put it all together we just start a server process running:

::

    if __name__ == '__main__':
        host = ''
        port = 8888
        server(host, port).start()


and run the module from the command line (or your IDE):

::

    $ python webserver.py

and to test the server open up your favourite web browser and navigate to `<http://127.0.0.1:8888/>`_ and you should see a web page a little like this:

::
    
    My python-csp web server!
    
    You asked for:
    
    GET / HTTP/1.1
    Host: 127.0.0.1:8888
    Connection: keep-alive
    User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.366.2 Safari/533.4
    Cache-Control: max-age=0
    Accept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: en-GB,en-US;q=0.8,en;q=0.6
    Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3
    -------------------------------------------------
    Date: Tue Apr 6 02:19:07 2010


Exercises
---------
  
-  Add in the missing features of the web server example:
  - Serving real files on disk
  - Serving different `MIME types <http://docs.python.org/library/mimetypes.html>`_
  - Giving the full range of `HTTP response codes <http://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_
  - Implementing the other `HTTP verbs <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_, such as ``PUT`` which allows your server to deal with web forms


Next in the tutorial
--------------------

:doc:`../part02/tutorial2`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
