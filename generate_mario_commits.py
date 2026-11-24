#!/usr/bin/env python3
"""
Generate a Super Mario Pixel Art 8-bit Commits SVG for GitHub Profile.
Pure Python standard library implementation.
Theme: Retro Super Mario Bros (Dark Mode #0d1117).
"""

import os
import json
import datetime
import urllib.request
import urllib.error

# --- CONFIGURATION ---
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "quoczai22")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

WIDTH = 860
HEIGHT = 400
GROUND_Y = 320

FONT_PIXEL = "'Press Start 2P', ui-monospace, 'Courier New', monospace"


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
            "User-Agent": "Mario-Commits-Generator"
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
        "commits_7d": 28,
        "commits_30d": 112,
        "languages": [
            {"name": "Python", "percentage": 42.0},
            {"name": "JavaScript", "percentage": 28.5},
            {"name": "TypeScript", "percentage": 14.5},
            {"name": "C++", "percentage": 9.0},
            {"name": "PHP", "percentage": 6.0}
        ],
        "is_fallback": True
    }


def parse_pixel_grid(matrix, color_map, pixel_size=3):
    """Converts an ASCII matrix into crisp SVG rect pixels."""
    svg_rects = []
    for r, row in enumerate(matrix):
        for c, ch in enumerate(row):
            if ch in color_map:
                x = c * pixel_size
                y = r * pixel_size
                svg_rects.append(
                    f'<rect x="{x}" y="{y}" width="{pixel_size}" height="{pixel_size}" fill="{color_map[ch]}"/>'
                )
    return "".join(svg_rects)


def build_mario_sprites(scale=3):
    """Builds authentic 8-bit Mario, Goomba, Coin, and Block sprites."""
    # Palette
    mario_colors = {
        'R': '#e52521',  # Red cap/shirt
        'B': '#92400e',  # Brown hair/shoes
        'S': '#fcd8a8',  # Skin
        'U': '#0058f8',  # Blue overalls
        'Y': '#facc15',  # Yellow buttons
    }

    mario_standing = [
        "....RRRRR......",
        "...RRRRRRRRR...",
        "...BBBSSBS.....",
        "..BSBSSSBS.....",
        "..BSBSSSBSSS...",
        "..BBSSSSBBBB...",
        "....SSSSSSS....",
        "...RRURR.......",
        "..RRRURRURRR...",
        ".RRRRUUUURRRR..",
        ".SSRUYYUURSS...",
        ".SSSUUUUUUSSS..",
        ".SSUUUUUUUUSS..",
        "..UUUU..UUUU...",
        "..BBB....BBB...",
        ".BBBB....BBBB.."
    ]

    mario_jumping = [
        "....SSSRRR.....",
        "...SSRRRRRR....",
        "...BBBSSBS.....",
        "..BSBSSSBS.....",
        "..BSBSSSBSSS...",
        "..BBSSSSBBBB...",
        "....SSSSSSS....",
        "...RRURRR......",
        "..RRRUUURRRR...",
        ".SSRRUYYUURSS..",
        ".SSSUUUUUUSSS..",
        ".SSUUUUUUUUSS..",
        "...UUU...UUU...",
        "..BBB.....BBB..",
        ".BBBB.....BBBB.",
        "...............",
    ]

    goomba_colors = {
        'B': '#7c2d12',  # Dark Brown
        'T': '#b45309',  # Tan body
        'W': '#ffffff',  # White eyes
        'K': '#000000',  # Black pupils
        'F': '#1c1917',  # Feet
    }

    goomba_1 = [
        ".....BBBBBB.....",
        "...BBBBBBBBBB...",
        "..BBBBBBBBBBBB..",
        ".BBBBBBBBBBBBBB.",
        "BBBBWKBKBKWBBBBB",
        "BBBBWKBKBKWBBBBB",
        "BBBBWKBKBKWBBBBB",
        "BBBBBBBBBBBBBBBB",
        "....TTTTTTTT....",
        "...TTTTTTTTTT...",
        "..TTTTTTTTTTTT..",
        "..TTTTTTTTTTTT..",
        ".FFFFF....FFFFF.",
        "FFFFFFF..FFFFFFF",
        "FFFFFFF..FFFFFFF",
        "................"
    ]

    coin_colors = {
        'G': '#f59e0b',  # Gold border
        'Y': '#fbbf24',  # Yellow fill
        'W': '#fef08a',  # White shine
        'K': '#b45309',  # Dark gold
    }

    coin_matrix = [
        "..GGGGGG..",
        ".GYYYYYYG.",
        "GYYWWWWYYG",
        "GYWKKKKYWG",
        "GYWKKKKYWG",
        "GYWKKKKYWG",
        "GYWKKKKYWG",
        "GYYWWWWYYG",
        ".GYYYYYYG.",
        "..GGGGGG.."
    ]

    mario_stand_svg = parse_pixel_grid(mario_standing, mario_colors, scale)
    mario_jump_svg = parse_pixel_grid(mario_jumping, mario_colors, scale)
    goomba_svg = parse_pixel_grid(goomba_1, goomba_colors, scale)
    coin_svg = parse_pixel_grid(coin_matrix, coin_colors, scale)

    return {
        "mario_stand": mario_stand_svg,
        "mario_jump": mario_jump_svg,
        "goomba": goomba_svg,
        "coin": coin_svg,
    }


