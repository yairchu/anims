"""Keep presets complete even when values match the current timeline."""
import shlex
import moops

OPTIONS = {
    "account": "--account", "caption": "--caption",
    "app": "--notification-app", "title": "--notification-title",
    "body": "--notification-body", "notification_scale": "--notification-size",
}


class PhonePresets(moops.Presets):
    def __init__(self, get_selected, set_selected, *, filename, defaults):
        super().__init__(get_selected, set_selected, filename=filename)
        self.defaults = dict(defaults)

    def save(self, name, args):
        # moops omits default-valued arguments. Freeze those too, since
        # timeline defaults change when another preset is applied for export.
        tokens = iter(shlex.split(args))
        values = dict(zip(tokens, tokens))
        complete = [token for key, option in OPTIONS.items()
                    for token in (option, str(values.get(option, self.defaults[key])))]
        super().save(name, shlex.join(complete))
