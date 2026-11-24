#!/usr/bin/env python3
"""
Generate a Super Mario Contribution Graph Game SVG for GitHub Profile.
Mario literally runs across the 52-week contribution grid, EATING the green
commit blocks (turning them from green to eaten), chasing & eating Super Mushrooms,
and popping coins into the Green Warp Pipe! (Light / Clean Retro Theme).
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

TOTAL_DUR = 12.0  # Total animation loop duration in seconds


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


def parse_pixel_grid(matrix, color_map, pixel_size=1.4):
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


def build_sprites():
    """Builds mini 8-bit Mario, Super Mushroom, and Coin sprites."""
    mario_colors = {
        'R': '#e52521',  # Red cap/shirt
        'B': '#6b2f0a',  # Brown hair/shoes
        'S': '#fcd8a8',  # Skin
        'U': '#0058f8',  # Blue overalls
        'Y': '#facc15',  # Yellow buttons
    }

    mario_run = [
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

    mario_eat_jump = [
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

    # Authentic 8-bit Super Mushroom
    shroom_colors = {
        'R': '#e52521',  # Red cap
        'W': '#ffffff',  # White spots
        'S': '#fcd8a8',  # Tan face
        'K': '#000000',  # Black eyes/outline
    }

    shroom_matrix = [
        ".....RRRRRR.....",
        "...RRRRRRRRRR...",
        "..RRWWRRRRWWRR..",
        ".RRWWWRRRRWWWRR.",
        ".RRWWWRRRRWWWRR.",
        "RRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRR",
        "....SSSSSSSS....",
        "...SSKSSSSKSS...",
        "...SSKSSSSKSS...",
        "...SSSSSSSSSS...",
        "....SSSSSSSS...."
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
        "mario_run": parse_pixel_grid(mario_run, mario_colors, pixel_size=1.4),
        "mario_eat": parse_pixel_grid(mario_eat_jump, mario_colors, pixel_size=1.4),
        "mushroom": parse_pixel_grid(shroom_matrix, shroom_colors, pixel_size=1.3),
        "coin": parse_pixel_grid(coin_matrix, coin_colors, pixel_size=1.2),
    }


def build_contribution_svg(data):
    total = data["total_contributions"]
    weeks = data["weeks"]

    # Calculate 7-day commits
    all_days = []
    for w in weeks:
        for d in w["contributionDays"]:
            all_days.append(d)
    recent_7d = sum(d["contributionCount"] for d in all_days[-7:]) if len(all_days) >= 7 else 0

    sprites = build_sprites()

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
            if not month_labels or (x_pos - month_labels[-1][0] >= 38):
                month_labels.append((x_pos, month_names[month_num]))
                last_month = month_num

    month_svg = [
        f'<text x="{mx}" y="44" fill="#57606a" font-family="{FONT_TEXT}" font-size="10" font-weight="500">{mname}</text>'
        for mx, mname in month_labels
    ]

    # 2. Day of Week Labels on left (Mon, Wed, Fri)
    day_labels_svg = [
        f'<text x="26" y="{START_Y + 1 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Mon</text>',
        f'<text x="26" y="{START_Y + 3 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Wed</text>',
        f'<text x="26" y="{START_Y + 5 * STEP + 9}" fill="#57606a" font-family="{FONT_TEXT}" font-size="9">Fri</text>',
    ]

    # 3. 53-Week Grid Cells WITH DYNAMIC EATING ANIMATION
    # Mario runs from Week 0 to Week 53 between time fraction 0.05 and 0.88
    # When Mario visits Week w, every green commit cell in that column gets EATEN!
    # It flashes white and turns into #ebedf0 (eaten empty), then resets at loop end!
    cells_svg = []
    num_weeks = len(weeks)

    for w_idx, week in enumerate(weeks):
        # Time fraction when Mario traverses column w_idx
        t_arrive = round(0.06 + (w_idx / (num_weeks + 2)) * 0.80, 3)
        t_eaten = round(t_arrive + 0.015, 3)
        t_reset = 0.96

        for day in week["contributionDays"]:
            d_idx = day["weekday"]
            cx = START_X + w_idx * STEP
            cy = START_Y + d_idx * STEP
            cnt = day["contributionCount"]

            if cnt == 0:
                # Empty cell stays empty
                cells_svg.append(
                    f'<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{COLOR_EMPTY}"/>'
                )
            else:
                # Green commit cell
                if cnt <= 3:
                    orig_color = COLOR_L1
                elif cnt <= 9:
                    orig_color = COLOR_L2
                elif cnt <= 19:
                    orig_color = COLOR_L3
                else:
                    orig_color = COLOR_L4

                # Mario EATS this cell: green -> flash white -> consumed #ebedf0 -> resets at end
                cell_anim = f"""
                <rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{orig_color}">
                    <animate attributeName="fill"
                             values="{orig_color}; {orig_color}; #ffffff; {COLOR_EMPTY}; {COLOR_EMPTY}; {orig_color}"
                             keyTimes="0; {t_arrive}; {t_arrive + 0.005:.3f}; {t_eaten}; {t_reset}; 1"
                             dur="{TOTAL_DUR}s"
                             repeatCount="indefinite" />
                </rect>
                """
                cells_svg.append(cell_anim)

    # 4. Green Warp Pipe at the right end (Week 53, x = 794)
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

    # 5. SUPER MUSHROOM SPAWNS FROM COMMITS & BOUNCES FORWARD
    # Mushroom spawns at Week 8 (t = 2.0s), bounces across the tops of commit blocks,
    # and Mario chases it until catching and eating it at Week 28 (t = 5.2s)!
    shroom_start_x = START_X + 8 * STEP
    shroom_catch_x = START_X + 28 * STEP
    shroom_y = START_Y - 14

    shroom_anim_svg = f"""
    <g id="commit-mushroom">
        <!-- Mushroom bounces across commit blocks ahead of Mario -->
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{shroom_start_x},{shroom_y}; {shroom_start_x + 80},{shroom_y - 12}; {shroom_start_x + 160},{shroom_y}; {shroom_catch_x},{shroom_y}; {shroom_catch_x},{shroom_y}"
            keyTimes="0; 0.20; 0.35; 0.44; 1"
            dur="{TOTAL_DUR}s"
            repeatCount="indefinite"
        />
        <!-- Mushroom disappears when Mario catches & eats it at t = 0.44! -->
        <g>
            <animate attributeName="opacity" values="0; 1; 1; 0; 0" keyTimes="0; 0.12; 0.43; 0.45; 1" dur="{TOTAL_DUR}s" repeatCount="indefinite"/>
            {sprites['mushroom']}
            <!-- 1-UP Floating text when eaten -->
            <text x="10" y="-8" fill="#00a800" font-family="{FONT_PIXEL}" font-size="7" font-weight="700">1-UP!</text>
        </g>
    </g>
    """

    # 6. ANIMATED MARIO EATING COMMITS ACROSS THE 52 WEEKS
    # Mario runs from left to right, jumping up and down across the rows of commit blocks,
    # chomping the green blocks, eating the mushroom, and diving into the pipe at the end!
    m_start_x = START_X - 18
    m_end_x = pipe_x + 2
    row_top_y = START_Y + 1 * STEP - 14
    row_mid_y = START_Y + 3 * STEP - 14
    row_bot_y = START_Y + 5 * STEP - 14

    # Mario's chomping trajectory visiting rows of commits
    mario_journey = (
        f"{m_start_x},{row_bot_y}; "
        f"{START_X + 10 * STEP},{row_mid_y}; "
        f"{START_X + 20 * STEP},{row_top_y}; "
        f"{shroom_catch_x},{shroom_y + 2}; "      # Catches mushroom at Week 28!
        f"{START_X + 36 * STEP},{row_mid_y}; "
        f"{START_X + 44 * STEP},{row_bot_y}; "
        f"{START_X + 50 * STEP},{row_mid_y}; "
        f"{m_end_x},{pipe_y - 24}; "             # Jumps onto pipe rim
        f"{m_end_x},{pipe_y + 6}; "              # Dives down into pipe!
        f"{m_end_x},{pipe_y + 6}"
    )

    mario_anim_svg = f"""
    <g id="commit-eating-mario">
        <!-- Mario traversing and eating the 52-week contribution blocks -->
        <animateTransform
            attributeName="transform"
            type="translate"
            values="{mario_journey}"
            keyTimes="0; 0.16; 0.32; 0.44; 0.58; 0.70; 0.80; 0.90; 0.95; 1"
            dur="{TOTAL_DUR}s"
            repeatCount="indefinite"
        />
        <!-- Mario Sprite: Toggling between running & jumping/chomping -->
        <g id="mario-sprites">
            <g id="mario-run">
                <animate attributeName="display" values="inline; none; inline; none; inline; none" keyTimes="0; 0.16; 0.40; 0.45; 0.75; 0.90" dur="{TOTAL_DUR}s" repeatCount="indefinite"/>
                {sprites['mario_run']}
            </g>
            <g id="mario-eat" display="none">
                <animate attributeName="display" values="none; inline; none; inline; none; inline" keyTimes="0; 0.16; 0.40; 0.45; 0.75; 0.90" dur="{TOTAL_DUR}s" repeatCount="indefinite"/>
                {sprites['mario_eat']}
            </g>
        </g>
    </g>
    """

    # 7. Popping Coins when high commit clusters get eaten
    popping_coins_svg = []
    coin_spots = [12, 24, 38, 48]
    for cs in coin_spots:
        cx = START_X + cs * STEP
        cy = START_Y + 2 * STEP
        t_pop = round(0.06 + (cs / (num_weeks + 2)) * 0.80, 2)
        popping_coins_svg.append(f"""
        <g transform="translate({cx}, {cy})">
            <animateTransform
                attributeName="transform"
                type="translate"
                values="{cx},{cy}; {cx},{cy - 22}; {cx},{cy - 12}"
                keyTimes="0; 0.5; 1"
                begin="{t_pop * TOTAL_DUR:.1f}s"
                dur="0.8s"
                repeatCount="indefinite"
            />
            <g opacity="0">
                <animate attributeName="opacity" values="0; 1; 0" keyTimes="0; 0.2; 1" begin="{t_pop * TOTAL_DUR:.1f}s" dur="0.8s" repeatCount="indefinite"/>
                {sprites['coin']}
                <text x="14" y="-4" fill="#b45309" font-family="{FONT_PIXEL}" font-size="7" font-weight="700">+100</text>
            </g>
        </g>
        """)

    # 8. Classic Super Mario Arcade HUD Header (Top Bar)
    score = total * 100
    score_str = f"{score:06d}"

    hud_svg = f"""
    <g id="retro-hud" transform="translate(50, 22)">
        <!-- MARIO & LIVE SCORE -->
        <text x="0" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">MARIO</text>
        <text x="0" y="13" fill="#e52521" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">{score_str}</text>

        <!-- COINS COLLECTED (7D COMMITS) -->
        <g transform="translate(190, -8)">
            {sprites['coin']}
            <text x="24" y="17" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">x{recent_7d:02d}</text>
            <text x="56" y="17" fill="#b45309" font-family="{FONT_PIXEL}" font-size="6.5" font-weight="700">7D COINS</text>
        </g>

        <!-- WORLD 1-1 -->
        <text x="430" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">WORLD</text>
        <text x="442" y="13" fill="#00a800" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">1-1</text>

        <!-- TOTAL 52-WEEK CONTRIBUTIONS EATEN -->
        <text x="580" y="0" fill="#000000" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">COMMITS EATEN</text>
        <text x="640" y="13" fill="#0058f8" font-family="{FONT_PIXEL}" font-size="9" font-weight="700">{total:,} PTS</text>
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

    <!-- Clean Light Canvas with soft border -->
    <rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff" stroke="#d0d7de" stroke-width="1" rx="8"/>

    <!-- Super Mario Arcade HUD Header -->
    {hud_svg}

    <!-- Month Labels -->
    <g id="month-labels">
        {"".join(month_svg)}
    </g>

    <!-- Day of Week Labels -->
    <g id="day-labels">
        {"".join(day_labels_svg)}
    </g>

    <!-- 52-Week Contribution Grid (Animated Commit Eating Effect) -->
    <g id="contribution-cells">
        {"".join(cells_svg)}
    </g>

    <!-- Green Warp Pipe -->
    {pipe_svg}

    <!-- Super Mushroom (Bouncing & Eaten by Mario) -->
    {shroom_anim_svg}

    <!-- Popping Score Coins -->
    <g id="popping-coins">
        {"".join(popping_coins_svg)}
    </g>

    <!-- Mario Running, Chomping Commits & Eating Mushroom -->
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

    print(f"[✓] Mario Commit-Eating Grid SVG generated at: {output_path}")


if __name__ == "__main__":
    main()
