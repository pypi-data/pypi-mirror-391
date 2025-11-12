Sphinx TimeTravel Plugin - Examples
===================================

Welcome to the TimeTravel plugin documentation. This guide demonstrates how to use the timeline directive.

.. toctree::
   :maxdepth: 2

   vertical_timeline
   horizontal_timeline
   toggle_feature
   advanced_examples


Introduction
------------

The TimeTravel plugin allows you to create beautiful, interactive timelines in your Sphinx documentation.
Timelines can display events with year/month resolution and support multiple layout options.

Quick Start
-----------

Add the extension to your ``conf.py``:

.. code-block:: python

    extensions = [
        'sphinx_timetravel',
    ]

Then use the directive in your RST files:

.. code-block:: rst

    .. timeline::

       2024-01 First Event
       ~~~
       Description of the event.

       2024-06 Second Event
       ~~~
       More details here.
