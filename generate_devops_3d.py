#!/usr/bin/env python3
"""
Generate a 3D Isometric DevOps Network SVG for GitHub Profile.
Pure Python standard library implementation.
"""

import os
import json
import math
import datetime
import urllib.request
import urllib.error

# --- CONFIGURATION ---
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "quoczai22")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

WIDTH = 850
HEIGHT = 480
ORIGIN_X = 425
ORIGIN_Y = 250

COS30 = math.cos(math.radians(30))  # ≈ 0.866025
SIN30 = math.sin(math.radians(30))  # 0.5

LANG_COLORS = {
    "Java": "#b07219",
    "Python": "#3572A5",
    "C++": "#f34b7d",
    "C": "#555555",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Docker": "#38bdf8",
    "Kubernetes": "#326ce5",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4F5D95",
    "C#": "#178600",
}


def to_iso(x, y, z=0):
    """Convert 3D coordinate (x, y, z) to 2D Isometric screen coordinate."""
    iso_x = ORIGIN_X + (x - y) * COS30
    iso_y = ORIGIN_Y + (x + y) * SIN30 - z
    return round(iso_x, 2), round(iso_y, 2)


def fetch_github_data(username, token):
    """Fetch user commits and top languages from GitHub GraphQL API."""
    now = datetime.datetime.now(datetime.timezone.utc)
    from_7d = (now - datetime.timedelta(days=7)).isoformat()
    from_30d = (now - datetime.timedelta(days=30)).isoformat()
    now_iso = now.isoformat()

    query = """
    query($login: String!, $from7: DateTime!, $from30: DateTime!, $to: DateTime!) {
      user(login: $login) {
        c7: contributionsCollection(from: $from7, to: $to) {
          totalCommitContributions
        }
        c30: contributionsCollection(from: $from30, to: $to) {
          totalCommitContributions
        }
        repositories(first: 30, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            name
            languages(first: 6, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "login": username,
        "from7": from_7d,
        "from30": from_30d,
        "to": now_iso
    }

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": "DevOps-Isometric-3D-Generator"
        }
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        result = json.loads(response.read().decode("utf-8"))
        if "errors" in result:
            raise RuntimeError(f"GraphQL Errors: {result['errors']}")
        return result["data"]["user"]


def get_profile_data():
    """Fetch live data or return robust fallback values."""
    if GITHUB_TOKEN:
        try:
            print(f"[*] Fetching GraphQL API for user: {GITHUB_USERNAME}...")
            raw = fetch_github_data(GITHUB_USERNAME, GITHUB_TOKEN)
            commits_7d = raw.get("c7", {}).get("totalCommitContributions", 0)
            commits_30d = raw.get("c30", {}).get("totalCommitContributions", 0)

            lang_totals = {}
            for repo in raw.get("repositories", {}).get("nodes", []):
                for edge in repo.get("languages", {}).get("edges", []):
                    name = edge["node"]["name"]
                    size = edge["size"]
                    color = edge["node"].get("color")
                    if color:
                        LANG_COLORS[name] = color
                    lang_totals[name] = lang_totals.get(name, 0) + size

            sorted_langs = sorted(lang_totals.items(), key=lambda item: item[1], reverse=True)[:5]
            if not sorted_langs:
                raise ValueError("No languages found in public repositories.")

            total_bytes = sum(s for _, s in sorted_langs)
            languages = [
                {"name": name, "percentage": round((size / total_bytes) * 100, 1)}
                for name, size in sorted_langs
            ]

            print(f"[✓] Fetched successfully: 7d commits={commits_7d}, 30d commits={commits_30d}, languages={len(languages)}")
            return {
                "commits_7d": commits_7d,
                "commits_30d": commits_30d,
                "languages": languages,
                "is_fallback": False
            }
        except Exception as e:
            print(f"[!] API fetch failed ({e}). Switching to Fallback dataset...")

    # Fallback dataset
    return {
        "commits_7d": 18,
        "commits_30d": 74,
        "languages": [
            {"name": "Java", "percentage": 38.5},
            {"name": "Python", "percentage": 27.2},
            {"name": "C++", "percentage": 18.0},
            {"name": "Docker", "percentage": 10.3},
            {"name": "Kubernetes", "percentage": 6.0}
        ],
        "is_fallback": True
    }


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def shade_color(hex_str, factor):
    """Adjust color brightness by a factor."""
    r, g, b = hex_to_rgb(hex_str)
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_isometric_box(cx, cy, cz, dx, dy, dz, base_color, stroke_color=None, stroke_width=1):
    """
    Draw a 3D isometric cuboid with 3 faces (Top, Left, Right).
    Shading: Top (brightest), Left (medium), Right (dark).
    """
    x1, x2 = cx - dx / 2, cx + dx / 2
    y1, y2 = cy - dy / 2, cy + dy / 2
    z1, z2 = cz, cz + dz

    p100 = to_iso(x2, y1, z1)
    p110 = to_iso(x2, y2, z1)
    p010 = to_iso(x1, y2, z1)

    p001 = to_iso(x1, y1, z2)
    p101 = to_iso(x2, y1, z2)
    p111 = to_iso(x2, y2, z2)
    p011 = to_iso(x1, y2, z2)

    top_color = shade_color(base_color, 1.25)
    left_color = shade_color(base_color, 0.95)
    right_color = shade_color(base_color, 0.70)
    stroke = stroke_color or shade_color(base_color, 1.45)

    svg_parts = []
    # Left Face (x = x2)
    svg_parts.append(
        f'<polygon points="{p100[0]},{p100[1]} {p110[0]},{p110[1]} {p111[0]},{p111[1]} {p101[0]},{p101[1]}" '
        f'fill="{left_color}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round" />'
    )
    # Right Face (y = y2)
    svg_parts.append(
        f'<polygon points="{p010[0]},{p010[1]} {p110[0]},{p110[1]} {p111[0]},{p111[1]} {p011[0]},{p011[1]}" '
        f'fill="{right_color}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round" />'
    )
    # Top Face (z = z2)
    svg_parts.append(
        f'<polygon points="{p001[0]},{p001[1]} {p101[0]},{p101[1]} {p111[0]},{p111[1]} {p011[0]},{p011[1]}" '
        f'fill="{top_color}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round" />'
    )
    return "".join(svg_parts)


def build_svg(data):
    commits_7d = data["commits_7d"]
    commits_30d = data["commits_30d"]
    languages = data["languages"]

    # Packet travel speed inversely proportional to 7-day commits
    if commits_7d >= 40:
        anim_duration = 1.6
    elif commits_7d >= 20:
        anim_duration = 2.4
    elif commits_7d >= 5:
        anim_duration = 3.6
    else:
        anim_duration = 5.2

    # Worker Node positions on isometric plane
    worker_offsets = [
        (-145, -75),
        (145, -75),
        (-155, 85),
        (155, 85),
        (0, 160)
    ]

    elements_to_render = []

    # 1. Grid lines on isometric floor
    grid_lines = []
    for gx in range(-200, 201, 50):
        p_start = to_iso(gx, -180, 0)
        p_end = to_iso(gx, 180, 0)
        grid_lines.append(f'<line x1="{p_start[0]}" y1="{p_start[1]}" x2="{p_end[0]}" y2="{p_end[1]}" stroke="#1e293b" stroke-width="0.8" opacity="0.6"/>')
    for gy in range(-180, 181, 45):
        p_start = to_iso(-200, gy, 0)
        p_end = to_iso(200, gy, 0)
        grid_lines.append(f'<line x1="{p_start[0]}" y1="{p_start[1]}" x2="{p_end[0]}" y2="{p_end[1]}" stroke="#1e293b" stroke-width="0.8" opacity="0.6"/>')

    # 2. Core API Gateway Box at Center (0, 0, 0)
    core_z = 0
    core_dx, core_dy, core_dz = 52, 52, 56
    core_svg = draw_isometric_box(
        0, 0, core_z, core_dx, core_dy, core_dz,
        base_color="#0284c7", stroke_color="#38bdf8", stroke_width=1.5
    )
    elements_to_render.append({
        "depth": 0,
        "svg": core_svg
    })

    # 3. Cables and Worker Nodes
    cables_svg = []
    packet_animations_svg = []
    labels_svg = []

    core_center_iso = to_iso(0, 0, 18)

    for idx, lang in enumerate(languages[:5]):
        wx, wy = worker_offsets[idx]
        pct = lang["percentage"]
        node_color = LANG_COLORS.get(lang["name"], "#0ea5e9")

        node_height = max(24, int(pct * 1.5))
        node_svg = draw_isometric_box(
            wx, wy, 0, 36, 36, node_height,
            base_color=node_color, stroke_width=1.2
        )

        elements_to_render.append({
            "depth": wx + wy,
            "svg": node_svg
        })

        node_base_iso = to_iso(wx, wy, 10)
        mid_x = (core_center_iso[0] + node_base_iso[0]) / 2
        mid_y = (core_center_iso[1] + node_base_iso[1]) / 2 - 12

        cable_id = f"cable_{idx}"
        path_d = f"M {core_center_iso[0]} {core_center_iso[1]} Q {mid_x} {mid_y} {node_base_iso[0]} {node_base_iso[1]}"

        cables_svg.append(
            f'<path id="{cable_id}" d="{path_d}" fill="none" stroke="{node_color}" stroke-width="2" '
            f'stroke-dasharray="4 2" opacity="0.75" />'
        )

        delay = round(idx * (anim_duration / len(languages)), 2)
        packet_animations_svg.append(f"""
        <circle r="3.2" fill="#ffffff" filter="url(#glow-packet)">
            <animateMotion dur="{anim_duration}s" repeatCount="indefinite" begin="{delay}s" path="{path_d}" />
        </circle>
        """)

        label_pos = to_iso(wx, wy, -10)
        labels_svg.append(f"""
        <g transform="translate({label_pos[0]}, {label_pos[1] + 28})">
            <rect x="-48" y="-12" width="96" height="20" rx="3" fill="#0b0f17" fill-opacity="0.85" stroke="{node_color}" stroke-width="0.8"/>
            <text x="0" y="2" fill="#f8fafc" font-size="8.5" font-family="'JetBrains Mono', 'Fira Code', monospace" font-weight="600" text-anchor="middle">
                {lang['name'][:10].upper()} [{pct}%]
            </text>
        </g>
        """)

    # Painter's Algorithm depth sort
    elements_to_render.sort(key=lambda item: item["depth"])
    boxes_svg_str = "".join([item["svg"] for item in elements_to_render])

    # Core Label
    core_label_pos = to_iso(0, 0, core_dz + 8)
    core_label_svg = f"""
    <g transform="translate({core_label_pos[0]}, {core_label_pos[1] - 8})">
        <rect x="-56" y="-13" width="112" height="22" rx="4" fill="#0369a1" fill-opacity="0.9" stroke="#38bdf8" stroke-width="1.2" filter="url(#glow-core)"/>
        <text x="0" y="2" fill="#ffffff" font-size="9" font-family="'JetBrains Mono', 'Fira Code', monospace" font-weight="700" text-anchor="middle">
            CORE GATEWAY
        </text>
    </g>
    """

    status_text = "HEALTHY"
    status_color = "#22c55e"
    throughput = round(commits_30d / 30.0, 1)

    hud_svg = f"""
    <g transform="translate(25, 25)">
        <rect width="270" height="92" rx="6" fill="#161b22" fill-opacity="0.9" stroke="#30363d" stroke-width="1.2"/>
        <circle cx="16" cy="18" r="4.5" fill="{status_color}">
            <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/>
        </circle>
        <text x="28" y="22" fill="#f0f6fc" font-size="10.5" font-family="'JetBrains Mono', 'Fira Code', monospace" font-weight="700">
            SYSTEM: {status_text}
        </text>
        <line x1="10" y1="32" x2="260" y2="32" stroke="#21262d" stroke-width="1"/>
        <text x="14" y="48" fill="#8b949e" font-size="9" font-family="'JetBrains Mono', monospace">NODE OPERATOR:</text>
        <text x="120" y="48" fill="#58a6ff" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="600">@{GITHUB_USERNAME}</text>
        <text x="14" y="64" fill="#8b949e" font-size="9" font-family="'JetBrains Mono', monospace">7D COMMITS:</text>
        <text x="120" y="64" fill="#3fb950" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="600">{commits_7d} pkts</text>
        <text x="14" y="80" fill="#8b949e" font-size="9" font-family="'JetBrains Mono', monospace">30D THROUGHPUT:</text>
        <text x="120" y="80" fill="#d29922" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="600">{commits_30d} ({throughput} / day)</text>
    </g>

    <g transform="translate(625, 25)">
        <rect width="200" height="50" rx="6" fill="#161b22" fill-opacity="0.9" stroke="#30363d" stroke-width="1.2"/>
        <text x="14" y="22" fill="#8b949e" font-size="9" font-family="'JetBrains Mono', monospace">ARCHITECTURE:</text>
        <text x="108" y="22" fill="#a371f7" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="600">ISOMETRIC 3D</text>
        <text x="14" y="38" fill="#8b949e" font-size="9" font-family="'JetBrains Mono', monospace">SYNC INTERVAL:</text>
        <text x="108" y="38" fill="#38bdf8" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="600">12 HOURS</text>
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
    <defs>
        <filter id="glow-core" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="glow-packet" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <radialGradient id="bg-grad" cx="50%" cy="50%" r="70%">
            <stop offset="0%" stop-color="#111827"/>
            <stop offset="100%" stop-color="#0d1117"/>
        </radialGradient>
    </defs>

    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg-grad)" rx="10"/>

    <g id="grid-floor">
        {"".join(grid_lines)}
    </g>

    <g id="network-cables">
        {"".join(cables_svg)}
    </g>

    <g id="isometric-nodes">
        {boxes_svg_str}
    </g>

    {core_label_svg}

    <g id="node-labels">
        {"".join(labels_svg)}
    </g>

    <g id="network-packets">
        {"".join(packet_animations_svg)}
    </g>

    {hud_svg}
</svg>"""
    return svg_content


def main():
    os.makedirs("dist", exist_ok=True)
    data = get_profile_data()
    svg_code = build_svg(data)

    output_path = os.path.join("dist", "devops-3d-network.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_code)

    print(f"[✓] File generated successfully at: {output_path}")


if __name__ == "__main__":
    main()
