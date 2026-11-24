import os
import json
import urllib.request
from collections import deque

def fetch_contributions(username, token=None):
    query = """query($userName: String!) {
  user(login: $userName) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionLevel
            date
          }
        }
      }
    }
  }
}"""
    req_data = json.dumps({'query': query, 'variables': {'userName': username}}).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'User-Agent': 'MarioSnk/1.0'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        req = urllib.request.Request('https://api.github.com/graphql', data=req_data, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'data' in data and data['data']['user']:
                return data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    except Exception as e:
        print(f"GraphQL API error: {e}")

    # Fallback to public events/mock grid if no token or rate-limited
    print("Using default grid size fallback")
    return [[{'contributionLevel': 'NONE'} for _ in range(7)] for _ in range(53)]

def solve_mario_path(grid, width, height):
    """
    Greedy BFS nearest neighbor solver with smooth grid pathfinding:
    Mario visits every active commit dot, eating them one by one, then loops cleanly back.
    """
    targets = set()
    for x in range(width):
        for y in range(height):
            if grid[x][y] > 0:
                targets.add((x, y))
    
    current = (0, 0)
    full_path = [current]
    eaten_order = [] # [(x, y, step_index)]
    
    def bfs_shortest_path(start, goals):
        if not goals:
            return None, None
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node in goals:
                return path, node
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = node[0] + dx, node[1] + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
        return None, None

    remaining = set(targets)
    while remaining:
        path, found = bfs_shortest_path(current, remaining)
        if not path:
            break
        for step in path[1:]:
            full_path.append(step)
            current = step
            if current in remaining:
                remaining.remove(current)
                eaten_order.append((current[0], current[1], len(full_path) - 1))

    # Return back to origin (0,0) smoothly
    return_path, _ = bfs_shortest_path(current, {(0, 0)})
    if return_path:
        for step in return_path[1:]:
            full_path.append(step)

    return full_path, eaten_order

def generate_svg(weeks_data, output_file="mario_snake.svg"):
    width = len(weeks_data)
    height = 7
    
    level_map = {
        'NONE': 0,
        'FIRST_QUARTILE': 1,
        'SECOND_QUARTILE': 2,
        'THIRD_QUARTILE': 3,
        'FOURTH_QUARTILE': 4
    }
    
    grid = [[0 for _ in range(height)] for _ in range(width)]
    for w_idx, week in enumerate(weeks_data):
        for d_idx, day in enumerate(week.get('contributionDays', [])):
            if d_idx < height:
                grid[w_idx][d_idx] = level_map.get(day.get('contributionLevel', 'NONE'), 0)

    # Solve path
    path, eaten_order = solve_mario_path(grid, width, height)
    total_steps = max(len(path), 1)

    # Timing: ~90ms per step, minimum 15s, maximum 45s
    step_duration_ms = 100
    total_duration_s = max(18.0, (total_steps * step_duration_ms) / 1000.0)

    # Platane/snk sizing constants
    size_cell = 16
    size_dot = 12
    size_dot_border_radius = 2
    offset_dot = (size_cell - size_dot) / 2 # 2px

    svg_width = (width + 2) * size_cell
    svg_height = (height + 5) * size_cell
    view_box = f"{-size_cell} {-size_cell * 2} {svg_width} {svg_height}"

    # Palette definitions (Light mode default + Dark mode support)
    # Match GitHub Contribution grid exactly
    colors_light = {
        'cb': '#1b1f230a',
        'ce': '#ebedf0',
        'c1': '#9be9a8',
        'c2': '#40c463',
        'c3': '#30a14e',
        'c4': '#216e39'
    }
    colors_dark = {
        'cb': '#1b1f230a',
        'ce': '#161b22',
        'c1': '#0e4429',
        'c2': '#006d32',
        'c3': '#26a641',
        'c4': '#39d353'
    }

    # Track eaten times
    eaten_dict = {}
    for x, y, step_idx in eaten_order:
        eaten_dict[(x, y)] = step_idx / total_steps

    css_rules = []
    
    # CSS root variables
    css_rules.append(f"""
    :root {{
      --cb: {colors_light['cb']};
      --ce: {colors_light['ce']};
      --c1: {colors_light['c1']};
      --c2: {colors_light['c2']};
      --c3: {colors_light['c3']};
      --c4: {colors_light['c4']};
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --cb: {colors_dark['cb']};
        --ce: {colors_dark['ce']};
        --c1: {colors_dark['c1']};
        --c2: {colors_dark['c2']};
        --c3: {colors_dark['c3']};
        --c4: {colors_dark['c4']};
      }}
    }}
    .c {{
      shape-rendering: geometricPrecision;
      fill: var(--ce);
      stroke-width: 1px;
      stroke: var(--cb);
      width: {size_dot}px;
      height: {size_dot}px;
      rx: {size_dot_border_radius}px;
      ry: {size_dot_border_radius}px;
      animation: none {total_duration_s:.2f}s linear infinite;
    }}
    .mario-sprite {{
      animation: marioMove {total_duration_s:.2f}s linear infinite;
    }}
    .u {{
      transform-origin: 0 0;
      animation: none linear {total_duration_s:.2f}s infinite;
    }}
    """)

    # Grid Rects and animations
    grid_rects = []
    cell_idx = 0
    for x in range(width):
        for y in range(height):
            lvl = grid[x][y]
            px = x * size_cell + offset_dot
            py = y * size_cell + offset_dot
            
            if (x, y) in eaten_dict and lvl > 0:
                t = eaten_dict[(x, y)]
                cid = f"c{cell_idx}"
                cell_idx += 1
                
                t_before = max(0.0, t - 0.0005)
                t_after = min(1.0, t + 0.0005)

                css_rules.append(f"""
    @keyframes kf_{cid} {{
      0% {{ fill: var(--c{lvl}); }}
      {t_before*100:.2f}% {{ fill: var(--c{lvl}); }}
      {t_after*100:.2f}% {{ fill: var(--ce); }}
      100% {{ fill: var(--ce); }}
    }}
    .{cid} {{
      fill: var(--c{lvl});
      animation-name: kf_{cid};
    }}""")
                grid_rects.append(f'  <rect class="c {cid}" x="{px}" y="{py}" />')
            elif lvl > 0:
                grid_rects.append(f'  <rect class="c" x="{px}" y="{py}" style="fill: var(--c{lvl});" />')
            else:
                grid_rects.append(f'  <rect class="c" x="{px}" y="{py}" />')

    # Mario Keyframes
    # Mario is 16x16, centered over the 16x16 cell
    mario_keyframes = ["@keyframes marioMove {"]
    for i, (px, py) in enumerate(path):
        progress = (i / (total_steps - 1)) * 100 if total_steps > 1 else 0
        tx = px * size_cell
        ty = py * size_cell
        
        # Face direction check
        flip = ""
        if i < len(path) - 1:
            next_x = path[i+1][0]
            if next_x < px:
                flip = f" translate({tx + 16}px, {ty}px) scale(-1, 1)"
        mario_keyframes.append(f"  {progress:.2f}% {{ transform: translate({tx}px, {ty}px); }}")
    mario_keyframes.append("}")
    css_rules.append("\n".join(mario_keyframes))

    # Bottom Stack (Platane/snk style stack progress bar)
    stack_y = (height + 2) * size_cell
    stack_rects = []
    if eaten_order:
        bar_total_w = width * size_cell
        step_w = bar_total_w / len(eaten_order)
        for i, (ex, ey, s_idx) in enumerate(eaten_order):
            lvl = grid[ex][ey]
            t = s_idx / total_steps
            bx = i * step_w
            uid = f"u{i}"
            css_rules.append(f"""
    @keyframes kf_{uid} {{
      0% {{ opacity: 0; transform: scaleY(0); }}
      {max(0.0, t-0.001)*100:.2f}% {{ opacity: 0; transform: scaleY(0); }}
      {min(1.0, t+0.001)*100:.2f}% {{ opacity: 1; transform: scaleY(1); }}
      100% {{ opacity: 1; transform: scaleY(1); }}
    }}
    .{uid} {{
      fill: var(--c{lvl});
      transform-origin: {bx:.1f}px {stack_y + size_dot}px;
      animation-name: kf_{uid};
    }}""")
            stack_rects.append(f'  <rect class="u {uid}" x="{bx:.1f}" y="{stack_y}" width="{step_w + 0.5:.1f}" height="{size_dot}" rx="1" />')

    # Mario 8-Bit Sprite (16x16 pixel art scaled into 16px)
    # Mario palette: R: Red (#e52521), B: Brown (#8B4513), S: Skin (#ffcca6), U: Blue (#0026a8), Y: Yellow (#fbd000)
    # Super Mario Bros NES running/standing sprite
    mario_pixels = [
        "....RRRRR.......",
        "...RRRRRRRRR....",
        "...BBSBBBO......",
        "..BSBSSSBO......",
        "..BSBBSSSBO.....",
        "..BBSSSSBB......",
        "....SSSSSSS.....",
        "...RRURR........",
        "..RRRURRURRR....",
        "..RRUUUUURRR....",
        "..SSUYYUYUSS....",
        "..SSSSSSSSSS....",
        "..SS.UUUU.SS....",
        "....UUUUUU......",
        "...BBBB.BBBB....",
        "..BBBBB.BBBBB..."
    ]
    color_map = {
        'R': '#e52521',
        'B': '#6a3805',
        'S': '#fcd8a8',
        'U': '#0038a8',
        'Y': '#fbd000',
        'O': '#d87000'
    }
    sprite_elements = []
    scale = 1.0 # 16x16 fits cell_size (16px)
    for row_idx, row in enumerate(mario_pixels):
        for col_idx, ch in enumerate(row):
            if ch in color_map:
                sprite_elements.append(
                    f'      <rect x="{col_idx*scale:.1f}" y="{row_idx*scale:.1f}" width="{scale}" height="{scale}" fill="{color_map[ch]}" />'
                )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="{svg_width}" height="{svg_height}">
  <desc>Mario eating contribution graph - inspired by Platane/snk</desc>
  <style>
{''.join(css_rules)}
  </style>

  <!-- Contribution Grid -->
  <g id="grid">
{''.join(grid_rects)}
  </g>

  <!-- Stack progress bar at bottom -->
  <g id="stack">
{''.join(stack_rects)}
  </g>

  <!-- Mario Character Sprite -->
  <g class="mario-sprite">
{''.join(sprite_elements)}
  </g>
</svg>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {output_file} ({len(path)} steps, {len(eaten_order)} commits eaten, duration: {total_duration_s:.1f}s)")

if __name__ == '__main__':
    username = os.environ.get("GITHUB_ACTOR", "quoczai22")
    token = os.environ.get("GITHUB_TOKEN")
    weeks = fetch_contributions(username, token)
    generate_svg(weeks, "mario_snake.svg")
