"""
Timeline directive for Sphinx
Supports events with year/month resolution
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.states import Body
import datetime
from typing import List, Dict, Any


class TimelineEventNode(nodes.General, nodes.Element):
    """Node representing a timeline event."""
    pass


def visit_timeline_node(self, node):
    """Visit a timeline node for HTML output."""
    self.body.append(node.html)


def depart_timeline_node(self, node):
    """Depart a timeline node for HTML output."""
    pass


class TimelineDirective(Directive):
    """
    Sphinx directive for creating timelines.

    Usage:
        .. timeline::
           :start-year: 2020
           :end-year: 2024
           :layout: vertical

           2020-01 Project Start
           ~~~
           This is the beginning of the project.

           2021-06 Major Release
           ~~~
           Version 1.0 released to production.

           2024-11 Current Status
           ~~~
           Active development continues.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'start-year': directives.positive_int,
        'end-year': directives.positive_int,
        'layout': directives.unchanged,  # 'vertical' or 'horizontal'
        'height': directives.unchanged,  # e.g. '400px'
        'width': directives.unchanged,   # e.g. '100%'
    }

    def run(self):
        """Process the timeline directive."""
        # Parse options
        start_year = int(self.options.get('start-year', 2020))
        end_year = int(self.options.get('end-year', datetime.datetime.now().year))
        layout = self.options.get('layout', 'vertical')
        height = self.options.get('height', '600px')
        width = self.options.get('width', '100%')

        # Parse events from content
        events = self._parse_events()

        # Generate HTML
        html = self._generate_html(events, layout, start_year, end_year, height, width)

        # Create and return the node
        node = TimelineEventNode()
        node.html = html
        return [node]

    def _parse_events(self) -> List[Dict[str, str]]:
        """Parse timeline events from directive content."""
        events = []
        i = 0

        while i < len(self.content):
            line = self.content[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check if this is an event header (format: YYYY-MM Title or YYYY Title)
            if self._is_event_header(line):
                parts = line.split(maxsplit=1)
                date_str = parts[0]
                title = parts[1] if len(parts) > 1 else "Event"

                # Collect description (until next event or end)
                description_lines = []
                i += 1

                # Skip separator line (~~~) if present
                if i < len(self.content) and self.content[i].strip().startswith('~'):
                    i += 1

                # Collect description
                while i < len(self.content):
                    next_line = self.content[i].strip()
                    if not next_line or self._is_event_header(next_line):
                        break
                    description_lines.append(self.content[i])
                    i += 1

                description = '\n'.join(description_lines).strip()

                # Parse date
                date_parts = date_str.split('-')
                year = date_parts[0]
                month = date_parts[1] if len(date_parts) > 1 else '01'

                events.append({
                    'date': f'{year}-{month}',
                    'year': year,
                    'month': month,
                    'title': title,
                    'description': description,
                })
            else:
                i += 1

        return events

    def _is_event_header(self, line: str) -> bool:
        """Check if a line is an event header (YYYY-MM or YYYY)."""
        if not line:
            return False

        parts = line.split(maxsplit=1)
        date_part = parts[0]

        # Check format YYYY or YYYY-MM
        date_components = date_part.split('-')
        if len(date_components) not in [1, 2]:
            return False

        try:
            year = int(date_components[0])
            if len(date_components) == 2:
                month = int(date_components[1])
                if not (1 <= month <= 12):
                    return False
            return True
        except ValueError:
            return False

    def _generate_html(self, events: List[Dict[str, str]], layout: str,
                      start_year: int, end_year: int,
                      height: str, width: str) -> str:
        """Generate HTML for the timeline."""

        if layout == 'horizontal':
            return self._generate_horizontal_timeline(events, start_year, end_year, height, width)
        else:
            return self._generate_vertical_timeline(events, height, width)

    def _generate_vertical_timeline(self, events: List[Dict[str, str]],
                                   height: str, width: str) -> str:
        """Generate a vertical timeline HTML."""

        html_parts = [
            '<div class="sphinx-timeline sphinx-timeline-vertical" style="height: {}; width: {};">'.format(height, width),
            '<div class="timeline-container">',
        ]

        for event in events:
            html_parts.append(
                f'<div class="timeline-event">'
                f'<div class="timeline-date">{event["date"]}</div>'
                f'<div class="timeline-marker"></div>'
                f'<div class="timeline-content">'
                f'<h4 class="timeline-title">{event["title"]}</h4>'
                f'<p class="timeline-description">{event["description"]}</p>'
                f'</div>'
                f'</div>'
            )

        html_parts.extend([
            '</div>',
            '</div>',
        ])

        return '\n'.join(html_parts)

    def _generate_horizontal_timeline(self, events: List[Dict[str, str]],
                                     start_year: int, end_year: int,
                                     height: str, width: str) -> str:
        """Generate a horizontal timeline HTML."""

        # Sort events by date
        sorted_events = sorted(events, key=lambda e: (e['year'], e['month']))

        html_parts = [
            '<div class="sphinx-timeline sphinx-timeline-horizontal" style="height: {}; width: {};">'.format(height, width),
            '<svg class="timeline-svg" viewBox="0 0 1000 150" preserveAspectRatio="xMidYMid meet">',
            '<!-- Timeline axis -->',
            '<line x1="50" y1="75" x2="950" y2="75" stroke="#ccc" stroke-width="2"/>',
        ]

        # Calculate positions for years
        num_years = end_year - start_year + 1
        year_width = 900 / max(num_years - 1, 1)

        # Add year markers
        for i, year in enumerate(range(start_year, end_year + 1)):
            x = 50 + (i * year_width)
            html_parts.append(
                f'<line x1="{x}" y1="70" x2="{x}" y2="80" stroke="#999" stroke-width="1"/>'
            )
            html_parts.append(
                f'<text x="{x}" y="95" text-anchor="middle" font-size="12">{year}</text>'
            )

        # Add events
        for event in sorted_events:
            year = int(event['year'])
            month = int(event['month'])

            year_index = year - start_year
            month_offset = (month - 1) / 12.0  # Position within the year

            x = 50 + year_index * year_width + (month_offset * year_width)

            html_parts.append(
                f'<circle cx="{x}" cy="75" r="5" fill="#0066cc" '
                f'class="timeline-event-marker" title="{event["date"]}: {event["title"]}"/>'
            )
            html_parts.append(
                f'<text x="{x}" y="30" text-anchor="middle" font-size="11" '
                f'class="timeline-event-label">{event["title"]}</text>'
            )

        html_parts.extend([
            '</svg>',
            '<div class="timeline-events-legend">',
        ])

        for event in sorted_events:
            html_parts.append(
                f'<div class="timeline-legend-item">'
                f'<span class="timeline-legend-date">{event["date"]}</span>'
                f'<strong>{event["title"]}</strong>'
                f'<p>{event["description"]}</p>'
                f'</div>'
            )

        html_parts.extend([
            '</div>',
            '</div>',
        ])

        return '\n'.join(html_parts)
