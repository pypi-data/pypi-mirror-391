"""
Vertical chronological timeline directive for Sphinx.
Supports events with year/month resolution.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from typing import List, Dict


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
    Sphinx directive for creating vertical chronological timelines.

    Usage:
        .. timeline::
           :height: 600px
           :width: 100%

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
        'height': directives.unchanged,  # e.g. '600px'
        'width': directives.unchanged,   # e.g. '100%'
    }

    def run(self):
        """Process the timeline directive."""
        # Parse options
        height = self.options.get('height', '600px')
        width = self.options.get('width', '100%')

        # Parse events from content
        events = self._parse_events()

        # Generate HTML for vertical timeline
        html = self._generate_vertical_timeline(events, height, width)

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

    def _generate_vertical_timeline(self, events: List[Dict[str, str]],
                                   height: str, width: str) -> str:
        """Generate a vertical timeline HTML."""
        
        # Icons/emojis for different event types
        icons = ['📅', '🚀', '💾', '🎯', '📊', '🔧', '✨', '🌟', '💡', '🎉']
        
        html_parts = [
            '<div class="sphinx-timeline">',
        ]

        for i, event in enumerate(events):
            icon = icons[i % len(icons)]
            event_type = (i % 3) + 1  # Cycle through 3 color schemes
            side = 'left' if i % 2 == 0 else 'right'  # Alternate between left and right
            
            # For left events: content → date → icon (icon is absolutely positioned)
            # For right events: icon → date → content (icon is absolutely positioned)
            if side == 'left':
                html_parts.append(
                    f'<div class="timeline__event animated fadeInUp timeline__event--type{event_type} timeline__event--{side}">'
                    f'<div class="timeline__event__icon">'
                    f'{icon}'
                    f'</div>'
                    f'<div class="timeline__event__content">'
                    f'<div class="timeline__event__title">'
                    f'{event["title"]}'
                    f'</div>'
                    f'<div class="timeline__event__description">'
                    f'<p>{event["description"]}</p>'
                    f'</div>'
                    f'</div>'
                    f'<div class="timeline__event__date-block">'
                    f'<div class="timeline__event__date">'
                    f'{event["date"]}'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
            else:  # right
                html_parts.append(
                    f'<div class="timeline__event animated fadeInUp timeline__event--type{event_type} timeline__event--{side}">'
                    f'<div class="timeline__event__icon">'
                    f'{icon}'
                    f'</div>'
                    f'<div class="timeline__event__date-block">'
                    f'<div class="timeline__event__date">'
                    f'{event["date"]}'
                    f'</div>'
                    f'</div>'
                    f'<div class="timeline__event__content">'
                    f'<div class="timeline__event__title">'
                    f'{event["title"]}'
                    f'</div>'
                    f'<div class="timeline__event__description">'
                    f'<p>{event["description"]}</p>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )

        html_parts.append('</div>')

        return '\n'.join(html_parts)
