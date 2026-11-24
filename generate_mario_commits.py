#!/usr/bin/env python3
"""
Generate a Super Mario Pixel Art 8-bit Commits SVG for GitHub Profile.
Pure Python standard library implementation.
Theme: Authentic NES Super Mario Bros World 1-1 (Bright Sky #5c94fc).
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
    """Builds authentic 8-bit Mario, Goomba, and Coin sprites."""
    mario_colors = {
        'R': '#e52521',  # Red cap/shirt
        'B': '#6b2f0a',  # Brown hair/shoes
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
        'B': '#7c2d12',
        'T': '#b45309',
        'W': '#ffffff',
        'K': '#000000',
        'F': '#1c1917',
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
        'G': '#b45309',
        'Y': '#facc15',
        'W': '#fef08a',
        'K': '#78350f',
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

    return {
        "mario_stand": parse_pixel_grid(mario_standing, mario_colors, scale),
        "mario_jump": parse_pixel_grid(mario_jumping, mario_colors, scale),
        "goomba": parse_pixel_grid(goomba_1, goomba_colors, scale),
        "coin": parse_pixel_grid(coin_matrix, coin_colors, scale),
    }


def draw_pixel_cloud(cx, cy, width=70, height=30):
    """Draws a classic puffy 8-bit Mario cloud."""
    return f"""
    <g transform="translate({cx}, {cy})">
        <!-- Main white cloud body -->
        <rect x="12" y="0" width="{width - 24}" height="{height}" rx="12" fill="#ffffff"/>
        <rect x="0" y="8" width="{width}" height="{height - 8}" rx="8" fill="#ffffff"/>
        <!-- Soft blue underside shadow -->
        <rect x="4" y="{height - 4}" width="{width - 8}" height="4" rx="2" fill="#84c0fc"/>
        <!-- Cute pixel cloud eyes -->
        <rect x="{width * 0.35:.0f}" y="10" width="3" height="7" fill="#000000"/>
        <rect x="{width * 0.62:.0f}" y="10" width="3" height="7" fill="#000000"/>
    </g>
    """


def draw_pixel_hill(hx, hy, width=120, height=65):
    """Draws a classic Super Mario World 1-1 green hill."""
    return f"""
    <g transform="translate({hx}, {hy})">
        <!-- Green hill dome -->
        <ellipse cx="{width/2}" cy="{height}" rx="{width/2}" ry="{height}" fill="#00a800" stroke="#000000" stroke-width="2"/>
        <!-- Lighter green highlight -->
        <ellipse cx="{width/2}" cy="{height}" rx="{width/2 - 6}" ry="{height - 6}" fill="#00c800"/>
        <!-- Dark spot marks -->
        <ellipse cx="{width * 0.35}" cy="{height * 0.5}" rx="3" ry="6" fill="#008000"/>
        <ellipse cx="{width * 0.65}" cy="{height * 0.4}" rx="4" ry="7" fill="#008000"/>
    </g>
    """


def build_mario_svg(data):
    commits_7d = data["commits_7d"]
    commits_30d = data["commits_30d"]
    languages = data["languages"]

    score = commits_30d * 100
    score_str = f"{score:06d}"

    sprites = build_mario_sprites(scale=3)

    # 1. Background Hills & Bushes
    hills_svg = [
        draw_pixel_hill(40, GROUND_Y - 70, 140, 70),
        draw_pixel_hill(460, GROUND_Y - 50, 100, 50),
    ]

    # Green bushes
    bushes_svg = f"""
    <g transform="translate(230, {GROUND_Y - 30})">
        <circle cx="20" cy="18" r="16" fill="#00a800" stroke="#000000" stroke-width="1.5"/>
        <circle cx="45" cy="12" r="20" fill="#00c800" stroke="#000000" stroke-width="1.5"/>
        <circle cx="70" cy="18" r="16" fill="#00a800" stroke="#000000" stroke-width="1.5"/>
    </g>
    """

    # 2. Pixel Clouds floating across bright sky
    clouds_svg = [
        draw_pixel_cloud(80, 50, 80, 36),
        draw_pixel_cloud(340, 75, 90, 38),
        draw_pixel_cloud(630, 40, 100, 42),
    ]

    # 3. Ground Blocks: Classic NES Brick with Green Grass Top
    ground_blocks = []
    block_size = 32
    for gx in range(0, WIDTH, block_size):
        # Top block with grass cap
        ground_blocks.append(f"""
        <g transform="translate({gx}, {GROUND_Y})">
            <!-- Orange-brown dirt brick -->
            <rect width="{block_size}" height="{block_size}" fill="#c84c0c" stroke="#000000" stroke-width="1.5"/>
            <rect x="2" y="8" width="{block_size-4}" height="{block_size-10}" fill="#e86828"/>
            <rect x="4" y="10" width="8" height="6" fill="#fc9838"/>
            <!-- Bright Green Grass Cap -->
            <rect x="0" y="0" width="{block_size}" height="8" fill="#00a800"/>
            <rect x="0" y="0" width="{block_size}" height="4" fill="#00e800"/>
            <line x1="0" y1="0" x2="{block_size}" y2="0" stroke="#000000" stroke-width="1.5"/>
        </g>
        """)
        # Sub-ground row
        for gy in range(GROUND_Y + block_size, HEIGHT, block_size):
            ground_blocks.append(f"""
            <g transform="translate({gx}, {gy})">
                <rect width="{block_size}" height="{block_size}" fill="#c84c0c" stroke="#000000" stroke-width="1.5"/>
                <rect x="2" y="2" width="{block_size-4}" height="{block_size-4}" fill="#e86828"/>
                <rect x="4" y="4" width="8" height="6" fill="#fc9838"/>
            </g>
            """)

    # 4. Floating Question Blocks & Language Brick Blocks (y = 175)
    blocks_y = 175
    q_block_x = 390

    # Question Block [?] with bounce animation
    q_block_svg = f"""
    <g id="q-block" transform="translate({q_block_x}, {blocks_y})">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{q_block_x},{blocks_y}; {q_block_x},{blocks_y-14}; {q_block_x},{blocks_y}"
            keyTimes="0; 0.5; 1"
            dur="0.32s"
            begin="1.8s; 5.8s"
            repeatCount="1"
        />
        <rect width="40" height="40" rx="3" fill="#c84c0c" stroke="#000000" stroke-width="2"/>
        <rect x="3" y="3" width="34" height="34" fill="#fc9838"/>
        <rect x="5" y="5" width="30" height="30" fill="#fce000"/>
        <!-- Pixel Question Mark -->
        <g fill="#884400">
            <rect x="14" y="8" width="12" height="4"/>
            <rect x="22" y="12" width="4" height="6"/>
            <rect x="18" y="18" width="6" height="4"/>
            <rect x="18" y="22" width="4" height="4"/>
            <rect x="18" y="28" width="4" height="4"/>
        </g>
        <!-- Corner rivets -->
        <rect x="4" y="4" width="3" height="3" fill="#ffffff"/>
        <rect x="33" y="4" width="3" height="3" fill="#ffffff"/>
        <rect x="4" y="33" width="3" height="3" fill="#884400"/>
        <rect x="33" y="33" width="3" height="3" fill="#884400"/>
    </g>
    """

    # Language Brick Blocks
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
            <rect width="40" height="40" rx="2" fill="#c84c0c" stroke="#000000" stroke-width="2"/>
            <rect x="2" y="2" width="36" height="36" fill="#e86828"/>
            <line x1="2" y1="12" x2="38" y2="12" stroke="#000000" stroke-width="1.5"/>
            <line x1="2" y1="26" x2="38" y2="26" stroke="#000000" stroke-width="1.5"/>
            <line x1="20" y1="2" x2="20" y2="12" stroke="#000000" stroke-width="1.5"/>
            <line x1="12" y1="12" x2="12" y2="26" stroke="#000000" stroke-width="1.5"/>
            <line x1="28" y1="12" x2="28" y2="26" stroke="#000000" stroke-width="1.5"/>
            <line x1="20" y1="26" x2="20" y2="38" stroke="#000000" stroke-width="1.5"/>
            <text x="20" y="-8" fill="#ffffff" stroke="#000000" stroke-width="0.8" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700" text-anchor="middle">
                {b_label[:6].upper()}
            </text>
        </g>
        """)

    # 5. Spawning Coin from Question Block Animation
    coin_x = q_block_x + 6
    coin_pop_svg = f"""
    <g transform="translate({coin_x}, {blocks_y})">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{coin_x},{blocks_y}; {coin_x},{blocks_y-58}; {coin_x},{blocks_y-42}; {coin_x},{blocks_y}"
            keyTimes="0; 0.45; 0.75; 1"
            dur="0.8s"
            begin="1.85s; 5.85s"
            repeatCount="1"
            fill="freeze"
        />
        <g opacity="0">
            <animate attributeName="opacity" values="0; 1; 1; 0" keyTimes="0; 0.1; 0.85; 1" dur="0.8s" begin="1.85s; 5.85s" repeatCount="1"/>
            {sprites['coin']}
            <text x="14" y="-12" fill="#ffffff" stroke="#000000" stroke-width="1.2" font-family="{FONT_PIXEL}" font-size="9" font-weight="700" text-anchor="middle">
                +1 COMMIT!
            </text>
        </g>
    </g>
    """

    # 6. Classic Green Warp Pipe on Right (x = 710, y = 230 to 320)
    pipe_x = 710
    pipe_y = 230
    pipe_w = 64
    pipe_h = GROUND_Y - pipe_y
    pipe_svg = f"""
    <g id="warp-pipe" transform="translate({pipe_x}, {pipe_y})">
        <!-- Pipe Rim Top -->
        <rect x="-4" y="0" width="{pipe_w + 8}" height="26" fill="#00a800" stroke="#000000" stroke-width="2"/>
        <rect x="0" y="3" width="{pipe_w}" height="20" fill="#00e800"/>
        <line x1="8" y1="3" x2="8" y2="23" stroke="#ffffff" stroke-width="3"/>
        <line x1="{pipe_w-10}" y1="3" x2="{pipe_w-10}" y2="23" stroke="#007000" stroke-width="5"/>
        <!-- Pipe Stem -->
        <rect x="0" y="26" width="{pipe_w}" height="{pipe_h - 26}" fill="#00a800" stroke="#000000" stroke-width="2"/>
        <rect x="4" y="26" width="{pipe_w - 8}" height="{pipe_h - 26}" fill="#00e800"/>
        <line x1="12" y1="26" x2="12" y2="{pipe_h}" stroke="#ffffff" stroke-width="3"/>
        <line x1="{pipe_w-12}" y1="26" x2="{pipe_w-12}" y2="{pipe_h}" stroke="#007000" stroke-width="5"/>
        <!-- Piranha Plant Head -->
        <g transform="translate(18, -12)">
            <animateTransform
                attributeName="transform"
                type="translate"
                values="18,12; 18,-18; 18,-18; 18,12"
                keyTimes="0; 0.25; 0.75; 1"
                dur="4s"
                repeatCount="indefinite"
            />
            <circle cx="14" cy="8" r="14" fill="#e52521" stroke="#000000" stroke-width="1.5"/>
            <polygon points="4,8 24,8 14,0" fill="#ffffff"/>
            <circle cx="8" cy="4" r="3" fill="#ffffff"/>
            <circle cx="20" cy="4" r="3" fill="#ffffff"/>
        </g>
    </g>
    """

    # 7. Animated Mario: Run -> Jump & Hit Block -> Land
    mario_start_x = 120
    mario_target_x = q_block_x - 3
    mario_y = GROUND_Y - 48

    mario_anim_svg = f"""
    <g id="animated-mario">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{mario_start_x},{mario_y}; {mario_target_x},{mario_y}; {mario_target_x},{mario_y-92}; {mario_target_x},{mario_y}; {mario_target_x+80},{mario_y}"
            keyTimes="0; 0.42; 0.52; 0.62; 1"
            dur="4s"
            repeatCount="indefinite"
        />
        <g id="mario-sprites">
            <g id="mario-run">
                <animate attributeName="display" values="inline; none; inline" keyTimes="0; 0.43; 0.61" dur="4s" repeatCount="indefinite"/>
                {sprites['mario_stand']}
            </g>
            <g id="mario-jump-frame" display="none">
                <animate attributeName="display" values="none; inline; none" keyTimes="0; 0.43; 0.61" dur="4s" repeatCount="indefinite"/>
                {sprites['mario_jump']}
            </g>
        </g>
    </g>
    """

    # 8. Animated Goomba Walking
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

    # 9. Super Mario Classic NES Arcade HUD (White text with black stroke for crisp readability)
    hud_svg = f"""
    <g id="retro-hud" transform="translate(40, 36)">
        <!-- Player & Score -->
        <text x="0" y="0" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">MARIO</text>
        <text x="0" y="18" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">{score_str}</text>

        <!-- Coins / 7D Commits -->
        <g transform="translate(230, -10)">
            {sprites['coin']}
            <text x="36" y="22" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">x{commits_7d:02d}</text>
            <text x="36" y="36" fill="#fce000" stroke="#000000" stroke-width="1" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700">7D COMMITS</text>
        </g>

        <!-- World / Level -->
        <text x="490" y="0" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">WORLD</text>
        <text x="500" y="18" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">1-1</text>

        <!-- Total 30D Commits -->
        <text x="680" y="0" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">COMMITS</text>
        <text x="704" y="18" fill="#ffffff" stroke="#000000" stroke-width="1.5" font-family="{FONT_PIXEL}" font-size="12" font-weight="700">{commits_30d}</text>
    </g>

    <!-- Sub-status banner: Player badge -->
    <g transform="translate(40, 78)">
        <rect width="780" height="24" rx="4" fill="#000000" fill-opacity="0.65" stroke="#ffffff" stroke-width="1"/>
        <circle cx="16" cy="12" r="4" fill="#00e800">
            <animate attributeName="opacity" values="1; 0.4; 1" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <text x="28" y="16" fill="#fce000" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700">
            PLAYER: @{GITHUB_USERNAME}
        </text>
        <text x="240" y="16" fill="#ffffff" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700">
            LEVEL: MASTER COMMIT COLLECTOR
        </text>
        <text x="765" y="16" fill="#fce000" font-family="{FONT_PIXEL}" font-size="7.5" font-weight="700" text-anchor="end">
            1-UP ACTIVE ★
        </text>
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%" shape-rendering="crispEdges">
    <defs>
        <!-- Classic NES Mario 1985 Sky Blue -->
        <linearGradient id="nes-sky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#6b8cff"/>
            <stop offset="100%" stop-color="#5c94fc"/>
        </linearGradient>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;display=swap');
            text {{
                user-select: none;
            }}
        </style>
    </defs>

    <!-- Classic Mario NES Sky Blue Background -->
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#nes-sky)" rx="10"/>

    <!-- Puffy Pixel Clouds -->
    <g id="sky-clouds">
        {"".join(clouds_svg)}
    </g>

    <!-- Green Rolling Hills & Bushes -->
    <g id="hills">
        {"".join(hills_svg)}
        {bushes_svg}
    </g>

    <!-- Classic Ground Blocks with Grass Cap -->
    <g id="ground">
        {"".join(ground_blocks)}
    </g>

    <!-- Green Warp Pipe with Piranha Plant -->
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

    print(f"[✓] Bright Mario Commits SVG generated at: {output_path}")


if __name__ == "__main__":
    main()
