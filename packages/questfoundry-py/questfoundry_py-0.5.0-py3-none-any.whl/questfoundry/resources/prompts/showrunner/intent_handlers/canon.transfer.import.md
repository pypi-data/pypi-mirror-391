# Intent Handler — canon.transfer.import

Inputs

- Envelope with `intent = canon.transfer.import`, referencing Canon Transfer Package artifact ID.
- Optional: seed_ideas (list of project-specific ideas to validate against invariant canon).

Preconditions

- Canon Transfer Package artifact exists in hot workspace.
- Current project has initialized entity registry and timeline manager (or will create them).
- Caller has authorization to import canon (typically Showrunner or Lore Weaver).

Process

1. Validate envelope (required: package_id; optional: seed_ideas, conflict_resolution_strategy).
2. Load Canon Transfer Package from hot workspace.
3. Validate package structure and integrity:
   - Verify mutability labels (invariant vs mutable)
   - Check timeline chronological consistency
   - Validate entity registry format
4. If seed_ideas provided, run conflict detection:
   - Use ConflictDetector to identify contradictions with invariant canon
   - Generate ConflictReport with severity and resolution recommendations
   - If critical conflicts found, halt import or request user guidance
5. Merge canon into current project:
   - Entity Registry: Merge entities with deduplication (immutable takes precedence)
   - Timeline: Merge anchors with chronological validation
   - Canon Facts: Add to project canon with immutability tracking
6. Generate Constraint Manifest:
   - Extract invariants ("You CANNOT")
   - Extract mutables ("You CAN")
   - Document timeline and entity constraints
   - Export as markdown and save to hot workspace
7. Update artifact metadata:
   - Mark imported canon with `immutable` flag
   - Track source attribution (original project name)
8. Optionally promote canon artifacts to cold storage with `immutable=true` and `source="canon-import"`.
9. Acknowledge import success with summary (entities imported, conflicts resolved, constraints generated).

Outputs

- Merged entity registry and timeline in project state.
- Constraint Manifest artifact in hot workspace.
- Conflict Report (if seed_ideas provided).
- Canon artifacts in cold storage (if promoted).
- Acknowledgment envelope with import summary.

Errors

- validation_error (invalid package structure or missing required fields)
- not_authorized (caller lacks import permission)
- conflict_critical (unresolvable conflicts between invariant canon and seed ideas)
- timeline_error (chronological inconsistencies in merged timeline)
- entity_duplicate (conflicting entities with same name but different immutability)

References

- 00-north-star/LAYER6_7_CANON_IMPACT.md §2.1 Canon Transfer Package
- 00-north-star/LAYER6_7_CANON_IMPACT.md §3.2 Conflict Detection
- 00-north-star/LAYER6_7_CANON_IMPACT.md §3.3 Constraint Manifests
- 04-protocol/INTENTS.md §7.2 canon.transfer.import
