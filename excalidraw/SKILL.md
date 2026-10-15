---
name: excalidraw
description: Excalidraw canvas toolkit for creating, editing, and refining diagrams on a live canvas. Use when an agent needs to (1) draw or lay out diagrams, (2) iteratively refine them by describing the scene and screenshotting its own work, (3) export/import .excalidraw files or PNG/SVG images, (4) save/restore canvas snapshots, (5) convert Mermaid to Excalidraw, or (6) perform element-level CRUD, alignment, distribution, grouping, duplication, and locking. Use the configured Excalidraw MCP server first when its tools are available. The bundled CLI (npx -y mcp-excalidraw-server <command>) is a fallback for tasks the MCP tools cannot handle; the REST API is a last resort.
---

# Excalidraw Skill

## Step 0: Pick an Interface

Three interfaces drive the same live canvas. Pick the first one that applies:

1. **MCP tools** — use the configured Excalidraw server tools for scene creation, editing, screenshots, file import/export, and rendering. Prefer MCP when available so results and screenshots stay in the conversation.
2. **CLI** (fallback when MCP tools are unavailable or lack a needed operation):
   ```bash
   npx -y mcp-excalidraw-server <command>
   ```
   No setup needed — any canvas-touching command **auto-starts the canvas server** on `http://127.0.0.1:3000` (first `npx` run downloads the package). If the CLI is installed globally (`npm i -g mcp-excalidraw-server`), the shorter alias `excalidraw-canvas <command>` works too.
3. **REST API** (last resort, e.g. from application code): HTTP endpoints on `http://127.0.0.1:3000` — see `references/cheatsheet.md` for payloads. The server must already be running.

The canvas URL comes from `EXPRESS_SERVER_URL` (default `http://127.0.0.1:3000`). Screenshots and image exports render headless inside the canvas server, so you never need a browser tab to check your own work. Mermaid conversion and viewport control need an open canvas tab. Still tell the user the URL — opening it lets them watch you draw.

### CLI Quick Reference

Results are JSON on stdout — except `describe` (plain text) and raw-content output when `--out` is omitted (`export` scene JSON, `screenshot --format svg`). Diagnostics on stderr. Exit codes: 0 ok, 1 error, 2 usage, 3 canvas unreachable, 4 browser tab required (only `mermaid` and `screenshot --renderer browser`).

| Task | Command |
|------|---------|
| Start / stop / inspect server | `start`, `stop`, `status` |
| Create elements (batch) | `add elements.json` or `echo '[...]' \| add` or `add --one '{...}'` |
| Multi-op patch in one call | `apply patch.json` — `{"create":[...],"update":[{"id":"a","set":{...}}],"delete":[...]}` |
| Read one / query many | `get <id>`, `query [--type t] [--bbox x0,y0,x1,y1] [--filter k=v] [--filter-json '{...}']` |
| Update / delete | `update <id> --set '{...}'`, `delete <id> [...]` |
| Understand the scene | `describe` (plain-text summary: ids, positions, labels, connections) |
| See the scene | `screenshot [--out f.png]` (PNG without `--out` → temp file path in JSON; SVG without `--out` → raw SVG) |
| Layout operations | `arrange align\|distribute\|group\|ungroup\|lock\|unlock\|duplicate --ids a,b,c [--to left\|horizontal\|...]` |
| Scene files | `export [--out scene.excalidraw]`, `import [scene.excalidraw|-] [--replace]` — a `.excalidraw.md` out path writes Obsidian's format (see File I/O) |
| Mermaid → canvas | `mermaid [diagram.mmd|-]` (or stdin) |
| Snapshots | `snapshot save\|list\|restore <name>` |
| Share link | `share` (encrypted upload → excalidraw.com URL) |
| Wipe canvas | `clear --yes` |
|
### Element Format (CLI and MCP)

The CLI and MCP tools accept the same agent-friendly format and normalize it automatically:

- **Labels**: put `"text": "My Label"` on any shape — converted to Excalidraw's bound-label format for you.
- **Arrow binding**: `"startElementId": "a"` / `"endElementId": "b"` — arrows auto-route to element edges.
- **fontFamily**: pass a string name (`"helvetica"`, `"cascadia"`, `"excalifont"`, ...) or string number `"1"`–`"8"`.
- **points**: both `[[x,y], ...]` tuples and `[{"x":..,"y":..}]` objects are accepted.
- **Patch updates**: in `apply`, update entries can use either direct fields (`{"id":"a","x":120}`) or a `set` object (`{"id":"a","set":{"x":120}}`). Do not mix both forms in one update entry.

