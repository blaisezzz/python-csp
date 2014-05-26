Part 4 - Poisoning channels and terminating processes
=====================================================

A set of communicating processes can be terminated by "poisoning" any of the channels used by those processes. This can be achieved by calling the ``poison()`` method on any channel. For example:

::

    >>> import time
    >>> import random
    >>> @process
    ... def send5(cout):
    ...     for i in xrange(5):
    ...             print 'send5 sending:', i
    ...             cout.write(i)
    ...             time.sleep(random.random() * 5)
    ...     return
    ... 
    >>> @process
    ... def recv(cin):
    ...     for i in xrange(5):
    ...             data = cin.read()
    ...             print 'recv got:', data
    ...             time.sleep(random.random() * 5)
    ...     return
    ... 
    >>> @process
    ... def interrupt(chan):
    ...     time.sleep(random.random() * 7)
    ...     print 'Poisoning channel:', chan.name
    ...     chan.poison()
    ...     return
    ... 
    >>> doomed = Channel()
    >>> Par(send5(doomed), recv(doomed), interrupt(doomed)).start()
    send5 sending: 0
    recv got: 0
    send5 sending: 1
    recv got: 1
    send5 sending: 2
    recv got: 2
    send5 sending: 3
    recv got: 3
    Poisoning channel: 5c906e38-5559-11df-8503-002421449824
    send5 sending: 4
    >>> 


A larger example
----------------

The second example tries to demonstrate the poisoning of all channels that are related to primary channel. In this case merchant is watching what customers are going to send and merchant's wife is watching what customer's children are going to send. 

::

    import time
    import random
    @process
    def customer_child(cchildout, n):
    	for i in xrange(3):
    		print "Customer's "+str(n)+" child sending "+str(i)
    		cchildout.write(i)
    		time.sleep(random.random() * 3)
    	return
    
    @process
    def customer(cparentout, cchildout, n):
    	for i in xrange(5):
    		print 'Customer '+str(n)+" sending "+str(i)
    		Par(customer_child(cchildout, n)).start()
    		cparentout.write(i)
    		time.sleep(random.random() * 5)
    	return
    
    @process
    def merchant(cin):
    	for i in xrange(15):
    		data = cin.read()
    		print 'Merchant got:', data
    		time.sleep(random.random() * 5)
    	return
    
    @process
    def merchantswife(cin):
    	for i in xrange(15):
    		data = cin.read()
    		print "Merchant's wife got: ", data
    		time.sleep(random.random() * 4)
    	return
    
    @process
    def terminator(chan):
    	time.sleep(10)
    	print 'Terminator is killing channel:', chan.name
    	chan.poison()
    	return
    
    doomed = Channel()
    doomed_children = Channel()
    Par(customer(doomed, doomed_children, 1),\
        merchant(doomed), \
        merchantswife(doomed_children), \
        customer(doomed, doomed_children, 2), \
        customer(doomed, doomed_children, 3), \
        terminator(doomed)).start()


Exercises
---------

Writeme!


Next in the tutorial
--------------------

:doc:`../part05/tutorial5`

..

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

