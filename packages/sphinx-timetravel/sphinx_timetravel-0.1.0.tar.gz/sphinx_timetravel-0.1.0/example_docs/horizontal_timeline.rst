Horizontal Timeline
===================

Horizontal timelines use an SVG-based visualization showing events along a year axis.
This layout is ideal when you want to emphasize the year-by-year progression.

Basic Horizontal Timeline
-------------------------

Here's a simple horizontal timeline:

.. timeline::
   :layout: horizontal
   :start-year: 2020
   :end-year: 2024

   2020 Project Start
   ~~~
   Initial concept and planning.

   2021-06 Version 1.0
   ~~~
   Major release with core features.

   2023 Growth Phase
   ~~~
   Significant user and revenue growth.

   2024 Maturity
   ~~~
   Stable platform with enterprise features.


Multi-Year Overview
-------------------

Track milestones across a 5-year period:

.. timeline::
   :layout: horizontal
   :start-year: 2020
   :end-year: 2024
   :height: 400px

   2020 Foundation
   ~~~
   Company founded.
   Initial product development began.

   2020-06 Beta Launch
   ~~~
   Beta testing phase started.

   2021 Public Release
   ~~~
   Official product launch.

   2021-09 Series A
   ~~~
   $5M funding round completed.

   2022-03 1M Users
   ~~~
   Reached 1 million registered users.

   2022-09 International
   ~~~
   Expanded to 10 countries.

   2023 Enterprise
   ~~~
   Enterprise tier launched.

   2023-06 Strategic Partnership
   ~~~
   Partnership with major tech company.

   2024 Innovation
   ~~~
   AI features introduced.

   2024-09 IPO Announcement
   ~~~
   IPO announced for next year.


Quarter-Based Events
---------------------

Events can be specified with month-level precision:

.. timeline::
   :layout: horizontal
   :start-year: 2024
   :end-year: 2025
   :height: 350px

   2024-01 Q1 Planning
   ~~~
   Defined roadmap for 2024.

   2024-04 Q2 Launch
   ~~~
   Released new dashboard.

   2024-07 Q3 Growth
   ~~~
   User base grew 40%.

   2024-10 Q4 Optimization
   ~~~
   Performance improvements.

   2025-01 Q1 Expansion
   ~~~
   Planned new market entry.


Technology Evolution
--------------------

Show how your technology stack evolved:

.. timeline::
   :layout: horizontal
   :start-year: 2015
   :end-year: 2024
   :height: 500px

   2015 Legacy System
   ~~~
   Built on monolithic architecture.

   2017 Microservices
   ~~~
   Refactored to microservices.

   2018 Kubernetes
   ~~~
   Containerized all services.

   2019 Cloud Migration
   ~~~
   Moved to cloud infrastructure.

   2020-06 DevOps Pipeline
   ~~~
   Implemented CI/CD.

   2021 Infrastructure as Code
   ~~~
   All infrastructure versioned.

   2022-03 Observability
   ~~~
   Advanced monitoring deployed.

   2023 Edge Computing
   ~~~
   Edge deployment capabilities added.

   2024 AI/ML Integration
   ~~~
   ML pipelines in production.


Customization
-------------

Horizontal timelines support several customization options:

**Height and Width**

.. timeline::
   :layout: horizontal
   :height: 300px
   :width: 80%

   2020 Start
   ~~~
   Beginning.

   2024 Current
   ~~~
   Present day.

**Year Range**

The `:start-year:` and `:end-year:` options define the visible range:

.. timeline::
   :layout: horizontal
   :start-year: 2022
   :end-year: 2024

   2022-01 Event 1
   ~~~
   Details.

   2024-12 Event 2
   ~~~
   More details.

**Responsive Design**

The horizontal timeline automatically adjusts to different screen sizes:

- On desktop: Full SVG visualization with year markers
- On tablet: Maintains readability with adjusted sizing
- On mobile: Stacked layout for better usability

The timeline below automatically scales to fit your screen:

.. timeline::
   :layout: horizontal
   :start-year: 2020
   :end-year: 2024

   2020 Launch
   ~~~
   Product launch.

   2022 Growth
   ~~~
   Rapid growth phase.

   2024 Maturity
   ~~~
   Established market leader.
