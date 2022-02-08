.. _getting_started_dev:

.. toctree::
    :glob:

***************
Getting Started
***************

This section provides instructions for setting up your development environment.  If you follow the
steps from top to bottom you should be ready to roll by the end.


Get the Source
==============

The source code for the `ghostbuster` project lives at
`github <https://github.com/assetnote/ghostbuster>`_.  
You can use `git clone` to get it.

.. code-block:: bash

   git clone https://github.com/patdaburu/bnrml

Create the Virtual Environment
==============================

You can create a virtual environment and install the project's dependencies using :ref:`make <make>`.

.. code-block:: bash

    make venv
    make install
    source venv/bin/activate

Try It Out
==========

One way to test out the environment is to run the tests.  You can do this with the `make test`
target.

.. code-block:: bash

    make test

If the tests run and pass, you're ready to roll.

Getting Answers
===============

Once the environment is set up, you can perform a quick build of this project
documentation using the `make answers` target.

.. code-block:: bash

    make answers
