#!/usr/bin/env python3
"""
Generate a Super Mario Contribution Graph Game SVG for GitHub Profile.
Pure Python standard library implementation.
Draws the real 52-week GitHub contribution grid with animated Mario,
Goomba, Warp Pipe, and Question Blocks (Light/Clean Retro Theme).
"""

import os
import json
import datetime
import urllib.request
import urllib.error

# --- CONFIGURATION ---
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "quoczai22")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

WIDTH = 840
HEIGHT = 200

START_X = 52
START_Y = 56
CELL_SIZE = 11
GAP = 3
STEP = CELL_SIZE + GAP  # 14px

FONT_PIXEL = "'Press Start 2P', ui-monospace, 'Courier New', monospace"
FONT_TEXT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# GitHub Contribution Level Colors (Light Mode)
COLOR_EMPTY = "#ebedf0"
COLOR_L1 = "#9be9a8"
COLOR_L2 = "#40c463"
COLOR_L3 = "#30a14e"
COLOR_L4 = "#216e39"


def fetch_github_calendar(username, token):
    """Fetch user's 52-week contribution calendar via GitHub GraphQL API."""
    query = """
    query ($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
                weekday
              }
            }
          }
        }
      }
    }
    """

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8"),
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": "Mario-Commits-Grid-Generator"
        }
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        result = json.loads(response.read().decode("utf-8"))
        if "errors" in result:
            raise RuntimeError(f"GraphQL Errors: {result['errors']}")
        return result["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def get_calendar_data():
    """Retrieve live calendar data or fallback to realistic mock data."""
    if GITHUB_TOKEN:
        try:
            print(f"[*] Fetching 52-week contribution calendar for user: {GITHUB_USERNAME}...")
            cal = fetch_github_calendar(GITHUB_USERNAME, GITHUB_TOKEN)
            total = cal["totalContributions"]
            weeks = cal["weeks"]
            print(f"[✓] Successfully fetched {len(weeks)} weeks with {total} total contributions.")
            return {
                "total_contributions": total,
                "weeks": weeks,
                "is_fallback": False
            }
        except Exception as e:
            print(f"[!] API fetch failed ({e}). Switching to Fallback calendar...")

    # Realistic Fallback Generator (53 weeks x 7 days)
    weeks = []
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=52 * 7 + today.weekday() + 1)
    cur_date = start_date

    total_commits = 0
    for w in range(53):
        days = []
        for d in range(7):
            count = 0
            if (w * 7 + d) % 3 == 0:
                count = (w + d) % 8
            elif (w * 7 + d) % 5 == 0:
                count = (w * d) % 15
            total_commits += count

            if count == 0:
                color = COLOR_EMPTY
            elif count <= 3:
                color = COLOR_L1
            elif count <= 9:
                color = COLOR_L2
            elif count <= 19:
                color = COLOR_L3
            else:
                color = COLOR_L4

            days.append({
                "date": cur_date.isoformat(),
                "contributionCount": count,
                "color": color,
                "weekday": d
            })
            cur_date += datetime.timedelta(days=1)
        weeks.append({"contributionDays": days})

    return {
        "total_contributions": total_commits,
        "weeks": weeks,
        "is_fallback": True
    }


def parse_pixel_grid(matrix, color_map, pixel_size=1.5):
    """Converts an ASCII matrix into crisp SVG rect pixels."""
    svg_rects = []
    for r, row in enumerate(matrix):
        for c, ch in enumerate(row):
            if ch in color_map:
                x = c * pixel_size
                y = r * pixel_size
                svg_rects.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{pixel_size}" height="{pixel_size}" fill="{color_map[ch]}"/>'
                )
    return "".join(svg_rects)


