"""Vector phone overlay. No video is baked into the transparent screen aperture."""

from html import escape

# Canonical 720 × 1280 composition; multiply by 1.5 for the default export.
VIDEO_RECT = (150, 144, 420, 700)


def text(x, y, value, size=18, fill="white", **attrs):
    attributes = " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"'
                          for key, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {attributes}>{escape(str(value))}</text>'


def icon(kind, x, y, size=28, color="white", filled=False):
    paths = {
        "heart": '<path d="M12 21S2 15 2 8a5 5 0 0 1 10-2 5 5 0 0 1 10 2c0 7-10 13-10 13Z"/>',
        "comment": '<path d="M21 11a9 9 0 1 0-5 8l5 2-1-6a9 9 0 0 0 1-4Z"/>',
        "send": '<path d="m2 3 20-1-7 20-4-10Z M11 12 22 2"/>',
        "home": '<path d="m2 11 10-9 10 9v11h-7v-8H9v8H2Z"/>',
        "search": '<circle cx="10" cy="10" r="7"/><path d="m15 15 7 7"/>',
        "plus": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M12 7v10M7 12h10"/>',
        "reels": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M2 8h20M7 2l4 6M15 2l4 6"/><path d="m10 11 6 4-6 4Z"/>',
        "camera": '<path d="M2 8h5l2-4h6l2 4h5v13H2Z"/><circle cx="12" cy="14" r="4"/>',
        "shield": '<path d="m12 2 9 4v7c0 5-9 9-9 9S3 18 3 13V6Z"/><path d="m8 12 3 3 5-6"/>',
        "music": '<path d="M9 18V5l11-3v13M9 9l11-3"/><ellipse cx="6" cy="18" rx="3" ry="2"/><ellipse cx="17" cy="15" rx="3" ry="2"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/24})" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="{color if filled else "none"}">{paths[kind]}</g>'


def video_matte(width=1080, height=1920):
    """White aperture on black for an optional luma matte in the editor."""
    x, y, w, h = VIDEO_RECT
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280"><rect width="720" height="1280" fill="black"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/></svg>'


def render_phone(state, *, width=1080, height=1920, transparent=True):
    labels = state.get("labels", {})
    entered = state.get("notification_in", 0)
    dismiss = state.get("dismiss", 0)
    touch = state.get("touch", 0)
    banner_y = -160 + 260 * entered - 280 * dismiss
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280">
    <defs>
      <clipPath id="screen"><rect x="150" y="50" width="420" height="880" rx="48"/></clipPath>
      <mask id="bezel"><rect x="138" y="38" width="444" height="904" rx="60" fill="white"/><rect x="150" y="50" width="420" height="880" rx="48" fill="black"/></mask>
      <linearGradient id="metal" x2="1" y2="1"><stop stop-color="#84888f"/><stop offset=".3" stop-color="#25272c"/><stop offset=".7" stop-color="#111217"/><stop offset="1" stop-color="#777c84"/></linearGradient>
      <linearGradient id="bottomShade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".76"/></linearGradient>
      <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#f6f6f8" stop-opacity=".98"/><stop offset="1" stop-color="#dedee4" stop-opacity=".96"/></linearGradient>
      <filter id="shadow" x="-25%" y="-40%" width="150%" height="190%"><feGaussianBlur stdDeviation="5"/></filter>
      <filter id="ink" x="-25%" y="-25%" width="150%" height="150%"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity=".65"/></filter>
    </defs>''']
    if not transparent:
        parts.append('<rect width="720" height="1280" fill="#e9edf2"/>')
        parts.append('<rect x="150" y="144" width="420" height="700" fill="#71887d"/>')
        parts.append(text(360, 442, "YOUR VIDEO HERE", 20, text_anchor="middle", font_weight="700"))
        parts.append(text(360, 469, "Transparent in the MOV export", 13, text_anchor="middle"))
    parts.append('''<g font-family="Arial, sans-serif">
      <rect x="134" y="189" width="5" height="40" rx="2" fill="#44464d"/>
      <rect x="134" y="246" width="5" height="65" rx="2" fill="#44464d"/>
      <rect x="581" y="229" width="5" height="90" rx="2" fill="#44464d"/>
      <rect x="138" y="38" width="444" height="904" rx="60" fill="url(#metal)" mask="url(#bezel)"/>
      <rect x="140" y="40" width="440" height="900" rx="58" fill="none" stroke="#a4a7ad" stroke-opacity=".5"/>
      <g clip-path="url(#screen)">
      <path d="M150 50h420v94H150Z M150 844h420v86H150Z" fill="#09090c"/>
      <rect x="150" y="680" width="420" height="164" fill="url(#bottomShade)"/>
      <rect x="297" y="60" width="126" height="31" rx="16" fill="#000"/>
      <circle cx="407" cy="76" r="5" fill="#11141e"/>
      <circle cx="408" cy="75" r="2" fill="#1b2c49"/>
    ''')
    parts.append(text(180, 82, "9:41", 17, font_weight="700"))
    for i in range(4):
        parts.append(f'<rect x="{474+i*5}" y="{80-i*3}" width="3" height="{4+i*3}" rx="1" fill="white"/>')
    parts.append('''<path d="M499 73q8-7 16 0m-13 4q5-4 10 0m-7 4 2 2 2-2" stroke="white" stroke-width="2" fill="none"/>
      <rect x="523" y="69" width="24" height="13" rx="4" fill="none" stroke="white" stroke-opacity=".6"/>
      <rect x="525" y="71" width="18" height="9" rx="2" fill="white"/><path d="M549 73v5" stroke="white" stroke-width="2"/>''')
    parts.append(text(171, 129, "Reels", 25, font_weight="700"))
    parts.append('<path d="m243 117 5 5 5-5" stroke="white" stroke-width="2" fill="none"/>')
    parts.append(icon("camera", 520, 105, 27))
    parts.append('<g filter="url(#ink)">')
    for kind, y, count in [("heart", 522, "24.8K"), ("comment", 596, "318"), ("send", 670, "1,204")]:
        parts.append(icon(kind, 522, y, 30))
        parts.append(text(537, y+48, count, 12, text_anchor="middle", font_weight="600"))
    parts.append('<circle cx="528" cy="750" r="2" fill="white"/><circle cx="536" cy="750" r="2" fill="white"/><circle cx="544" cy="750" r="2" fill="white"/>')
    parts.append('<circle cx="184" cy="768" r="15" fill="#dcc6a5" stroke="white" stroke-width="1.5"/>')
    parts.append(text(184, 774, "g", 20, "#4b382c", text_anchor="middle", font_weight="700"))
    parts.append(text(207, 775, labels.get("account", "good.dog.club"), 15, font_weight="700"))
    parts.append('<rect x="325" y="755" width="58" height="24" rx="6" fill="none" stroke="white" stroke-opacity=".8"/>')
    parts.append(text(354, 772, "Follow", 12, text_anchor="middle"))
    parts.append(text(170, 803, labels.get("caption", "Just another day at the skatepark."), 14))
    parts.append(icon("music", 170, 816, 13))
    parts.append(text(190, 827, "good.dog.club · Original audio", 11))
    parts.append('<rect x="522" y="788" width="29" height="29" rx="5" fill="#282b2f" stroke="white"/>')
    parts.append(icon("music", 529, 795, 15))
    parts.append('</g>')
    for kind, x in [("home", 180), ("search", 262), ("plus", 347), ("reels", 432)]:
        parts.append(icon(kind, x, 861, 25))
    parts.append('<circle cx="526" cy="875" r="13" fill="#94887c"/><circle cx="526" cy="871" r="4" fill="#ddd4c8"/><path d="M518 882q8-12 16 0" fill="#ddd4c8"/>')
    parts.append('<rect x="301" y="915" width="118" height="4" rx="2" fill="white"/>')
    if entered > 0 and dismiss < 1:
        parts.append(f'<g id="notification" transform="translate(0 {banner_y:.3f})">')
        parts.append('<rect x="162" y="5" width="396" height="116" rx="25" fill="#000" opacity=".28" filter="url(#shadow)"/>')
        parts.append('<rect x="162" width="396" height="116" rx="25" fill="url(#glass)" stroke="white" stroke-opacity=".55"/>')
        parts.append('<rect x="510" y="17" width="32" height="32" rx="8" fill="#3977dc"/>')
        parts.append(icon("shield", 517, 24, 18))
        parts.append(text(460, 35, labels.get("app", "בדיקת צוותים"), 13, "#54545b", direction="rtl", text_anchor="middle"))
        parts.append(text(180, 35, "now", 12, "#777780"))
        parts.append(text(360, 69, labels.get("title", "רשימת צוות לבדיקה"), 24, "#19191d", direction="rtl", text_anchor="middle", font_weight="700"))
        parts.append(text(360, 94, labels.get("body", "טיסה נכנסת • ממתינה לבדיקה"), 18, "#34343c", direction="rtl", text_anchor="middle"))
        parts.append('</g>')
    if touch > 0:
        parts.append(f'<circle id="touch" cx="371" cy="{205-260*dismiss:.3f}" r="17" fill="white" fill-opacity=".22" stroke="white" stroke-width="2" opacity="{touch:.3f}"/>')
    parts.append('</g></g></svg>')
    return "".join(parts)
