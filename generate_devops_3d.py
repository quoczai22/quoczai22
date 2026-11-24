#!/usr/bin/env python3
"""
Generate a 3D Isometric DevOps Network SVG for GitHub Profile.
Pure Python standard library implementation.
Network & NOC (Network Operations Center) telemetry theme.
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

WIDTH = 880
HEIGHT = 500
ORIGIN_X = 440
ORIGIN_Y = 280

COS30 = math.cos(math.radians(30))  # ≈ 0.866025
SIN30 = math.sin(math.radians(30))  # 0.5

# Canonical programming language & DevOps colors
LANG_COLORS = {
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Rust": "#dea584",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "Docker": "#38bdf8",
    "Kubernetes": "#326ce5",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4F5D95",
    "C#": "#178600",
}

FONT_FAMILY = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def shade_color(hex_str, factor):
    """Adjust color brightness with clamping."""
    r, g, b = hex_to_rgb(hex_str)
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def fetch_github_data(username, token):
    """Fetch user commit statistics and languages via GitHub GraphQL API."""
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
        repositories(first: 35, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
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
    """Retrieve live statistics or fallback to realistic default data."""
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
            if sorted_langs:
                total_bytes = sum(s for _, s in sorted_langs)
                languages = [
                    {"name": name, "percentage": round((size / total_bytes) * 100, 1)}
                    for name, size in sorted_langs
                ]
                print(f"[✓] Fetched successfully: 7d={commits_7d}, 30d={commits_30d}, langs={len(languages)}")
                return {
                    "commits_7d": commits_7d,
                    "commits_30d": commits_30d,
                    "languages": languages,
                    "is_fallback": False
                }
        except Exception as e:
            print(f"[!] API fetch failed ({e}). Switching to Fallback dataset...")

    # Realistic Fallback
    return {
        "commits_7d": 24,
        "commits_30d": 98,
        "languages": [
            {"name": "JavaScript", "percentage": 42.0},
            {"name": "Python", "percentage": 26.5},
            {"name": "TypeScript", "percentage": 16.0},
            {"name": "Rust", "percentage": 9.5},
            {"name": "Java", "percentage": 6.0}
        ],
        "is_fallback": True
    }


def render_isometric_cuboid(fx, fy, w, d, h, base_color, stroke_color=None, stroke_width=1, add_rack_lines=False):
    """
    Renders an isometric cuboid anchored at front-bottom vertex (fx, fy).
    Light source from top-left.
    """
    ux = (w / 2) * COS30
    uy = (w / 2) * SIN30
    vx = (d / 2) * COS30
    vy = (d / 2) * SIN30

    fb = (round(fx, 2), round(fy, 2))
    lb = (round(fx - vx, 2), round(fy - vy, 2))
    rb = (round(fx + ux, 2), round(fy - uy, 2))
    bb = (round(fx - vx + ux, 2), round(fy - vy - uy, 2))

    ft = (round(fx, 2), round(fy - h, 2))
    lt = (round(fx - vx, 2), round(fy - vy - h, 2))
    rt = (round(fx + ux, 2), round(fy - uy - h, 2))
    bt = (round(fx - vx + ux, 2), round(fy - vy - uy - h, 2))

    c_top = shade_color(base_color, 1.28)
    c_left = shade_color(base_color, 0.98)
    c_right = shade_color(base_color, 0.65)
    border = stroke_color or shade_color(base_color, 1.45)

    svg = []

    # Left face
    svg.append(
        f'<polygon points="{lb[0]},{lb[1]} {fb[0]},{fb[1]} {ft[0]},{ft[1]} {lt[0]},{lt[1]}" '
        f'fill="{c_left}" stroke="{border}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )
    # Right face
    svg.append(
        f'<polygon points="{fb[0]},{fb[1]} {rb[0]},{rb[1]} {rt[0]},{rt[1]} {ft[0]},{ft[1]}" '
        f'fill="{c_right}" stroke="{border}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )
    # Top face
    svg.append(
        f'<polygon points="{bt[0]},{bt[1]} {rt[0]},{rt[1]} {ft[0]},{ft[1]} {lt[0]},{lt[1]}" '
        f'fill="{c_top}" stroke="{border}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )

    # Server rack slotted horizontal blade vents
    if add_rack_lines and h >= 30:
        step = 10
        for offset_z in range(12, int(h - 8), step):
            l1 = (lb[0], round(lb[1] - offset_z, 2))
            l2 = (fb[0], round(fb[1] - offset_z, 2))
            r1 = (fb[0], round(fb[1] - offset_z, 2))
            r2 = (rb[0], round(rb[1] - offset_z, 2))
            svg.append(f'<line x1="{l1[0]}" y1="{l1[1]}" x2="{l2[0]}" y2="{l2[1]}" stroke="#0f172a" stroke-width="1.2" opacity="0.75"/>')
            svg.append(f'<line x1="{r1[0]}" y1="{r1[1]}" x2="{r2[0]}" y2="{r2[1]}" stroke="#0f172a" stroke-width="1.2" opacity="0.85"/>')
            # Blinking LED status indicator on left rack
            led_pos = (round(lb[0] + (fb[0] - lb[0]) * 0.25, 2), round(lb[1] - offset_z + 2, 2))
            svg.append(f'<circle cx="{led_pos[0]}" cy="{led_pos[1]}" r="1.3" fill="#22c55e" opacity="0.9"/>')

    return "".join(svg), ft


def build_devops_svg(data):
    commits_7d = data["commits_7d"]
    commits_30d = data["commits_30d"]
    languages = data["languages"]

    # Packet velocity based on 7-day commit throughput
    if commits_7d >= 100:
        packet_dur = 1.3
    elif commits_7d >= 30:
        packet_dur = 2.0
    elif commits_7d >= 10:
        packet_dur = 3.0
    else:
        packet_dur = 4.5

    cx = ORIGIN_X
    cy = ORIGIN_Y

    # Isometric floor grid
    grid_svg = []
    grid_step = 40
    grid_count = 5
    for i in range(-grid_count, grid_count + 1):
        su = (cx + (i * grid_step - grid_count * grid_step) * COS30, cy + (i * grid_step + grid_count * grid_step) * SIN30)
        eu = (cx + (i * grid_step + grid_count * grid_step) * COS30, cy + (i * grid_step - grid_count * grid_step) * SIN30)
        grid_svg.append(f'<line x1="{su[0]:.1f}" y1="{su[1]:.1f}" x2="{eu[0]:.1f}" y2="{eu[1]:.1f}" stroke="#1e293b" stroke-width="0.8" opacity="0.55"/>')
        sv = (cx + (-grid_count * grid_step - i * grid_step) * COS30, cy + (-grid_count * grid_step + i * grid_step) * SIN30)
        ev = (cx + (grid_count * grid_step - i * grid_step) * COS30, cy + (grid_count * grid_step + i * grid_step) * SIN30)
        grid_svg.append(f'<line x1="{sv[0]:.1f}" y1="{sv[1]:.1f}" x2="{ev[0]:.1f}" y2="{ev[1]:.1f}" stroke="#1e293b" stroke-width="0.8" opacity="0.55"/>')

    # Ambient intersection dots
    for ix in [-2, 0, 2]:
        for iy in [-2, 0, 2]:
            dx = cx + (ix * grid_step - iy * grid_step) * COS30
            dy = cy + (ix * grid_step + iy * grid_step) * SIN30
            grid_svg.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="1.6" fill="#38bdf8" opacity="0.35"/>')

    render_queue = []

    # 1. CORE BGP ROUTER at Center (cx, cy)
    core_w, core_d = 64, 64
    core_h = 60
    pedestal_svg, _ = render_isometric_cuboid(cx, cy + 12, core_w + 16, core_d + 16, 10, "#0f172a", stroke_color="#334155")
    core_svg, core_ft = render_isometric_cuboid(cx, cy, core_w, core_d, core_h, "#0284c7", stroke_color="#38bdf8", stroke_width=1.5, add_rack_lines=True)

    beacon_cy = core_ft[1] - 18
    beacon_svg = f"""
    <g transform="translate({core_ft[0]}, {beacon_cy})">
        <polygon points="0,-16 14,-7 14,7 0,16 -14,7 -14,-7" fill="#0284c7" fill-opacity="0.4" stroke="#38bdf8" stroke-width="1.4" filter="url(#glow-cyan)"/>
        <polygon points="0,-10 9,-4 9,4 0,10 -9,4 -9,-4" fill="#38bdf8" fill-opacity="0.85">
            <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
        </polygon>
    </g>
    """
    render_queue.append({
        "y": cy,
        "svg": pedestal_svg + core_svg + beacon_svg
    })

    # 2. WORKER POD NODES (5 nodes on an isometric ellipse)
    rx = 230
    ry = 130
    angles = [-90, -18, 54, 126, 198]

    cables_svg = []
    packets_svg = []
    labels_svg = []

    for idx, lang in enumerate(languages[:5]):
        deg = angles[idx]
        rad = math.radians(deg)
        nx = cx + rx * math.cos(rad)
        ny = cy + ry * math.sin(rad)

        pct = lang["percentage"]
        node_color = LANG_COLORS.get(lang["name"], "#0ea5e9")
        node_h = max(32, min(82, int(26 + pct * 0.95)))
        node_w, node_d = 42, 42

        n_pedestal, _ = render_isometric_cuboid(nx, ny + 6, node_w + 8, node_d + 8, 6, "#0f172a", stroke_color="#1e293b")
        n_body, n_ft = render_isometric_cuboid(nx, ny, node_w, node_d, node_h, node_color, stroke_color=shade_color(node_color, 1.4), stroke_width=1.2, add_rack_lines=True)

        render_queue.append({
            "y": ny,
            "svg": n_pedestal + n_body
        })

        # Dual Fiber Optic Cable
        core_port_x = cx
        core_port_y = cy - 14
        node_port_x = nx
        node_port_y = ny - 6

        ctrl_x = (core_port_x + node_port_x) / 2
        ctrl_y = (core_port_y + node_port_y) / 2 - 18

        path_d = f"M {core_port_x:.1f} {core_port_y:.1f} Q {ctrl_x:.1f} {ctrl_y:.1f} {node_port_x:.1f} {node_port_y:.1f}"
        rev_path_d = f"M {node_port_x:.1f} {node_port_y:.1f} Q {ctrl_x:.1f} {ctrl_y:.1f} {core_port_x:.1f} {core_port_y:.1f}"

        cables_svg.append(
            f'<path d="{path_d}" fill="none" stroke="{node_color}" stroke-width="2.2" stroke-dasharray="5 3" opacity="0.65" />'
        )

        delay1 = round(idx * (packet_dur / 5.0), 2)
        delay2 = round(delay1 + (packet_dur / 2.0), 2)

        packets_svg.append(f"""
        <circle r="3" fill="#ffffff" filter="url(#glow-packet)">
            <animateMotion dur="{packet_dur}s" repeatCount="indefinite" begin="{delay1}s" path="{path_d}" />
        </circle>
        <circle r="2.2" fill="{node_color}" filter="url(#glow-packet)">
            <animateMotion dur="{packet_dur}s" repeatCount="indefinite" begin="{delay2}s" path="{rev_path_d}" />
        </circle>
        """)

        # Network interface label below each node (NO TRUNCATION)
        label_y = ny + 14
        lang_display = lang['name'].upper()
        labels_svg.append(f"""
        <g transform="translate({nx:.1f}, {label_y:.1f})">
            <rect x="-64" y="-11" width="128" height="22" rx="4" fill="#0b0f17" fill-opacity="0.92" stroke="{node_color}" stroke-width="0.9"/>
            <circle cx="-52" cy="0" r="3" fill="{node_color}"/>
            <text x="-43" y="3.5" fill="#f8fafc" font-size="8.5" font-family="{FONT_FAMILY}" font-weight="700">
                ETH{idx}: {lang_display}
            </text>
            <text x="54" y="3.5" fill="#38bdf8" font-size="8" font-family="{FONT_FAMILY}" font-weight="600" text-anchor="end">
                {pct}%
            </text>
        </g>
        """)

    # Painter's Algorithm Depth Sort
    render_queue.sort(key=lambda item: item["y"])
    rendered_boxes = "".join([item["svg"] for item in render_queue])

    # Core Router Label
    core_label_svg = f"""
    <g transform="translate({cx}, {cy + 24})">
        <rect x="-72" y="-12" width="144" height="24" rx="4" fill="#0369a1" fill-opacity="0.92" stroke="#38bdf8" stroke-width="1.3" filter="url(#glow-cyan)"/>
        <text x="0" y="4" fill="#ffffff" font-size="9.5" font-family="{FONT_FAMILY}" font-weight="700" text-anchor="middle">
            CORE ROUTER [BGP-01]
        </text>
    </g>
    """

    # NOC Telemetry & Network-Themed HUD
    throughput = round(commits_30d / 30.0, 1)
    hud_svg = f"""
    <!-- Left HUD: NOC Telemetry -->
    <g transform="translate(24, 22)">
        <rect width="290" height="96" rx="6" fill="#0f172a" fill-opacity="0.92" stroke="#334155" stroke-width="1.2"/>
        <circle cx="16" cy="18" r="4.5" fill="#22c55e">
            <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
        </circle>
        <text x="28" y="21.5" fill="#f8fafc" font-size="10.5" font-family="{FONT_FAMILY}" font-weight="700">
            NOC TELEMETRY // GATEWAY ONLINE
        </text>
        <line x1="12" y1="32" x2="278" y2="32" stroke="#1e293b" stroke-width="1"/>
        <text x="14" y="48" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">NET OPERATOR:</text>
        <text x="135" y="48" fill="#38bdf8" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">@{GITHUB_USERNAME} [ADMIN]</text>
        <text x="14" y="64" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">7D COMMITS (RX):</text>
        <text x="135" y="64" fill="#22c55e" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">{commits_7d} PKTS [ACK 100%]</text>
        <text x="14" y="80" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">30D BANDWIDTH:</text>
        <text x="135" y="80" fill="#f59e0b" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">{commits_30d} FRAMES ({throughput} req/d)</text>
    </g>

    <!-- Right HUD: Network Topology Spec -->
    <g transform="translate(636, 22)">
        <rect width="220" height="96" rx="6" fill="#0f172a" fill-opacity="0.92" stroke="#334155" stroke-width="1.2"/>
        <text x="14" y="21" fill="#f8fafc" font-size="10.5" font-family="{FONT_FAMILY}" font-weight="700">
            TOPOLOGY SPECS
        </text>
        <line x1="12" y1="32" x2="208" y2="32" stroke="#1e293b" stroke-width="1"/>
        <text x="14" y="48" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">ARCHITECTURE:</text>
        <text x="110" y="48" fill="#a855f7" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">BGP TCP MESH</text>
        <text x="14" y="64" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">PACKET LOSS:</text>
        <text x="110" y="64" fill="#22c55e" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">0.0% [LOSSLESS]</text>
        <text x="14" y="80" fill="#64748b" font-size="8.8" font-family="{FONT_FAMILY}">LINK LATENCY:</text>
        <text x="110" y="80" fill="#38bdf8" font-size="8.8" font-family="{FONT_FAMILY}" font-weight="700">12ms (PING RTT)</text>
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
    <defs>
        <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
        <filter id="glow-packet" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <radialGradient id="space-bg" cx="50%" cy="50%" r="75%">
            <stop offset="0%" stop-color="#111827"/>
            <stop offset="60%" stop-color="#0d1117"/>
            <stop offset="100%" stop-color="#06090e"/>
        </radialGradient>
        <radialGradient id="center-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#0284c7" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#0284c7" stop-opacity="0"/>
        </radialGradient>
    </defs>

    <!-- Deep Space Terminal Background -->
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#space-bg)" rx="10"/>

    <!-- Subtle Ambient Center Glow -->
    <ellipse cx="{cx}" cy="{cy}" rx="290" ry="170" fill="url(#center-glow)"/>

    <!-- Isometric Symmetrical Floor Grid -->
    <g id="isometric-grid">
        {"".join(grid_svg)}
    </g>

    <!-- Fiber Optic Data Cables -->
    <g id="data-cables">
        {"".join(cables_svg)}
    </g>

    <!-- 3D Isometric Nodes (Depth Ordered) -->
    <g id="isometric-nodes">
        {rendered_boxes}
    </g>

    <!-- Core Router Label -->
    {core_label_svg}

    <!-- Worker Node Labels -->
    <g id="node-labels">
        {"".join(labels_svg)}
    </g>

    <!-- Animated Data Packets -->
    <g id="data-packets">
        {"".join(packets_svg)}
    </g>

    <!-- NOC Telemetry Overlay -->
    {hud_svg}
</svg>"""
    return svg_content


def main():
    os.makedirs("dist", exist_ok=True)
    data = get_profile_data()
    svg_code = build_devops_svg(data)

    output_path = os.path.join("dist", "devops-3d-network.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_code)

    print(f"[✓] SVG generated cleanly at: {output_path}")


if __name__ == "__main__":
    main()