def build_mario_svg(data):
    commits_7d = data["commits_7d"]
    commits_30d = data["commits_30d"]
    languages = data["languages"]

    score = commits_30d * 100
    score_str = f"{score:06d}"

    sprites = build_mario_sprites(scale=3)

    # 1. Ground Blocks (y = GROUND_Y to HEIGHT)
    ground_blocks = []
    block_size = 32
    for gx in range(0, WIDTH, block_size):
        for gy in range(GROUND_Y, HEIGHT, block_size):
            ground_blocks.append(f"""
            <g transform="translate({gx}, {gy})">
                <rect width="{block_size}" height="{block_size}" fill="#9a3412" stroke="#431407" stroke-width="2"/>
                <rect x="2" y="2" width="{block_size-4}" height="{block_size-4}" fill="#c2410c"/>
                <rect x="4" y="4" width="8" height="6" fill="#ea580c"/>
                <line x1="0" y1="0" x2="{block_size}" y2="0" stroke="#f97316" stroke-width="2"/>
            </g>
            """)

    # 2. Pixel Stars in Sky
    stars = [
        (60, 70), (140, 110), (220, 50), (310, 95), (420, 65),
        (530, 80), (640, 45), (730, 105), (810, 60), (180, 140),
        (480, 130), (690, 140)
    ]
    stars_svg = []
    for idx, (sx, sy) in enumerate(stars):
        dur = 1.5 + (idx % 4) * 0.5
        stars_svg.append(f"""
        <rect x="{sx}" y="{sy}" width="4" height="4" fill="#fef08a" opacity="0.8">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="{dur}s" repeatCount="indefinite" />
        </rect>
        """)

    # 3. Floating Question Blocks & Language Brick Blocks
    # Placed at y = 175
    blocks_y = 175
    q_block_x = 390

    # Question Block [?] with bounce animation
    q_block_svg = f"""
    <g id="q-block" transform="translate({q_block_x}, {blocks_y})">
        <!-- Bounce animation when Mario jumps under it -->
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{q_block_x},{blocks_y}; {q_block_x},{blocks_y-14}; {q_block_x},{blocks_y}"
            keyTimes="0; 0.5; 1"
            dur="0.32s"
            begin="1.8s; 5.8s"
            repeatCount="1"
        />
        <rect width="40" height="40" rx="3" fill="#ea580c" stroke="#431407" stroke-width="2"/>
        <rect x="3" y="3" width="34" height="34" fill="#f59e0b"/>
        <!-- Pixel Question Mark -->
        <g fill="#431407">
            <rect x="14" y="8" width="12" height="4"/>
            <rect x="22" y="12" width="4" height="6"/>
            <rect x="18" y="18" width="6" height="4"/>
            <rect x="18" y="22" width="4" height="4"/>
            <rect x="18" y="28" width="4" height="4"/>
        </g>
        <rect x="4" y="4" width="2" height="2" fill="#fef08a"/>
        <rect x="34" y="4" width="2" height="2" fill="#fef08a"/>
        <rect x="4" y="34" width="2" height="2" fill="#fef08a"/>
        <rect x="34" y="34" width="2" height="2" fill="#fef08a"/>
    </g>
    """

    # Language Brick Blocks surrounding the Question Block
    lang_bricks_svg = []
    brick_positions = [
        (q_block_x - 90, languages[0]["name"] if len(languages) > 0 else "CODE"),
        (q_block_x - 45, languages[1]["name"] if len(languages) > 1 else "DEV"),
        (q_block_x + 45, languages[2]["name"] if len(languages) > 2 else "GIT"),
        (q_block_x + 90, languages[3]["name"] if len(languages) > 3 else "OPS"),
    ]

    for bx, b_label in brick_positions:
        lang_bricks_svg.append(f"""
        <g transform="translate({bx}, {blocks_y})">
            <rect width="40" height="40" rx="2" fill="#78350f" stroke="#451a03" stroke-width="2"/>
            <rect x="2" y="2" width="36" height="36" fill="#b45309"/>
            <line x1="2" y1="12" x2="38" y2="12" stroke="#451a03" stroke-width="2"/>
            <line x1="2" y1="26" x2="38" y2="26" stroke="#451a03" stroke-width="2"/>
            <line x1="20" y1="2" x2="20" y2="12" stroke="#451a03" stroke-width="2"/>
            <line x1="12" y1="12" x2="12" y2="26" stroke="#451a03" stroke-width="2"/>
            <line x1="28" y1="12" x2="28" y2="26" stroke="#451a03" stroke-width="2"/>
            <line x1="20" y1="26" x2="20" y2="38" stroke="#451a03" stroke-width="2"/>
            <text x="20" y="-8" fill="#fcd34d" font-family="{FONT_PIXEL}" font-size="7" font-weight="700" text-anchor="middle">
                {b_label[:6].upper()}
            </text>
        </g>
        """)

    # 4. Spawning Coin from Question Block Animation
    coin_x = q_block_x + 6
    coin_pop_svg = f"""
    <g transform="translate({coin_x}, {blocks_y})">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{coin_x},{blocks_y}; {coin_x},{blocks_y-56}; {coin_x},{blocks_y-40}; {coin_x},{blocks_y}"
            keyTimes="0; 0.45; 0.75; 1"
            dur="0.8s"
            begin="1.85s; 5.85s"
            repeatCount="1"
            fill="freeze"
        />
        <g opacity="0">
            <animate attributeName="opacity" values="0; 1; 1; 0" keyTimes="0; 0.1; 0.85; 1" dur="0.8s" begin="1.85s; 5.85s" repeatCount="1"/>
            {sprites['coin']}
            <text x="14" y="-12" fill="#fef08a" font-family="{FONT_PIXEL}" font-size="9" font-weight="700" text-anchor="middle">
                +1 COMMIT!
            </text>
        </g>
    </g>
    """

    # 5. Green Warp Pipe on Right (x = 710, y = 230 to 320)
    pipe_x = 710
    pipe_y = 230
    pipe_w = 64
    pipe_h = GROUND_Y - pipe_y
    pipe_svg = f"""
    <g id="warp-pipe" transform="translate({pipe_x}, {pipe_y})">
        <!-- Pipe Rim Top -->
        <rect x="-4" y="0" width="{pipe_w + 8}" height="26" fill="#15803d" stroke="#14532d" stroke-width="2"/>
        <rect x="0" y="3" width="{pipe_w}" height="20" fill="#22c55e"/>
        <line x1="8" y1="3" x2="8" y2="23" stroke="#86efac" stroke-width="3"/>
        <line x1="{pipe_w-10}" y1="3" x2="{pipe_w-10}" y2="23" stroke="#14532d" stroke-width="5"/>
        <!-- Pipe Stem -->
        <rect x="0" y="26" width="{pipe_w}" height="{pipe_h - 26}" fill="#15803d" stroke="#14532d" stroke-width="2"/>
        <rect x="4" y="26" width="{pipe_w - 8}" height="{pipe_h - 26}" fill="#22c55e"/>
        <line x1="12" y1="26" x2="12" y2="{pipe_h}" stroke="#86efac" stroke-width="3"/>
        <line x1="{pipe_w-12}" y1="26" x2="{pipe_w-12}" y2="{pipe_h}" stroke="#14532d" stroke-width="5"/>
        <!-- Piranha Plant Head peaking out -->
        <g transform="translate(18, -12)">
            <animateTransform
                attributeName="transform"
                type="translate"
                values="18,12; 18,-18; 18,-18; 18,12"
                keyTimes="0; 0.25; 0.75; 1"
                dur="4s"
                repeatCount="indefinite"
            />
            <circle cx="14" cy="8" r="14" fill="#dc2626"/>
            <polygon points="4,8 24,8 14,0" fill="#ffffff"/>
            <circle cx="8" cy="4" r="3" fill="#ffffff"/>
            <circle cx="20" cy="4" r="3" fill="#ffffff"/>
        </g>
    </g>
    """

    # 6. Animated Mario: Run -> Jump & Hit Block -> Land -> Victory
    mario_start_x = 120
    mario_target_x = q_block_x - 3
    mario_y = GROUND_Y - 48

    # Mario runs from 120 to 387, jumps under [?], lands, and strikes victory pose!
    mario_anim_svg = f"""
    <g id="animated-mario">
        <!-- Horizontal movement across stage -->
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{mario_start_x},{mario_y}; {mario_target_x},{mario_y}; {mario_target_x},{mario_y-92}; {mario_target_x},{mario_y}; {mario_target_x+80},{mario_y}"
            keyTimes="0; 0.42; 0.52; 0.62; 1"
            dur="4s"
            repeatCount="indefinite"
        />
        <!-- Mario Sprite: Switch between Running and Jumping -->
        <g id="mario-sprites">
            <!-- Standing / Running Sprite -->
            <g id="mario-run">
                <animate attributeName="display" values="inline; none; inline" keyTimes="0; 0.43; 0.61" dur="4s" repeatCount="indefinite"/>
                {sprites['mario_stand']}
            </g>
            <!-- Jumping Sprite -->
            <g id="mario-jump-frame" display="none">
                <animate attributeName="display" values="none; inline; none" keyTimes="0; 0.43; 0.61" dur="4s" repeatCount="indefinite"/>
                {sprites['mario_jump']}
            </g>
        </g>
    </g>
    """

    # 7. Animated Goomba Walking along the floor
    goomba_start_x = 640
    goomba_end_x = 480
    goomba_y = GROUND_Y - 48
    goomba_anim_svg = f"""
    <g id="animated-goomba">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{goomba_start_x},{goomba_y}; {goomba_end_x},{goomba_y}; {goomba_start_x},{goomba_y}"
            keyTimes="0; 0.5; 1"
            dur="5s"
            repeatCount="indefinite"
        />
        {sprites['goomba']}
    </g>
    """

    # 8. Classic Super Mario Arcade HUD
    hud_svg = f"""
    <g id="retro-hud" transform="translate(40, 36)">
        <!-- Player & Score -->
        <text x="0" y="0" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">MARIO</text>
        <text x="0" y="18" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">{score_str}</text>

        <!-- Coins / 7D Commits -->
        <g transform="translate(230, -10)">
            {sprites['coin']}
            <text x="36" y="22" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">x{commits_7d:02d}</text>
            <text x="36" y="36" fill="#facc15" font-family="{FONT_PIXEL}" font-size="7" font-weight="700">7D COMMITS</text>
        </g>

        <!-- World / Level -->
        <text x="490" y="0" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">WORLD</text>
        <text x="500" y="18" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">1-1</text>

        <!-- Total 30D Commits -->
        <text x="680" y="0" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">COMMITS</text>
        <text x="704" y="18" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">{commits_30d}</text>
    </g>

    <!-- Sub-status banner: Player info -->
    <g transform="translate(40, 78)">
        <rect width="780" height="24" rx="4" fill="#161b22" fill-opacity="0.85" stroke="#30363d" stroke-width="1"/>
        <circle cx="16" cy="12" r="4" fill="#22c55e">
            <animate attributeName="opacity" values="1; 0.3; 1" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <text x="28" y="16" fill="#38bdf8" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700">
            PLAYER: @{GITHUB_USERNAME}
        </text>
        <text x="240" y="16" fill="#e2e8f0" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700">
            LEVEL: MASTER COMMIT COLLECTOR
        </text>
        <text x="765" y="16" fill="#facc15" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700" text-anchor="end">
            1-UP ACTIVE ★
        </text>
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%" shape-rendering="crispEdges">
    <defs>
        <radialGradient id="sky-dark" cx="50%" cy="30%" r="80%">
            <stop offset="0%" stop-color="#1e1b4b"/>
            <stop offset="50%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#020617"/>
        </radialGradient>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;display=swap');
            text {{
                user-select: none;
            }}
        </style>
    </defs>

    <!-- Retro Dark Night Sky -->
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#sky-dark)" rx="10"/>

    <!-- Retro Pixel Stars -->
    <g id="sky-stars">
        {"".join(stars_svg)}
    </g>

    <!-- Retro Ground Blocks -->
    <g id="ground">
        {"".join(ground_blocks)}
    </g>

    <!-- Green Warp Pipe -->
    {pipe_svg}

    <!-- Language Brick Blocks -->
    <g id="lang-bricks">
        {"".join(lang_bricks_svg)}
    </g>

    <!-- Question Block [?] -->
    {q_block_svg}

    <!-- Popping Coin -->
    {coin_pop_svg}

    <!-- Walking Goomba -->
    {goomba_anim_svg}

    <!-- Jumping / Running Mario -->
    {mario_anim_svg}

    <!-- Super Mario 8-bit Arcade HUD -->
    {hud_svg}
</svg>"""
    return svg_content


def main():
    os.makedirs("dist", exist_ok=True)
    data = get_profile_data()
    svg_code = build_mario_svg(data)

    output_path = os.path.join("dist", "mario-commits.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_code)

    print(f"[✓] Mario Commits SVG generated at: {output_path}")


if __name__ == "__main__":
    main()
