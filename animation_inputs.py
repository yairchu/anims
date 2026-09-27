"""One moops declaration for each input shared by preview and export."""

from scene_defaults import (
    DEFAULT_EXPORT_SCENE,
    ENDPOINT_TEXT_SIZE,
    ZONE_TEXT_SIZE,
    METER_SPACING,
    ISRAELI_COLOR,
    NEEDLE_COLOR,
    PALESTINIAN_COLOR,
    RECONCILIATION_END,
    RIGHT_ZONE_START,
)


def boundary_controls(args):
    reconciliation = args.slider(
        0.1,
        0.45,
        0.01,
        RECONCILIATION_END,
        option="--reconciliation-end",
        help_text="Reconciliation zone ends at",
        label="Reconciliation zone ends at",
        show_value=True,
        full_width=True,
    )
    right = args.slider(
        0.55,
        0.95,
        0.01,
        RIGHT_ZONE_START,
        option="--right-zone-start",
        help_text="Right-hand zones start at",
        label="Right-hand zones start at",
        show_value=True,
        full_width=True,
    )
    return reconciliation, right


def color_controls(args):
    # The custom component is constructed only in a live notebook. CLI values
    # remain strings, and the pickers initialize from the same resolved inputs.
    import marimo as mo
    import wigglystuff

    def picker(option, default, label):
        return args.custom(
            args.text(value=default, option=option, help_text=label),
            lambda color: mo.ui.anywidget(wigglystuff.ColorPicker(color=color)),
            # anywidget keeps live traits on the widget, not UIElement._value.
            value=lambda component, fallback: component.widget.color,
        )

    return (
        picker("--israeli-color", ISRAELI_COLOR, "Israeli meter color"),
        picker("--palestinian-color", PALESTINIAN_COLOR, "Palestinian meter color"),
        picker("--needle-color", NEEDLE_COLOR, "Needle color"),
    )


def scene_control(args, *, default=None, labels=None):
    from animation_timeline import SCENE_LABELS

    return labeled_choice(args, SCENE_LABELS if labels is None else labels, "--scene", "Scene", default)


def format_control(args, *, default=None):
    from video_formats import FORMAT_LABELS

    return labeled_choice(args, FORMAT_LABELS, "--format", "Video format", default)


def labeled_choice(args, labels, option, label, default):
    """Keep readable UI labels and short, stable CLI choices."""
    import marimo as mo

    return args.custom(
        args.dropdown(
            list(labels.values()),
            value=default,
            option=option,
            label=label,
            help_text=label,
            allow_select_none=default is None,
        ),
        lambda value: mo.ui.dropdown(
            labels,
            value=next((key for key, item in labels.items() if item == value), None),
            label=label,
            allow_select_none=default is None,
        ),
    )


def layout_controls(args):
    """Absolute font sizes and arc-to-arc gap in shared scene coordinates."""
    return tuple(
        args.slider(low, high, step, default, option=option, label=label,
                    help_text=label, show_value=True, full_width=True)
        for low, high, step, default, option, label in (
            (20, 70, 0.1, ENDPOINT_TEXT_SIZE, "--endpoint-text-size", "Endpoint font size (scene units)"),
            (12, 29, 0.1, ZONE_TEXT_SIZE, "--zone-text-size", "Zone font size (scene units)"),
            (0, 300, 5, METER_SPACING, "--meter-spacing", "Meter gap (scene units)"),
        )
    )


def build_export_command(scene, video_format, timeline, **settings):
    """Emit only options that differ from the exporter's effective defaults."""
    import shlex

    from video_formats import FORMATS

    defaults = dict(
        reconciliation_end=RECONCILIATION_END,
        right_zone_start=RIGHT_ZONE_START,
        endpoint_text_size=ENDPOINT_TEXT_SIZE,
        zone_text_size=ZONE_TEXT_SIZE,
        meter_spacing=METER_SPACING,
        israeli_color=ISRAELI_COLOR,
        palestinian_color=PALESTINIAN_COLOR,
        needle_color=NEEDLE_COLOR,
    )
    command = ["uv", "run", "python", "export_video.py"]
    if scene != DEFAULT_EXPORT_SCENE:
        command.extend(["--scene", scene])
    if FORMATS[video_format] != (timeline["width"], timeline["height"]):
        command.extend(["--format", video_format])
    for name, value in settings.items():
        if value != defaults[name]:
            command.extend(["--" + name.replace("_", "-"), str(value)])
    return shlex.join(command)
