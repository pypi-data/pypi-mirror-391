Timeline Toggle Feature
=======================

The timeline plugin now supports an interactive toggle switch to switch between vertical and horizontal layouts!

Basic Toggle Example
--------------------

Here's a timeline with a toggle switch. Click the switch to change layouts:

.. timeline::
   :toggle:
   :start-year: 2020
   :end-year: 2024

   2020-01 Project Started
   ~~~
   The beginning of our journey.

   2020-06 First Milestone
   ~~~
   Reached our first target.

   2021-03 Major Release
   ~~~
   Version 1.0 shipped successfully.

   2022-01 Series A Funding
   ~~~
   Raised significant investment.

   2023-06 Expansion Phase
   ~~~
   Expanded to new markets.

   2024-11 Current Status
   ~~~
   Continuing to grow and innovate.


Toggle with Vertical Default
-----------------------------

By default, the toggle starts with vertical layout:

.. timeline::
   :toggle:
   :layout: vertical
   :start-year: 2022
   :end-year: 2024

   2022-01 Q1 2022
   ~~~
   Started new quarter.

   2022-06 Mid-Year
   ~~~
   Half-way through the year.

   2023-01 Q1 2023
   ~~~
   Moving forward.

   2024-01 Q1 2024
   ~~~
   Current year.


Toggle with Horizontal Default
-------------------------------

You can also set horizontal as the default layout:

.. timeline::
   :toggle:
   :layout: horizontal
   :start-year: 2020
   :end-year: 2024
   :height: 450px

   2020 Foundation
   ~~~
   Company founded.

   2021 Growth
   ~~~
   Rapid expansion.

   2022 Consolidation
   ~~~
   Market leadership.

   2023 Innovation
   ~~~
   New product lines.

   2024 Global
   ~~~
   International presence.


Product Development Timeline with Toggle
-----------------------------------------

Perfect for showing development milestones:

.. timeline::
   :toggle:
   :start-year: 2023
   :end-year: 2024

   2023-01 Design Phase
   ~~~
   Created mockups and wireframes.
   User research conducted.

   2023-03 Development Begins
   ~~~
   Core architecture established.
   Development team assembled.

   2023-06 Alpha Release
   ~~~
   Internal testing started.
   Early feedback collected.

   2023-09 Beta Release
   ~~~
   Limited public beta launched.
   Community feedback positive.

   2024-01 Production Release
   ~~~
   Official public launch.
   Marketing campaign launched.

   2024-06 First Update
   ~~~
   Feature requests implemented.
   Performance optimizations.

   2024-09 v2.0 Planning
   ~~~
   Planning next major version.
   Gathering feature requests.


Company Milestones with Toggle
------------------------------

Track major events with the ability to switch views:

.. timeline::
   :toggle:
   :layout: vertical
   :start-year: 2015
   :end-year: 2024

   2015 Founded
   ~~~
   Company officially established.

   2016-06 First Product
   ~~~
   Launched initial product offering.

   2017 Series A
   ~~~
   $2M funding round.

   2018-03 Series B
   ~~~
   $10M funding round.

   2019 Profitability
   ~~~
   Reached profitability milestone.

   2020 Pandemic Pivot
   ~~~
   Adapted business model.

   2021 Series C
   ~~~
   $50M funding round.

   2022 Expansion
   ~~~
   Opened 5 new offices.

   2023 Strategic Partnerships
   ~~~
   Partnered with major corporations.

   2024 IPO Preparation
   ~~~
   Preparing for public offering.


How the Toggle Works
--------------------

The toggle switch is a smooth, interactive control that allows you to:

1. **Default Layout**: Set either vertical or horizontal as the default using `:layout:`
2. **Switch Views**: Click the toggle switch to alternate between layouts
3. **Smooth Transitions**: Layouts switch smoothly with CSS transitions
4. **Responsive**: Works on all screen sizes
5. **No Page Reload**: Changes happen instantly in the browser

The toggle remembers your preference for the current page session.


Usage
-----

To add a toggle to your timeline, simply add the `:toggle:` option:

.. code-block:: rst

   .. timeline::
      :toggle:
      :start-year: 2020
      :end-year: 2024

      2020 Event 1
      ~~~
      Description.

      2024 Event 2
      ~~~
      More details.


Combine with Other Options
---------------------------

The toggle can be combined with any other timeline options:

.. code-block:: rst

   .. timeline::
      :toggle:
      :layout: horizontal
      :start-year: 2020
      :end-year: 2024
      :height: 500px
      :width: 90%

      2020 Event
      ~~~
      Details here.


Benefits
--------

- **Better UX**: Users can choose their preferred view
- **Flexible Layouts**: Show timelines in different ways
- **Interactive**: Engages viewers more than static content
- **Works Everywhere**: No special JavaScript frameworks needed
- **Accessible**: Works with keyboard navigation
- **Mobile Friendly**: Touch-friendly toggle on all devices


Browser Compatibility
---------------------

The toggle feature works on:

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari (iOS)
- Chrome Mobile (Android)
- All modern browsers


Performance
-----------

- Minimal JavaScript (pure DOM manipulation)
- No external dependencies
- Smooth CSS transitions
- Lazy rendering of hidden layout


Tips & Tricks
-------------

**Tip 1: Default to Horizontal for Wide Data**

For timelines with many years, start with horizontal layout:

.. code-block:: rst

   .. timeline::
      :toggle:
      :layout: horizontal
      :start-year: 2000
      :end-year: 2024

**Tip 2: Large Timelines**

For very large timelines, consider using horizontal as default:

.. code-block:: rst

   .. timeline::
      :toggle:
      :layout: horizontal
      :height: 600px

**Tip 3: Mobile Friendly**

The toggle works great on mobile - vertical is usually better for small screens:

.. code-block:: rst

   .. timeline::
      :toggle:
      :layout: vertical
      :height: 100vh

**Tip 4: Multiple Timelines**

You can have multiple timelines with toggles on the same page:

.. code-block:: rst

   .. timeline::
      :toggle:
      :layout: vertical

      2024-01 Timeline 1
      ~~~
      First timeline.

   .. timeline::
      :toggle:
      :layout: horizontal

      2024-01 Timeline 2
      ~~~
      Second timeline.

Each toggle works independently!
