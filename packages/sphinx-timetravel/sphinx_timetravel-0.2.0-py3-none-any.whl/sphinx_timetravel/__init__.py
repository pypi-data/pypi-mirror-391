"""
Sphinx Time Travel Plugin - Display timelines in Sphinx documentation
"""

from sphinx_timetravel.timeline import TimelineDirective, TimelineEventNode
from sphinx_timetravel.timeline import visit_timeline_node, depart_timeline_node

__version__ = '0.1.0'


def setup(app):
    """Setup the Sphinx extension."""

    # Register the directive
    app.add_directive('timeline', TimelineDirective)

    # Register nodes and visitors for HTML output
    app.add_node(
        TimelineEventNode,
        html=(visit_timeline_node, depart_timeline_node),
    )

    # Add CSS for styling
    app.add_css_file('timeline.css')

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
