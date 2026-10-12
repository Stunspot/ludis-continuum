# Start here

Open the visual session desk with `codex/ludis-continuum/workspace/Open Ludis.cmd` on Windows or `Open Ludis.command` on macOS (Python 3.10+). Read `workspace/README.md` for shared native records, restart and player-candidate behavior. No desktop shortcut is installed automatically.

1. Read the maintained [orientation](source/ludis-continuum-v1.4.1/README.md) and [installation journey](source/ludis-continuum-v1.4.1/START-HERE.md).
2. For Codex, install the complete `codex/ludis-continuum/` folder as one skill root.
3. For Claude, install the untouched `claude/ludis-continuum-v1.4.1.zip`.
4. Restart or reload the host, confirm discovery, and invoke Ludis explicitly once.
5. Run `python -B scripts/self_check.py` from the installed skill root.
6. Keep campaign material outside the installed skill. Back it up before migration, export, or import work.

Do not install `source/`, manifests, checksums, or release notes as runtime cargo.

Windows: first open the existing Open Ludis.cmd; it refreshes adjacent Open Ludis.lnk with the product icon. Run the command again after moving the folder. Mac command applies its ICNS before ordinary launch; native Mac execution is unverified. Icon binding failure leaves launch usable.