**Raw REST is stricter**: labels must be `"label": {"text": "..."}`, bindings must be `"start": {"id": "..."}` / `"end": {"id": "..."}`. Only worry about this when POSTing to the API directly.

---

## Coordinate System

The canvas uses a 2D coordinate grid: **(0, 0) is the origin**, **x increases rightward**, **y increases downward**. Plan your layout before writing any JSON.

**General spacing guidelines:**
- Vertical spacing between tiers: 80–120px (enough that arrows don't crowd labels)
- Horizontal spacing between siblings: 40–60px minimum; give labeled arrows 120px+
- Shape width: `max(160, labelCharCount * 12)` to keep the label on one line
- Shape height: 60px single-line, 80px two-line labels
- Background/zone padding: 50px on all sides around contained elements

**Styling for a professional look:**
- `"fillStyle": "solid"` on shapes gives crisp flat fills — the default is a sketchy hachure pattern
- Pair pastel `backgroundColor` fills with their darker `strokeColor` (palette in the cheatsheet)
- `"strokeStyle": "dashed"` on zone borders and async arrows reads as "boundary / background"

---

## Layout Anti-Patterns (Critical for Complex Diagrams)

These are the most common mistakes that produce unreadable diagrams. Avoid all of them.

### 1. Do NOT use `label.text` (or `text`) on large background zone rectangles

When you put a label on a background rectangle, Excalidraw creates a bound text element centered in the middle of that shape — right where your service boxes will be placed. The text overlaps everything inside the zone and cannot be repositioned.

**Wrong:**
```json
{"id": "vpc-zone", "type": "rectangle", "x": 50, "y": 50, "width": 800, "height": 400, "text": "VPC (10.0.0.0/16)"}
```

**Right — use a free-standing text element anchored at the top of the zone:**
```json
{"id": "vpc-zone", "type": "rectangle", "x": 50, "y": 50, "width": 800, "height": 400, "backgroundColor": "#e3f2fd"},
{"id": "vpc-label", "type": "text", "x": 70, "y": 60, "width": 300, "height": 30, "text": "VPC (10.0.0.0/16)", "fontSize": 18}
```

The free-standing text element sits at the top corner of the zone and doesn't interfere with elements placed inside.

### 2. Avoid cross-zone arrows in complex diagrams

An arrow from an element in one layout zone to an element in a distant zone will draw a long diagonal line crossing through everything in between. In a multi-zone infra diagram this produces an unreadable tangle of spaghetti.

**Design rule:** Keep arrows within the same zone or tier. To show cross-zone relationships, use annotation text or separate the zones so their edges are adjacent (no elements between them), and route the arrow along the edge.

If you must connect across zones, use an elbowed arrow that travels along the perimeter — never through the middle of another zone.

### 3. Use arrow labels sparingly

Arrow labels are placed at the midpoint of the arrow. On short arrows, they overlap the shapes at both ends. On crowded diagrams, they collide with nearby elements.

- Only add an arrow label when the relationship name is genuinely essential (e.g., protocol, port number, data direction).
- If you're adding a label to every arrow, reconsider — it usually adds visual noise, not clarity.
- Keep arrow labels to ≤ 12 characters. Prefer omitting them entirely on dense diagrams.

---

## Quality: Why It Matters (and How to Check)

Excalidraw diagrams are visual communication. If text is cut off, elements overlap, or arrows cross through unrelated shapes, the diagram becomes confusing and unprofessional — it defeats the whole purpose of drawing it. So after every batch of elements, verify before adding more.

### Quality Checklist

After each `batch_create_elements` or `apply` operation, call `get_canvas_screenshot` and check:

1. **Text truncation** — Is all label text fully visible? Truncated text means the shape is too small. Increase `width` and/or `height`.
2. **Overlap** — Do any shapes share the same space? Background zones must fully contain children with padding.
3. **Arrow crossing** — Do arrows cut through unrelated elements? If yes, route them around using curved or elbowed arrows (see Arrow Routing below).
4. **Arrow-label overlap** — Arrow labels sit at the midpoint. If they overlap a shape, shorten the label or adjust the arrow path.
5. **Spacing** — At least 40px gap between elements. Cramped layouts are hard to read.
6. **Readability** — Font size ≥ 16 for body text, ≥ 20 for titles.
7. **Zone label placement** — If you used `text`/`label.text` on a background zone rectangle, the zone label will be centered in the middle of the zone, overlapping everything inside. Fix: delete the bound text element and add a free-standing text element at the top of the zone instead (see Layout Anti-Patterns above).

If you find any issue: **stop, fix it, re-screenshot, then continue.** Say "I see [issue], fixing it" rather than glossing over problems. Only proceed once all checks pass.

---

## Workflow: Drawing a New Diagram

### Mermaid vs. Direct Creation — Which to Use?

**Use `mermaid` / `create_from_mermaid`** when: the user already has a Mermaid diagram, or the structure maps cleanly to a flowchart/sequence/ER diagram with standard Mermaid syntax. It's fast and handles conversion automatically, though you get less control over exact layout.

**Create elements directly** when: you need precise layout control, the diagram type doesn't map to Mermaid well (e.g., custom architecture, annotated cloud diagrams), or you want elements positioned in a specific coordinate grid.

### Steps

1. Call `read_diagram_guide` for colors, sizing, and layout advice, then plan the coordinate grid.
2. Preserve the current canvas. Do not call `clear_canvas` unless the user explicitly asks to clear or replace the whole scene.
3. Create shapes and arrows together with `batch_create_elements`. Use stable custom IDs (such as `auth-svc`) so you can refine individual elements later. For example, send this array as the tool's `elements` argument:
   ```json
   [
     {"id": "lb", "type": "rectangle", "x": 300, "y": 50, "width": 180, "height": 60, "text": "Load Balancer"},
     {"id": "svc-a", "type": "rectangle", "x": 100, "y": 200, "width": 160, "height": 60, "text": "Web Server 1"},
     {"id": "svc-b", "type": "rectangle", "x": 450, "y": 200, "width": 160, "height": 60, "text": "Web Server 2"},
     {"id": "db", "type": "rectangle", "x": 275, "y": 350, "width": 210, "height": 60, "text": "PostgreSQL"},
     {"type": "arrow", "x": 0, "y": 0, "startElementId": "lb", "endElementId": "svc-a"},
     {"type": "arrow", "x": 0, "y": 0, "startElementId": "lb", "endElementId": "svc-b"},
     {"type": "arrow", "x": 0, "y": 0, "startElementId": "svc-a", "endElementId": "db"},
     {"type": "arrow", "x": 0, "y": 0, "startElementId": "svc-b", "endElementId": "db"}
   ]
   ```
4. Set shape widths using `max(160, labelLength * 12)`.
5. Call `get_canvas_screenshot`, inspect the returned image, run the Quality Checklist, and fix issues before finishing.

---

## Arrow Routing — Avoid Overlaps

Straight arrows can cross through elements in complex diagrams. Use curved or elbowed arrows when needed:

**Curved arrows** (smooth arc over obstacles):
```json
{
  "type": "arrow", "x": 100, "y": 100,
  "points": [[0, 0], [50, -40], [200, 0]],
  "roundness": {"type": 2}
}
```
The intermediate waypoint `[50, -40]` lifts the arrow upward. `roundness: {type: 2}` makes it smooth.

**Elbowed arrows** (right-angle / L-shaped routing):
```json
{
  "type": "arrow", "x": 100, "y": 100,
  "points": [[0, 0], [0, -50], [200, -50], [200, 0]],
  "elbowed": true
}
```

**When to use which:**
- Fan-out (one source → many targets): curved arrows with waypoints spread to avoid overlapping
- Cross-lane (connecting to side panels): elbowed arrows that go up, then across, then down
- Long horizontal connections: curved arrows with a slight vertical offset

**Rule:** If an arrow would pass through an unrelated shape, add a waypoint to route around it.

---

## Workflow: Iterative Refinement

Pairing `describe_scene` with `get_canvas_screenshot` makes this skill effective.

- **`describe_scene`** → structured text with element IDs, types, positions, labels, connections, and bounds. Use it to understand the canvas before updating elements.
- **`get_canvas_screenshot`** → rendered image for visual quality verification — check truncation, overlap, and arrow routing. Use `scale: 2` for dense diagrams, `elementIds` or `frameId` to inspect part of a scene, and `dark: true` for dark mode.

**Feedback loop:**
```
batch_create_elements
  → get_canvas_screenshot → inspect → "text truncated on auth-svc"
  → update_element auth-svc (width: 220) → get_canvas_screenshot → "overlap between auth-svc and rate-limiter"
  → update_element rate-limiter (x: 520) → get_canvas_screenshot → "all checks pass"
  → proceed
```

## Workflow: Refine an Existing Diagram

1. Call `describe_scene` to understand the current canvas — note element IDs and positions.
2. Identify elements by `id` or label text (not by x/y coordinates — they change).
3. Use `update_element` to resize, recolor, or move; use `delete_element` to remove; or bundle operations with `apply`. **Bound arrows re-route automatically when you move or resize their endpoints** — no need to delete and recreate them.
4. Call `get_canvas_screenshot` to confirm the change looks right.
5. If updates fail, check the ID with `get_element`; unlock it with `unlock_elements` if needed.

## Workflow: Mermaid Conversion

Call `create_from_mermaid` with a Mermaid diagram string.
Mermaid conversion runs in the canvas frontend and requires an open browser tab. Afterwards call `get_canvas_screenshot` to verify layout. If the auto-layout is poor (nodes crowded, edges crossing), use `describe_scene` and `update_element` to reposition elements.

## Workflow: File I/O

- Export scene with `export_scene` (`filePath` is optional; a `.excalidraw.md` path writes Obsidian's format).
- Import scene with `import_scene`, choosing `mode: "merge"` to add to the canvas or `mode: "replace"` only when the user intends to replace it.
- Export images with `export_to_image` as PNG or SVG (headless; SVGs embed their fonts).
- Offline: `render diagram.excalidraw --out diagram.png` renders a saved file without the canvas server (CI-friendly, same flags as `screenshot`)
- Share link with `export_to_excalidraw_url` — encrypts the scene and returns a shareable excalidraw.com URL.

This is how diagrams live in a repo: commit the `.excalidraw` file, and re-`import` + edit + `export` it when the architecture changes.

### Obsidian vaults: use `.excalidraw.md`

Check the destination before writing: if any ancestor directory contains `.obsidian/`, it is an Obsidian vault. A raw `.excalidraw` file there opens in the Excalidraw plugin only in **compatibility mode** ("Convert to new format" warning), gets no block references or vault-wide search, and default Obsidian Sync skips non-`.md` files. Give `export_scene` a `filePath` ending in `.excalidraw.md` to write the plugin's native format:

export_scene(filePath: "$VAULT/diagrams/system-map.excalidraw.md")
import_scene(filePath: "$VAULT/diagrams/system-map.excalidraw.md", mode: "replace")

Round-trips are safe: text-element block references follow the plugin's own id rules, so re-importing, editing, and re-exporting the same file keeps links from other notes intact.

## Workflow: Snapshots

1. Call `snapshot_scene` before risky changes.
2. Make changes and evaluate with `describe_scene` and `get_canvas_screenshot`.
3. Call `restore_snapshot` to roll back if needed.

## Workflow: Duplication

Use `duplicate_elements` with element IDs and an offset. Useful for repeated patterns or copying layouts.

## Error Recovery

- **Canvas unreachable?** Check whether the MCP server is running and `EXPRESS_SERVER_URL` points to the expected canvas.
- **Elements not appearing?** Call `describe_scene` to check whether they're off-screen. Use `set_viewport` with `scrollToContent: true`, or `scrollToElementIds` plus optional `viewportZoomFactor` to focus on a subgraph.
- **Arrow not connecting?** Verify element IDs with `get_element`. Make sure `startElementId` and `endElementId` match existing element IDs.
- **Canvas in a bad state?** Save a `snapshot_scene` before making changes, then use `restore_snapshot` if needed. Preserve the canvas unless the user asks to clear or replace it.
- **Element won't update?** It may be locked; call `unlock_elements` for its ID.
- **Duplicate text elements?** Excalidraw creates bound text elements for shape labels. Avoid labels on large background rectangles; use free-standing text elements instead.

---

## References

- `references/cheatsheet.md`: CLI reference, MCP tools, REST API endpoints and payload shapes, and the diagram design guide.
- Source: [yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw), MIT License.
