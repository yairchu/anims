"""One moops declaration for each input shared by preview and export."""

from scene_defaults import (
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


def scene_control(args, *, default=None):
    from animation_timeline import SCENE_LABELS

    return labeled_choice(args, SCENE_LABELS, "--scene", "Scene", default)


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
