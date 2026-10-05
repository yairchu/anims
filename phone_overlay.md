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

Click **Save text for export** to persist the fields to `timeline_phone.json`,
then rerun the export command with `--overwrite` to update the MOV. Saving text
does not regenerate existing videos. The account initial and audio attribution
follow the account name automatically. You can also edit the five entries under
`labels` in the JSON file directly; the notebook watches that file for changes.

| Seconds | Action |
| --- | --- |
| 0–2 | Reel interface; your video plays underneath. |
| 2–2.48 | Banner drops in. |
| 2.48–6.3 | Readable hold. |
| 6.08–6.64 | Brief illustrative touch indicator. |
| 6.3–6.68 | Banner swipes upward. |
| 6.68–10 | Unobstructed reel resumes. |

There is no automatic scrolling or dog footage in the overlay. The underlying video can keep playing throughout, including during the notification.

## Compositing

Use a 1080 × 1920 project and place the MOV above your dog video at its native size. Crop or mask the dog layer to the screen aperture; otherwise it will also show through the transparent space outside the phone. The overlay includes gradients and interface controls over the opening, so do not key out black or use a blend mode on the MOV.

The aperture, measured from the canvas's top-left corner, is **x=225, y=216, width=630, height=1050 pixels**. Its center is **(540, 741)**. The supplied matte represents exactly this rectangle. The visible aperture has square corners because the phone's curved ends are covered by opaque status/navigation bars. Slight overlap behind those bars can hide subpixel edges.

The phone ends around y=1413, leaving approximately the bottom 500 pixels clear for captions. Keep the dog clip masked when adding a background behind the entire composition.

The PNG still and SVG are also transparent. Checkerboard in the notebook is only a preview aid, never burned into exported artwork. Final Cut should read the MOV's alpha automatically; if compositing edges look wrong, inspect alpha interpretation before adding keys or effects.

## Commands

```sh
uv run marimo edit phone_notification.py
uv run python animation_preview.py --scene phone
uv run python export_video.py --scene phone --transparent --output output/phone-overlay.mov
uv run python export_video.py --scene phone --output output/phone-preview.mp4
```

Add `--overwrite` when replacing an existing export. Edit `labels` and keyframes in `timeline_phone.json` before rerendering. Setting the touch track to `[[0, 0]]` removes the illustrative touch circle.
