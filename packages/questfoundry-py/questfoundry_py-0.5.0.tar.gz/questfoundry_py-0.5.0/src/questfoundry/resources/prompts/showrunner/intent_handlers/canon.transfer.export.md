# Intent Handler — canon.transfer.export

Inputs

- Envelope with `intent = canon.transfer.export`, specifying mutability filter and optional entity/timeline filters.

Preconditions

- Cold storage contains canon artifacts ready for export.
- Caller has authorization to export canon (typically Showrunner or Lore Weaver).

Process

1. Validate envelope (required fields: mutability level, optional filters for entity types, timeline anchors).
2. Query cold storage for canon artifacts matching mutability filter:
   - **Invariant**: Export only immutable canon (`metadata.immutable = true`)
   - **Mutable**: Export extensible canon (`metadata.immutable = false`)
   - **Mixed**: Export both types with clear labeling
3. Filter by entity types if specified (characters, places, factions, items).
4. Filter by timeline anchors if specified (baseline vs extension anchors).
5. Extract canon facts, entity registry entries, and timeline anchors.
6. Generate Canon Transfer Package artifact with:
   - Canon facts organized by mutability level
   - Entity registry with source attribution
   - Timeline anchors with chronological validation
   - Metadata: source project, export timestamp, version
7. Save Canon Transfer Package to hot workspace with `immutable=true` and `source="canon-export"`.
8. Optionally validate package integrity (no conflicts, valid timeline).
9. Acknowledge export success with package artifact ID.

Outputs

- Canon Transfer Package artifact in hot workspace.
- Export metadata and validation report.
- Acknowledgment envelope with artifact ID.

Errors

- validation_error (invalid mutability filter or missing required fields)
- not_authorized (caller lacks export permission)
- empty_export (no canon artifacts match filters)
- integrity_error (exported canon contains conflicts or invalid timeline)

References

- 00-north-star/LAYER6_7_CANON_IMPACT.md §2.1 Canon Transfer Package
- 04-protocol/INTENTS.md §7.1 canon.transfer.export