def build_sprites(scale=1.4):
    """Builds mini 8-bit Mario, Goomba, Coin, and Pipe sprites."""
    mario_colors = {
        'R': '#e52521',  # Red cap/shirt
        'B': '#6b2f0a',  # Brown hair/shoes
        'S': '#fcd8a8',  # Skin
        'U': '#0058f8',  # Blue overalls
        'Y': '#facc15',  # Yellow buttons
    }

    mario_run1 = [
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

    mario_jump = [
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
        "..............."
    ]

    goomba_colors = {
        'B': '#7c2d12',
        'T': '#b45309',
        'W': '#ffffff',
        'K': '#000000',
        'F': '#1c1917',
    }

    goomba_matrix = [
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
        "mario_run": parse_pixel_grid(mario_run1, mario_colors, scale),
        "mario_jump": parse_pixel_grid(mario_jump, mario_colors, scale),
        "goomba": parse_pixel_grid(goomba_matrix, goomba_colors, scale),
        "coin": parse_pixel_grid(coin_matrix, coin_colors, scale),
    }


def build_contribution_svg(data):
    total = data["total_contributions"]
    weeks = data["weeks"]

    # Calculate 7-day commits
    recent_7d = 0
    all_days = []
    for w in weeks:
        for d in w["contributionDays"]:
            all_days.append(d)
    if len(all_days) >= 7:
        recent_7d = sum(d["contributionCount"] for d in all_days[-7:])

    sprites = build_sprites(scale=1.4)

    # 1. Month Labels across the top
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_labels = []
    last_month = None

    for w_idx, week in enumerate(weeks):
        if not week["contributionDays"]:
            continue
        first_date = week["contributionDays"][0]["date"]
        month_num = int(first_date.split("-")[1])
        if month_num != last_month:
            x_pos = START_X + w_idx * STEP
            # Don't place too close to previous
            if not month_labels or (x_pos - month_labels[-1][0] >= 38):
                month_labels.append((x_pos, month_names[month_num]))
                last_month = month_num

    month_svg = []
    for mx, mname in month_labels:
        month_svg.append(
            f'<text x="{mx}" y="44" fill="#57606a" font-family="{FONT_TEXT}" font-size="10" font-weight="500">{mname}</text>'
        )

    # 2. Day of Week Labels on left (Mon, Wed, Fri)
    day_labels_svg = [
        f'<text x="26" y="{START_Y + 1 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Mon</text>',
        f'<text x="26" y="{START_Y + 3 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Wed</text>',
        f'<text x="26" y="{START_Y + 5 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Fri</text>',
    ]

    # 3. 53-Week Grid Cells
    cells_svg = []
    for w_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            d_idx = day["weekday"]
            cx = START_X + w_idx * STEP
            cy = START_Y + d_idx * STEP
            cnt = day["contributionCount"]

            # Map count to authentic GitHub light colors
            if cnt == 0:
                color = COLOR_EMPTY
            elif cnt <= 3:
                color = COLOR_L1
            elif cnt <= 9:
                color = COLOR_L2
            elif cnt <= 19:
                color = COLOR_L3
            else:
                color = COLOR_L4

            cells_svg.append(
                f'<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{color}"/>'
            )

    # 4. Green Warp Pipe at the right end of the grid (Week 53, x = 794)
    pipe_x = START_X + len(weeks) * STEP + 4
    pipe_y = START_Y + 2 * STEP
    pipe_w = 26
    pipe_h = HEIGHT - pipe_y - 28

    pipe_svg = f"""
    <g id="warp-pipe" transform="translate({pipe_x}, {pipe_y})">
        <!-- Pipe Rim Top -->
        <rect x="-3" y="0" width="{pipe_w + 6}" height="14" fill="#00a800" stroke="#000000" stroke-width="1.2"/>
        <rect x="0" y="2" width="{pipe_w}" height="10" fill="#00e800"/>
        <line x1="4" y1="2" x2="4" y2="12" stroke="#ffffff" stroke-width="1.8"/>
        <line x1="{pipe_w - 5}" y1="2" x2="{pipe_w - 5}" y2="12" stroke="#007000" stroke-width="2.5"/>
        <!-- Pipe Stem -->
        <rect x="0" y="14" width="{pipe_w}" height="{pipe_h}" fill="#00a800" stroke="#000000" stroke-width="1.2"/>
        <rect x="2" y="14" width="{pipe_w - 4}" height="{pipe_h}" fill="#00e800"/>
        <line x1="6" y1="14" x2="6" y2="{pipe_h + 14}" stroke="#ffffff" stroke-width="1.8"/>
        <line x1="{pipe_w - 6}" y1="14" x2="{pipe_w - 6}" y2="{pipe_h + 14}" stroke="#007000" stroke-width="2.5"/>
    </g>
    """

    # 5. Question Blocks [?] placed over high-commit weeks
    q_blocks_svg = []
    q_block_weeks = [14, 28, 42]
    for qw in q_block_weeks:
        bx = START_X + qw * STEP - 3
        by = START_Y - 20
        q_blocks_svg.append(f"""
        <g transform="translate({bx}, {by})">
            <rect width="18" height="18" rx="2" fill="#fc9838" stroke="#000000" stroke-width="1"/>
            <rect x="2" y="2" width="14" height="14" fill="#fce000"/>
            <!-- Pixel ? -->
            <rect x="7" y="4" width="5" height="2" fill="#884400"/>
            <rect x="10" y="6" width="2" height="3" fill="#884400"/>
            <rect x="8" y="9" width="3" height="2" fill="#884400"/>
            <rect x="8" y="13" width="2" height="2" fill="#884400"/>
        </g>
        """)

    # 6. Animated Mario navigating the Contribution Grid
    # Mario runs along the grid, jumping from column to column, and lands into the Warp Pipe!
    m_start_x = START_X - 10
    m_end_x = pipe_x + 3
    base_mario_y = START_Y + 5 * STEP - 10

    # Path coordinates for Mario's journey across the 52 weeks
    mario_journey_values = (
        f"{m_start_x},{base_mario_y}; "
        f"{START_X + 14 * STEP},{base_mario_y - 30}; "
        f"{START_X + 18 * STEP},{base_mario_y}; "
        f"{START_X + 28 * STEP},{base_mario_y - 32}; "
        f"{START_X + 32 * STEP},{base_mario_y}; "
        f"{START_X + 42 * STEP},{base_mario_y - 35}; "
        f"{START_X + 46 * STEP},{base_mario_y}; "
        f"{m_end_x},{pipe_y - 24}; "
        f"{m_end_x},{pipe_y + 4}"
    )

    mario_anim_svg = f"""
    <g id="grid-mario">
        <!-- Movement across the 52-week contribution field -->
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{mario_journey_values}"
            keyTimes="0; 0.22; 0.32; 0.48; 0.58; 0.72; 0.82; 0.94; 1"
            dur="9s"
            repeatCount="indefinite"
        />
        <!-- Mario Sprite Animation -->
        <g id="mario-sprites">
            <g id="mario-run">
                <animate attributeName="display" values="inline; none; inline; none; inline" keyTimes="0; 0.20; 0.35; 0.70; 0.85" dur="9s" repeatCount="indefinite"/>
                {sprites['mario_run']}
            </g>
            <g id="mario-jump" display="none">
                <animate attributeName="display" values="none; inline; none; inline; none" keyTimes="0; 0.20; 0.35; 0.70; 0.85" dur="9s" repeatCount="indefinite"/>
                {sprites['mario_jump']}
            </g>
        </g>
    </g>
    """

    # 7. Animated Goomba patrolling along a row of the grid
    g_x1 = START_X + 22 * STEP
    g_x2 = START_X + 36 * STEP
    goomba_y = START_Y + 6 * STEP - 8

    goomba_anim_svg = f"""
    <g id="grid-goomba">
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{g_x1},{goomba_y}; {g_x2},{goomba_y}; {g_x1},{goomba_y}"
            keyTimes="0; 0.5; 1"
            dur="6s"
            repeatCount="indefinite"
        />
        {sprites['goomba']}
    </g>
    """

    # 8. Spawning Gold Coins over Question Blocks
    popping_coins_svg = []
    for qw in q_block_weeks:
        cx = START_X + qw * STEP
        cy = START_Y - 24
        popping_coins_svg.append(f"""
        <g transform="translate({cx}, {cy})">
            <animateTransform
                attributeName="transform"
                type="translate"
                values="{cx},{cy}; {cx},{cy - 20}; {cx},{cy}"
                dur="1.8s"
                repeatCount="indefinite"
            />
            {sprites['coin']}
        </g>
        """)

    # 9. Classic Super Mario Arcade HUD Header (Top Bar)
    score = total * 100
    score_str = f"{score:06d}"

    hud_svg = f"""
    <g id="retro-hud" transform="translate(50, 22)">
        <!-- MARIO & SCORE -->
        <text x="0" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">MARIO</text>
        <text x="0" y="13" fill="#e52521" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">{score_str}</text>

        <!-- COINS (7D COMMITS) -->
        <g transform="translate(190, -8)">
            {sprites['coin']}
            <text x="24" y="17" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">x{recent_7d:02d}</text>
            <text x="56" y="17" fill="#b45309" font-family="{FONT_PIXEL}" font-size="6.5" font-weight="700">7D COINS</text>
        </g>

        <!-- WORLD 1-1 -->
        <text x="430" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">WORLD</text>
        <text x="442" y="13" fill="#00a800" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">1-1</text>

        <!-- TOTAL YEAR CONTRIBUTIONS -->
        <text x="610" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">CONTRIBUTIONS</text>
        <text x="670" y="13" fill="#0058f8" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">{total:,}</text>
    </g>
    """

    # Legend at bottom right
    legend_x = 680
    legend_y = HEIGHT - 18
    legend_svg = f"""
    <g id="grid-legend" transform="translate({legend_x}, {legend_y})">
        <text x="-32" y="9" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Less</text>
        <rect x="0" y="0" width="10" height="10" rx="2" fill="{COLOR_EMPTY}"/>
        <rect x="14" y="0" width="10" height="10" rx="2" fill="{COLOR_L1}"/>
        <rect x="28" y="0" width="10" height="10" rx="2" fill="{COLOR_L2}"/>
        <rect x="42" y="0" width="10" height="10" rx="2" fill="{COLOR_L3}"/>
        <rect x="56" y="0" width="10" height="10" rx="2" fill="{COLOR_L4}"/>
        <text x="72" y="9" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">More</text>
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%" shape-rendering="crispEdges">
    <defs>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;display=swap');
            text {{
                user-select: none;
            }}
        </style>
    </defs>

    <!-- Clean Light Background with soft border -->
    <rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff" stroke="#d0d7de" stroke-width="1" rx="8"/>

    <!-- Super Mario Arcade HUD -->
    {hud_svg}

    <!-- Month Labels -->
    <g id="month-labels">
        {"".join(month_svg)}
    </g>

    <!-- Day of Week Labels -->
    <g id="day-labels">
        {"".join(day_labels_svg)}
    </g>

    <!-- 52-Week Contribution Grid -->
    <g id="contribution-cells">
        {"".join(cells_svg)}
    </g>

    <!-- Green Warp Pipe -->
    {pipe_svg}

    <!-- Question Blocks [?] -->
    <g id="q-blocks">
        {"".join(q_blocks_svg)}
    </g>

    <!-- Popping Gold Coins -->
    <g id="popping-coins">
        {"".join(popping_coins_svg)}
    </g>

    <!-- Walking Goomba on Grid -->
    {goomba_anim_svg}

    <!-- Animated Mario Running & Jumping Across Grid -->
    {mario_anim_svg}

    <!-- Contribution Level Legend -->
    {legend_svg}
</svg>"""
    return svg_content


def main():
    os.makedirs("dist", exist_ok=True)
    data = get_calendar_data()
    svg_code = build_contribution_svg(data)

    output_path = os.path.join("dist", "mario-commits.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_code)

    print(f"[✓] Mario Contribution Grid SVG generated at: {output_path}")


if __name__ == "__main__":
    main()
