---
name: excalidraw
description: Plan and refine clear, informative Excalidraw diagrams for workflows, systems, architectures, and concepts. Use whenever a request needs a diagram created or edited, including local .excalidraw files, Obsidian .excalidraw.md drawings, or rendered images for Markdown. Use the Excalidraw MCP tools for all canvas operations; this skill supplies design guidance.
---

# Excalidraw Diagram Design

Use the configured Excalidraw MCP server to create and edit diagrams. This skill guides the visual decisions; the MCP tools handle the canvas, files, screenshots, and image exports.

## Design for Meaning

Make the structure explain the idea. A diagram should show relationships, causality, and flow that plain text cannot show as clearly. Before drawing, ask: if the labels disappeared, would the arrangement still suggest how the parts relate? If not, choose a more meaningful structure.

Avoid defaulting to equal boxes in a grid. Match each visual pattern to the idea it represents, and use variety when a diagram contains several distinct concepts.

## Choose the Right Level of Detail

For a quick conceptual explanation, use a few abstract shapes and clear relationships. For a technical system, protocol, tutorial, or educational diagram, include concrete evidence: real event or method names, small request or response examples, relevant code, or a sequence of actual steps.

Before drawing technical details, verify the names, formats, and relationships against the source material or authoritative documentation. Mark assumptions when a detail cannot be confirmed.

For a comprehensive diagram, plan three levels:

1. A summary flow that shows the whole subject at a glance.
2. Sections that group components by responsibility, phase, actor, or boundary.
3. Concrete examples inside sections that help explain how the system works.

Build large diagrams a section at a time. Give elements stable, descriptive IDs so later edits and cross-section connections are easy to make. Review the entire scene after all sections are present.

## Map Concepts to Visual Patterns

Choose patterns that carry meaning:

| Relationship | Useful pattern |
|---|---|
| One source creates several outcomes | Fan-out with branches or radial arrows |
| Several inputs combine | Convergence or a funnel |
| Parent-child relationships | Tree branches with lines and labels |
| Steps happen over time | Timeline with markers and labels |
| A process repeats | Cycle or return arrow |
| Information changes form | Before, transformation, and after |
| Two choices differ | Side-by-side structures with visible contrast |
| Phases or boundaries matter | Distinct sections separated with space or dividers |

Trace the path a viewer's eye should follow before placing elements. Use left-to-right or top-to-bottom for ordered flows, and radial layouts for hubs. Connect related elements with arrows or lines; position alone rarely explains a relationship.

## Use Shapes and Text Deliberately

Default to free-floating text. Add a container when it groups related elements, represents a meaningful object, or gives an arrow a clear target. Section headings and annotations usually need typography rather than a box.

Use shapes according to their meaning: ellipses for entry or exit points, diamonds for decisions, rectangles for actions, small circles for timeline markers, and lines for trees, dividers, and timelines. Keep large background regions unlabeled internally; place their titles as separate text near the top edge.

Use scale and whitespace to set hierarchy. Give the main idea room, keep related items close, and use a consistent grid. Use font sizes large enough to read at the expected export size. Keep labels concise, especially on arrows.

Call the MCP server's `read_diagram_guide` before choosing colors and sizing. Use its semantic palette consistently: color should distinguish roles or states, with sufficient contrast between text, fills, and strokes. Avoid adding colors for decoration.

## Draw Through the MCP

Use MCP tools for every Excalidraw operation:

1. Call `read_diagram_guide` and inspect any existing scene with `describe_scene` before editing it.
2. Plan the content, sections, visual patterns, flow direction, and approximate coordinates.
3. Create related elements together with `batch_create_elements`. Add stable IDs and bind arrows to element IDs so connections remain attached during edits.
4. Refine existing elements with `update_element`, `delete_element`, and the layout tools. Preserve existing canvas content unless the user asks to replace or clear it.
5. Call `get_canvas_screenshot`, inspect the rendered image, and fix visual problems before finishing.

When converting an existing Mermaid diagram, use `create_from_mermaid`, then inspect and refine its layout through the MCP. If Mermaid's layout does not communicate the idea well, build or adjust the elements directly.

## Validate the Render

Do not judge a diagram from its element data alone. After creating or editing it, use `get_canvas_screenshot` and check:

- Text is readable and not clipped.
- Shapes and labels do not overlap unintentionally.
- Arrows connect to the intended elements and avoid unrelated content.
- Spacing is balanced and sections are easy to distinguish.
- The composition follows the planned visual path and gives emphasis to the right ideas.
- Technical examples are accurate and legible.

Fix defects with MCP edits, then take another screenshot. Repeat until the structure communicates the intended idea and the render is ready to share.

## Save for Markdown and Obsidian

For a repository diagram, use `export_scene` to save the editable `.excalidraw` source. Use `export_to_image` to create a PNG or SVG when a Markdown document or renderer needs an image; link to the image with a relative Markdown path and keep the editable source alongside it when useful.

For example, if the image is saved beside the note:

```markdown
![Service request flow](./service-request-flow.png)
```

For an Obsidian vault, save with `export_scene` to a path ending in `.excalidraw.md`. This uses the Excalidraw plugin's Markdown format. Use `import_scene` to reopen an existing drawing, and `export_to_image` when the Markdown page needs a directly rendered image.

Before delivering, report the saved paths and include or link the rendered image when the MCP returns one.

## Further Reading

- [Excalidraw MCP server](https://github.com/yctimlin/mcp_excalidraw) provides the canvas tools used by this skill.
- The visual design approach is informed by [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill).
