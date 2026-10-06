# Phone overlay for Final Cut

An editorial illustration with an invented crew-check app. Instagram-inspired controls and a classic iPhone-style banner; not a screenshot or a claim that an actual official received this alert. The upward gesture dismisses the banner without opening it; it does not depict deleting the underlying message.

Apple distinguishes notification banners from the Lock Screen and Notification Center: [iPhone notification settings](https://support.apple.com/guide/iphone/change-notification-settings-iph7c3d96bab/ios). This design uses a banner over an unlocked app. It is a stylized approximation, not a version-specific reproduction. The light notification card is translucent, but cannot blur footage added later in an editor.

## Files

- `phone_notification.py`: scrubber notebook with a checkerboard preview and SVG download.
- `phone_scene.py`: native SVG artwork, with a genuinely transparent video window.
- `timeline_phone.json`: timing and text, watched by the notebook.
- `output/phone-overlay.mov`: 1080 × 1920, 30 fps, 10 seconds, ProRes 4444 with alpha; silent.
- `output/phone-preview.mp4`: opaque reference preview; the placeholder is not in the MOV.
- `output/phone-overlay.png`: transparent still with the notification visible.
- `output/phone-video-matte.png`: white video aperture on black, for an optional luma mask.

## First-cut timing

To change text, open `uv run marimo edit phone_notification.py`. The notebook has
fields for **Account name**, **Post text**, **Notification app name**,
**Notification title**, and **Notification message**. Edits appear in the preview
after you submit the field (Enter or leaving the field). Scrub to 3 seconds to see
the notification. Keep text concise enough to fit the single-line fields.

The **Notification size** slider makes the banner taller and its text and icon
larger (1 = phone-accurate, up to 1.8). The banner keeps the screen's width, so
at large sizes keep the title short enough to fit on one line.

Click **Export MOV** at the bottom of the notebook to render the current text and
size to the **Output MOV** path, replacing any existing file there.
The notebook is also the exporter's command line: **Notebook CLI info** shows the
`uv run python phone_notification.py ...` command for the current values, and
running it renders the same MOV. The account initial and audio attribution follow
the account name automatically. The defaults come from `labels` and
`notification_scale` in `timeline_phone.json`; the notebook watches that file for
changes.

The text and size controls use **moops presets**. Enter a preset name and click
**Save** in the controls panel to store the five text fields and the size together.
Select a saved preset to restore them in the preview; the panel also supports renaming.
Presets are stored in `phone_notification_presets.json` next to the notebook.
Saving or selecting a preset does not change animation timing or the timeline
file. The output path and the time scrubber are not part of a preset.

| Seconds | Action |
| --- | --- |
| 0–2 | Reel interface; your video plays underneath. |
| 2–2.48 | Banner drops in. |
| 2.48–6.3 | Readable hold. |
| 6.08–6.64 | Brief illustrative touch indicator. |
| 6.3–6.68 | Banner swipes upward. |
| 6.68–7.2 | Unobstructed reel resumes. |
| 7.2–7.65 | Tap on the heart. |
| 7.3–7.6 | Heart pops and turns red; stays liked to the end. |

There is no automatic scrolling or dog footage in the overlay. The underlying video can keep playing throughout, including during the notification.

## Compositing

Use a 1080 × 1920 project and place the MOV above your dog video at its native size. Crop or mask the dog layer to the screen aperture; otherwise it will also show through the transparent space outside the phone. The overlay includes gradients and interface controls over the opening, so do not key out black or use a blend mode on the MOV.

The aperture, measured from the canvas's top-left corner, is **x=225, y=216, width=630, height=1050 pixels**. Its center is **(540, 741)**. The supplied matte represents exactly this rectangle. The visible aperture has square corners because the phone's curved ends are covered by opaque status/navigation bars. Slight overlap behind those bars can hide subpixel edges.

The phone ends around y=1413, leaving approximately the bottom 500 pixels clear for captions. Keep the dog clip masked when adding a background behind the entire composition.

The PNG still and SVG are also transparent. Checkerboard in the notebook is only a preview aid, never burned into exported artwork. Final Cut should read the MOV's alpha automatically; if compositing edges look wrong, inspect alpha interpretation before adding keys or effects.

## Commands

```sh
uv run marimo edit phone_notification.py
uv run python phone_notification.py --notification-size 1.6 --output output/phone-overlay.mov
uv run python animation_preview.py --scene phone
uv run python export_video.py --scene phone --output output/phone-preview.mp4
```

`export_video.py` needs `--overwrite` to replace an existing export, and uses only the timeline file's text and size. Edit keyframes in `timeline_phone.json` before rerendering. Setting the touch track to `[[0, 0]]` removes the illustrative touch circle; do the same to `like_touch` and `like` to drop the heart tap.
