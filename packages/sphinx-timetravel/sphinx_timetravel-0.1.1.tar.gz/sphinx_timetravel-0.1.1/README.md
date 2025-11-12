# Sphinx TimeTravel Plugin

A Sphinx extension for displaying interactive timelines with year/month resolution in your documentation.

## Features

- **Vertical Timeline**: Classic chronological layout showing events down the page
- **Horizontal Timeline**: Year-based timeline with SVG rendering
- **Layout Toggle**: Interactive switch to toggle between vertical and horizontal views
- **Year/Month Resolution**: Support for precise date specifications (YYYY-MM or YYYY)
- **Responsive Design**: Mobile-friendly layouts
- **Interactive Elements**: Hover effects and visual feedback

## Installation

```bash
pip install sphinx-timetravel
```

Or clone and install from source:

```bash
git clone https://github.com/robbinespu/sphinx-timetravel.git
cd sphinx-timetravel
pip install -e .
```

## Configuration

Add the plugin to your Sphinx `conf.py`:

```python
extensions = [
    'sphinx_timetravel',
]
```

## Usage

### Basic Vertical Timeline

```rst
.. timeline::

   2020-01 Project Started
   ~~~
   This is when we began the project.

   2021-06 Version 1.0 Released
   ~~~
   Major release with core features.

   2023-03 Milestone Achieved
   ~~~
   We reached 1 million users!
```

### Horizontal Timeline with Date Range

```rst
.. timeline::
   :start-year: 2020
   :end-year: 2024
   :layout: horizontal
   :height: 400px

   2020 Project Start
   ~~~
   The beginning of everything.

   2021-06 Major Release
   ~~~
   Version 1.0 shipped to production.

   2023-12 Record Year
   ~~~
   Best year in company history.

   2024-11 Current Status
   ~~~
   Ongoing development and improvement.
```

### Timeline with Toggle Switch

Add an interactive toggle to switch between layouts:

```rst
.. timeline::
   :toggle:
   :start-year: 2020
   :end-year: 2024

   2020-01 Project Started
   ~~~
   The beginning.

   2024-11 Current Status
   ~~~
   Still going!
```

### Options

- `start-year`: Starting year for horizontal timeline (optional)
- `end-year`: Ending year for horizontal timeline (optional)
- `layout`: Timeline layout - `vertical` (default) or `horizontal`
- `height`: Timeline container height (e.g., `600px`, default: `600px`)
- `width`: Timeline container width (e.g., `100%`, default: `100%`)
- `toggle`: Show layout toggle switch (boolean flag, no value needed)

## Event Format

Each event consists of:

1. **Date line**: `YYYY-MM` or `YYYY` format, followed by event title
2. **Separator**: Optional `~~~` line
3. **Description**: Multi-line description text

```rst
2024-05 Event Title
~~~
This is a detailed description
that can span multiple lines.
```

## Styling

The plugin includes default styling in `timeline.css`. You can customize colors and appearance by:

1. **Overriding CSS variables** in your custom stylesheet
2. **Adding custom CSS** in your `_static/` directory
3. **Modifying the source** CSS file

### CSS Classes

- `.sphinx-timeline`: Main container
- `.sphinx-timeline-vertical`: Vertical timeline variant
- `.sphinx-timeline-horizontal`: Horizontal timeline variant
- `.timeline-event`: Individual event
- `.timeline-date`: Date label
- `.timeline-marker`: Visual marker point
- `.timeline-content`: Event description container

## Examples

See the `docs/` directory for complete working examples.

## Development

### Setup Development Environment

```bash
git clone https://github.com/robbinespu/sphinx-timetravel.git
cd sphinx-timetravel
pip install -e ".[dev]"
```

### Building Documentation

```bash
cd docs
make html
```

### Running Tests

```bash
pytest
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### Timeline not displaying

- Ensure the extension is added to `extensions` in `conf.py`
- Check that `timeline.css` is being served (check browser dev tools)
- Verify event format is correct (YYYY-MM or YYYY)

### Styling issues

- Clear Sphinx build cache: `make clean` then `make html`
- Check CSS file path and ensure it's in the `_static/` directory
- Verify no conflicting CSS in your theme

### Performance issues with many events

- For horizontal timelines with many events, consider splitting into multiple timelines
- Use vertical layout for large datasets (more scalable)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example files

## Changelog

### 0.1.1
- Add toggle options to switch horizontal and vertical timeline
- Update metadata and documentation

### 0.1.0 (Initial Release)
- Vertical timeline layout
- Horizontal timeline layout
- Year/month resolution
- Responsive design
- Basic styling
