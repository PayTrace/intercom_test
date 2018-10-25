.. intercom_test documentation master file, created by
   sphinx-quickstart on Wed Oct 24 11:55:15 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to intercom_test's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   modules


Using This Package
==================

:py:mod:`intercom_test` provides :py:class:`~intercom_test.framework.InterfaceCaseProvider`
to iterate over test cases defined in YAML files.  With the additional use of a
*case_augmenter* -- either an :py:class:`~intercom_test.framework.HTTPCaseAugmenter`,
a :py:class:`~intercom_test.framework.RPCCaseAugmenter`, or your own class
derived from :py:class:`~intercom_test.framework.CaseAugmenter` -- the
:py:class:`~intercom_test.framework.InterfaceCaseProvider` can add more data
from a different directory to any test case; this supports decoupling a *service
provider's* implementation details necessary to passing the given test case from
the request and response information needed by both the *consumer* and the
*provider*.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
