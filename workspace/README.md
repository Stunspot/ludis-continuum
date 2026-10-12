# Ludis Campaign Table

Open Open Ludis.cmd on Windows or Open Ludis.command on macOS. Python 3.10+ is required. The launcher starts or reconnects to the local loopback service and opens the browser. You can also run python workspace/desk.py --data-root YOUR_CAMPAIGN_DIRECTORY. LUDIS_DATA_HOME otherwise selects the shared store; the default is Documents/LudisContinuum. Keep one campaign per directory. The native campaign-ledger.json, history, and original imports live outside the package.

## Why open the table?

A conversational response can prepare a scene. The table keeps the scene, ordered cues, near horizon, prep, source status, and linked material visible while the GM moves through play. It makes relationships and competing records inspectable without reconstructing the world from chat. It never invents choices or treats a visibility label as player approval.

**Tonight** is the live working surface. Bring any material into the ordered extensions.workspace.tray list from **World & relationships**. Select a cue to focus its full text and explicit links. Move cues earlier or later; remove one without deleting the underlying object. The margin holds the campaign's actual premise and horizon, next_prep, and the latest session title/notes. These fields are draft changes until **Save campaign**.

**World & relationships** is the campaign's orientation surface. Search actual object text and filter all, tonight, or unresolved material. Selecting an object keeps its content beside status, visibility, confidence, tenure, export eligibility, authority, provenance, outgoing links, incoming links, and contradictions. Follow a link or compare two connected objects side by side. Pin material directly from this reading surface. The proposed-material editor is secondary; active canon is read-only in the table.

**At the table** captures observations, player choices as observations, notes, or proposed consequences as GM-only proposals. Recent captures stay visible. Recording a choice does not turn an interpretation into canon. **Ledger tools** holds native JSON, import and export, and the player reading candidate. A valid raw JSON draft follows you to another view locally; invalid JSON keeps you in the editor with an error. Saves use the native validator, exclusive lock, history, and digest-checked atomic writer. A stale change or unauthorized canon mutation is rejected while the draft remains available to export.

The player reading page is a separate server projection from the existing exporter. Only eligible, active, player-safe object ID/kind/title/content are included. GM metadata, table contract, arbitrary object data, provenance, assets, sessions, and the whole ledger are absent. It is a **candidate**: the GM reviews exact prose before sharing. Use the governed Tonight Pack tools for exact-byte approved exports. The table is a private local operator tool, not a multi-user VTT.

## Start and recover

Create a campaign with a stable ID and title, or import a native v2 ledger. The labeled example is unsaved and never replaces a native campaign. Legacy 0.1 ledgers need the existing migration tool before import. If the native record cannot load, the table shows a retryable error rather than claiming no campaign exists. If a save reports a stale ledger, export the current draft, reload, and reconcile it with the native record.

The two environments carry the same data and actions. **Night Routes**, the dark default, uses layered mineral and smoked-glass light to keep a playable focus, near horizon and ordered waypoints in view. **Patchwork World** uses dark woven earth, stitched tobacco reading surfaces, flax text and a restrained copper working thread; it is the dark woven alternative. Theme choice is a local browser preference and never changes the ledger. See [SKINS.md](SKINS.md) for the visual contract and theme records.

## Native entry icons

The browser tab uses the bundled Ludis icon. On Windows, the existing launcher creates or refreshes `Open Ludis.lnk` beside itself, targeting the adjacent launcher with its ICO; use that shortcut for the recognizable entry icon. After moving the folder, run `Open Ludis.cmd` once to refresh its paths. On macOS, the existing command applies the bundled ICNS to itself through AppKit before opening the desk. Icon binding is optional: a read-only installation or native icon error leaves the ordinary launcher usable. Native macOS execution has not been observed on the Windows repair host.
