# Intent Handler — canon.genesis.create

Inputs

- Envelope with `intent = canon.genesis.create`, specifying worldbuilding parameters.
- Required: theme_list (core themes to explore), budget_level (minimal/standard/epic).
- Optional: baseline_anchors (timeline starting points), entity_seeds (initial entity ideas).

Preconditions

- Fresh project with no existing canon (or explicit override to reset canon).
- Caller has authorization to initiate world genesis (typically Showrunner).
- Lore Weaver role is available for canon-first worldbuilding loop.

Process

1. Validate envelope (required: theme_list, budget_level; optional: baseline_anchors, entity_seeds).
2. Validate budget level and set expectations:
   - **Minimal** (2-4 hours): 3-5 core themes, light detail, essential entities only
   - **Standard** (5-10 hours): 5-8 themes, moderate depth, balanced coverage
   - **Epic** (20+ hours): 10+ themes, exhaustive exploration, deep lore
3. Initialize world genesis state:
   - Create empty EntityRegistry
   - Create TimelineManager with baseline anchors (or default T0)
   - Initialize canon fact accumulator
4. Wake Lore Weaver role for canon-first worldbuilding loop:
   - Systematic theme exploration (history, geography, culture, magic, politics, etc.)
   - Entity creation with immutability marking (founders, ancient locations, etc.)
   - Timeline anchor definition (major historical events)
   - Canon fact documentation with mutability labels
5. Monitor progress against budget:
   - Track time/token expenditure per theme
   - Ensure balanced coverage across themes
   - Adjust depth dynamically based on budget
6. Generate World Genesis Manifest artifact:
   - Document explored themes with coverage level
   - List created entities (characters, places, factions, items)
   - Timeline with anchors and chronology
   - Canon facts organized by theme and mutability
   - Metadata: budget used, themes explored, entity count
7. Generate Constraint Manifest from genesis output:
   - Extract invariants from immutable canon
   - Extract mutables from extensible canon
   - Document timeline and entity constraints
   - Provide creative guidance for Story Spark
8. Promote genesis artifacts to cold storage:
   - Entities with `immutable=true` and `source="world-genesis"`
   - Timeline anchors with baseline designation
   - Canon packs with mutability tracking
9. Acknowledge genesis completion with summary (themes explored, entities created, timeline established, constraints defined).

Outputs

- World Genesis Manifest artifact in hot workspace.
- Constraint Manifest artifact in hot workspace.
- EntityRegistry populated with genesis entities.
- TimelineManager populated with baseline anchors.
- Canon artifacts promoted to cold storage.
- Acknowledgment envelope with genesis summary.

Errors

- validation_error (invalid theme_list or budget_level)
- not_authorized (caller lacks world genesis permission)
- budget_exceeded (worldbuilding exceeded time/token budget)
- canon_exists (project already has canon and no override specified)
- theme_incomplete (insufficient coverage of required themes)

References

- 00-north-star/LAYER6_7_CANON_IMPACT.md §2.2 World Genesis Manifest
- 00-north-star/LAYER6_7_CANON_IMPACT.md §3.1 Canon-First Worldbuilding
- 00-north-star/LAYER6_7_CANON_IMPACT.md §3.3 Constraint Manifests
- 04-protocol/INTENTS.md §7.3 canon.genesis.create
