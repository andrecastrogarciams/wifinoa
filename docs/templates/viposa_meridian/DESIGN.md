# Design System Document: Precision Editorial for Network Intelligence

## 1. Overview & Creative North Star
### Creative North Star: "The Orchestrated Core"
Network access management is often cluttered and chaotic. This design system rejects the "standard dashboard" aesthetic in favor of **The Orchestrated Core**—a visual philosophy that treats data management as a high-end editorial experience. We prioritize data density not through compression, but through clear architectural hierarchy and tonal depth.

By moving away from traditional grid lines and opting for **Asymmetric Layering**, we create a signature look that feels custom and premium. The system uses the brand’s authoritative deep blue (`primary`) and high-energy orange (`secondary`) to guide the eye toward critical operational nodes, while the background remains a calm, sophisticated canvas of cool greys and whites.

---

## 2. Colors: Tonal Architecture
Instead of separating sections with harsh lines, we use a chromatic scale of surfaces to define importance and functional zones.

*   **Primary (`#002c57`) & Secondary (`#9f4200`):** Reserved for high-intent actions and brand identity. Use `primary` for global navigation and `secondary` for critical system alerts or "Add/Create" actions.
*   **The "No-Line" Rule:** 1px solid borders are strictly prohibited for sectioning. Structural boundaries must be defined by shifts between `surface`, `surface_container_low`, and `surface_container_high`.
*   **Surface Hierarchy & Nesting:**
    *   **Level 0 (Background):** `surface` (`#f7f9ff`) - The foundation.
    *   **Level 1 (Main Content Area):** `surface_container_low` (`#f1f4fa`) - A subtle recess for the primary workspace.
    *   **Level 2 (Data Cards):** `surface_container_lowest` (`#ffffff`) - Pure white cards that "pop" against the recessed workspace.
*   **The "Glass & Gradient" Rule:** Floating modals or navigation overlays should utilize `surface` colors with a 80% opacity and a `20px` backdrop-blur. For main CTAs, apply a subtle linear gradient from `primary` (`#002c57`) to `primary_container` (`#1a4273`) to add "soul" and depth to the button face.

---

## 3. Typography: The Editorial Voice
We use **Inter** for its mathematical precision and high legibility in dense data environments.

*   **Display & Headlines:** Use `display-md` and `headline-lg` sparingly for high-level dashboard summaries. These should have a slight letter-spacing reduction (-0.02em) to mimic premium print typography.
*   **Titles & Body:** `title-md` (`1.125rem`) is our workhorse for card headers. `body-md` (`0.875rem`) provides the density required for network logs and table data.
*   **Labels:** `label-sm` (`0.6875rem`) should be used for metadata and table headers, set in All Caps with +0.05em tracking to ensure readability at small sizes.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are replaced by **Ambient Occlusion** and **Tonal Stacking**.

*   **The Layering Principle:** A `surface_container_lowest` card sitting on a `surface_container_low` background creates a natural, soft lift. This is our primary method of elevation.
*   **Ambient Shadows:** For "Active" states or floating elements, use an extra-diffused shadow: `box-shadow: 0 12px 32px rgba(24, 28, 32, 0.06)`. Note the use of the `on_surface` color (`#181c20`) at a very low opacity rather than pure black.
*   **The "Ghost Border" Fallback:** In high-density tables where separation is critical, use a "Ghost Border": `1px solid outline_variant` (`#c3c6d0`) at 15% opacity. Never use 100% opaque borders.
*   **Glassmorphism:** Navigation sidebars should feel lightweight. Use `surface` at 85% opacity with `backdrop-filter: blur(12px)`.

---

## 5. Components: Optimized for Velocity

### Buttons (High-Intent Primitives)
*   **Primary:** Gradient fill (`primary` to `primary_container`), white text, `md` (`0.375rem`) roundedness.
*   **Critical Action:** `secondary` (`#9f4200`) background. Use this only for "Grant Access" or "Revoke" to ensure it cuts through the blue-heavy UI.
*   **Tertiary:** No background or border. Use `primary` text. On hover, apply a `surface_container_high` background tint.

### Data Tables & Dashboard Cards
*   **The "No-Divider" Rule:** Forbid 1px dividers between rows. Use alternating row colors (Level 0 to Level 1) or `16px` of vertical whitespace to separate items.
*   **Header Style:** Use `label-md` with `on_surface_variant` color. 
*   **Density:** Content should use `body-sm` for data-heavy cells to maximize information per screen.

### Input Fields & Controls
*   **Text Inputs:** Use `surface_container_highest` for the field background with a "Ghost Border." Focus state uses a `primary` 2px bottom-only border to maintain an editorial feel.
*   **States:**
    *   **Success:** Use a subtle `surface_container` background with a `secondary` (orange) accent icon (Viposa's orange acts as a high-visibility indicator).
    *   **Error:** Background `error_container`, text `on_error_container`.
    *   **Loading:** Use a custom shimmering skeleton screen using a gradient from `surface_container` to `surface_container_high`.

### Additional Component: The "Network Node" Chip
*   A custom compact chip for IP addresses or Node IDs. Use `surface_container_high` background with `title-sm` monospace font for distinct readability.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts (e.g., a wide data table balanced by a narrow right-hand telemetry column).
*   **Do** prioritize vertical rhythm over horizontal lines.
*   **Do** use `secondary_container` (orange) for system notifications to ensure they are never missed in a sea of blue.

### Don't
*   **Don't** use 100% opaque black shadows; they feel "cheap" and dated.
*   **Don't** use standard 1px borders to separate dashboard widgets; use background color shifts instead.
*   **Don't** crowd the UI. Even in high-density modes, use `xl` (`0.75rem`) internal padding for cards to let the data "breathe."