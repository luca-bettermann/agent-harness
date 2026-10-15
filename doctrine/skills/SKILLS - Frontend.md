Owns browser implementation, layout, journeys and rendered acceptance. [[SKILLS - SSOT and Single Pipeline]] owns served meaning. [[SKILLS - Coding]] owns implementation and test quality; [[SKILLS - Visual Identity]] owns visual standards, and [[Writing Guide]] owns interface language. INSTANCE names standing previews and browser tooling.

## Served meaning

A browser presents the domain meaning supplied by its authoritative projection.

**Covers:** Vocabulary, labels, enabled state, refusals and fixtures.

**Applying:** A control renders the projection's label and enabled state, including a distinct unknown state.

**Violating:** A browser maintains its own operation list or infers eligible actions from path names.

**Detailed rules:**

- Consume typed envelopes under SSOT's projection rules. Do not reconstruct eligibility, lineage or vocabulary in the client. Display mappings follow that owner's rule.
- Use producer-generated or contract-validated fixtures with realistic identities. Repeated fake identifiers and ports can conceal broken links and layouts.

## Thin views

Presentation code separates interaction state, rendering and placement so each has one responsibility.

**Covers:** View models, DOM updates, layout containers and components.

**Applying:** A pure view function folds interaction data, and a layout container places reusable content.

**Violating:** Scattered flags recreate a state machine or a component fixes its own screen coordinates.

**Detailed rules:**

- Use pure functions for view logic and keep the DOM layer focused on rendering and input. Fold interaction state from data instead of scattered flags.
- Containers own placement; components own content. Use shared layout tokens for chrome, docks and strips instead of private fixed coordinates.
- Apply Coding to JavaScript as to Python. Changed JavaScript passes lint and view-model tests; syntax checking alone is not a gate.
- Patterns are portable, but shared code across repositories needs a justified public owner. Palettes remain with their existing authorities.

## Journeys prove interactions

Rendered acceptance demonstrates the complete user journey on the live surface before human handoff.

**Covers:** Committed flows, preview review, affordance coverage and operator acceptance.

**Applying:** The implementer runs the committed journey, then the reviewer drives the full journey on the updated live preview before handing it to the operator.

**Violating:** Screenshots of selected states or a diff stand in for interactions across the complete journey.

**Detailed rules:**

- Settle design in chat and record the accepted specification in the task note. Work owns the review process.
- The implementer runs the committed headless journey for every increment. Cover both navigation directions and all layouts, including mounting and unmounting chrome, scrub and seek, window addition, replacement and closure, link formation, tooltips and overlap.
- Enumerate tooltips and affordances and assert that list in the flow. Apply Coding's denominator and exact-outcome rules; expected bytes and refusals follow actual artifact selection. Never suppress all browser errors or pin arbitrary variant numbers.
- Update the standing preview with realistic data before review. The reviewer personally drives the full journey on that live preview before any human handoff. No preview link goes to the operator before this pass.
- Verify closed findings against the rendered surface. The operator reviews the result and accepts it in chat. These gates remain distinct from verification ownership under Interfaces.
