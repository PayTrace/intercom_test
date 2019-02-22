==============================
``icy-test`` Command Line Tool
==============================

Not every test harness is written in Python.  To accommodate this, the
:doc:`intercom_test package </index>` can be installed to provide a command
line tool call ``icy-test`` that provides access to the core functionality.


Installation
------------

To install the ``icy-test`` command line tool, simply install 
:doc:`intercom_test package </index>` with the `[cli]` *extra*, e.g.::

  pip install intercom_test[cli]

This creates a command line tool named ``icy-test``, which can be run with the
``--help`` flag to get usage information.  This information will be the most
recent and detailed available.


Configuration File
------------------

``icy-test`` needs a configuration file to provide information that would,
in a typical Python testing setting, be provided as parameters to the
:py:class:`~intercom_test.framework.InterfaceCaseProvider` constructor.
The path to this file is specified with the ``-c`` or ``--config`` flag when
running ``icy-test``.

A text-mode helper for building a configuration file (which is a YAML file,
usually with a ``.yml`` extension) is provided as ``icy-test init``, and requires
specifying a config file using one of the options mentioned above.


Consuming Test Cases
--------------------

The main use of ``icy-test`` is to access the test cases.  These are available
in the output of ``icy-test enumerate`` in either a stream of YAML documents
(one per test case) or as `JSON Lines`_ (each line contains a JSON document).


Committing Augmentation Data Updates
------------------------------------

Where :py:class:`~intercom_test.framework.InterfaceCaseProvider` used within a
Python testing framework can provide *case runners* that can automatically
update the compact augmentation data files when all test cases have passed,
no such facility is easily implemented when consuming the test cases from
another process and/or language.  The augmentation data changes embodied in the
*update files* need to be explicitly committed to the *compact files* by running
``icy-test commitupdates``.


Merging Interface Extension Test Cases To Main File
---------------------------------------------------

Use the ``icy-test mergecases`` subcommand to invoke
:py:meth:`intercom_test.framework.InterfaceCaseProvider.merge_test_extensions`
with appropriate setup taken from the ``icy-test`` configuration file.


.. _JSON Lines: http://jsonlines.org
