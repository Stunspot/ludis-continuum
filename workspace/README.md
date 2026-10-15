# Ludis gaming table 1.5.0

Open **Open Ludis.cmd** on Windows or **Open Ludis.command** on macOS (Python 3.10+). The table opens in your browser. Your existing campaign is resumed when Ludis knows its location; otherwise the first screen offers **Start a campaign** and **Open an existing campaign**. **Campaigns & location** is always available to switch, recover, or choose another folder. Browse with the system folder dialog or paste a full path. A new campaign is created only when you choose Create campaign; its destination is checked for write access first.

## Get something ready to play

On **Tonight**, name the session, describe its opening, and name the next meaningful choice. Keep a character's resources and conditions in view. Add preparation tasks, roll real dice, order an encounter by initiative, and record choices or discoveries as they occur. The GM/player selector changes the working emphasis; it is not a security boundary or a player-sharing service. Edits save automatically, with visible success or recovery feedback. Download session notes when you want a portable recap.

Use **Materials & maps** to link the RPG folders you already use. Sources remain in place and are read without modifying their originals. Or import copies of documents, maps, pictures, audio, or ZIPs into the campaign's materials folder. PDF, common raster images, audio, plain text/Markdown, and Word DOCX text have in-app readers. DOCX text preview omits layout and illustrations; Open original opens your usual application. Other supported formats can be opened in their usual application. Images can be shown full-screen. Keep any file within reach on Tonight. Unlink source removes the connection and tonight's references, never the source files.

Browsing includes nested folders to eight levels and up to 5,000 supported files per source; a visible message identifies that limit. Link a smaller subfolder when needed. Imported batches are limited to 50 MB; link the original folder for larger files. A missing or unreadable source gives a recoverable message and does not replace the campaign.

**People & world** holds characters, NPCs, places, scenes, clues and other campaign material. Existing native campaign entries appear here. Read and edit your material, connect entries by their visible names, or bring them to Tonight. Internal identity, status and export metadata stay behind the interface. Existing export/approval tools retain their own responsibilities; editing material here does not approve a public or player export.

**Create & prepare** starts from the thing you need for play, with domain guidance spanning the 32 creative instruments. Draft and keep it directly, or use Copy campaign brief for Ludis to take the chosen purpose and relevant campaign context to your AI conversation. This offline app does not pretend to generate creative content; the Ludis skill in your conversational host performs that work. Bring the resulting text back into the table.

## Resume, sources, and recovery

The campaign folder contains the compatible campaign-ledger.json plus table-state.json for session, character, encounter and source connections. Existing native campaigns are read in place; their preparation and session notes seed the new table when no table-state file exists. Campaign changes preserve ledger history. Source files are not migrated automatically.

Campaigns & location remembers recent campaigns. The settings location is LOCALAPPDATA/LudisContinuum on Windows and ~/.local/share/LudisContinuum elsewhere; LUDIS_SETTINGS_HOME overrides it. A known LUDIS_DATA_HOME, the last opened campaign, or an existing legacy Documents/LudisContinuum campaign is resumed. With none of these, Ludis proposes a local application-data campaign folder and asks the user to create or choose a campaign. It does not assume that Documents is a data source.

LUDIS_LIBRARY_HOME offers an existing RPG library. A NOVA_DATA_ROOT or NOVA_HOME estate may also supply estate/rpg-library.json. The offered source becomes connected only when you choose Use this source. Individual sources and campaign locations remain selectable in the UI.

Campaign backup & recovery downloads campaign data and source links; linked files and imported materials should remain in your regular file backup. Restore a table backup or native v2 campaign into an empty folder. Original imported backup bytes are retained. Legacy v0.1 records still require the existing migration tool before they can be opened as a v2 campaign.

If saving fails, keep the tab open: the draft remains on screen, and Download session notes / Download campaign backup retain the work. The app rejects stale saves from another window. Reopen the saved campaign after retaining the draft to reconcile changes. No multi-user or remote synchronization is claimed.

## Appearance and platform

Night Routes keeps the session in a dark, mineral-lit working environment. Patchwork World uses a woven, field-notebook texture and contrasting seams. Both carry the same actions and information. Native Windows folder browsing is implemented; typed paths are also first-class. Local browser journey checks exercise Windows launch, ordinary files, session work, return, error recovery, and narrow layout. Live group play, native macOS dialogs and assistive-technology conformance remain unobserved.
