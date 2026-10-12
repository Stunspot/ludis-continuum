function run(argv) {
    ObjC.import('AppKit');
    var icon = $.NSImage.alloc.initWithContentsOfFile(argv[0]);
    if (!icon) throw new Error('Ludis Continuum ICNS could not be read');
    var workspace = $.NSWorkspace.sharedWorkspace;
    for (var i = 1; i < argv.length; i++) {
        if (!workspace.setIconForFileOptions(icon, argv[i], 0))
            throw new Error('Ludis Continuum entry icon could not be applied');
    }
}
