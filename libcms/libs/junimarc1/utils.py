# coding=utf-8
def beautify(libcard):
    replaces = [
        ('. :', '.:'),
        (', .', '. '),
        ('. .', '. '),
        ('.  .', '. '),
        ('— , ', '— '),
        ('.. ', '. '),
        ('..,', '.,'),
        ("..\n", ".\n"),
        ("..<", ".<"),
        ("..<", ".<"),
        (".</a>\n", ".</a>"),
        (".</p>\n", ".</p>"),
        (".</a>.", ".</a>"),
        (".</div>.", ".</div>"),
        (".<div class=\"links\">.", ".<div class=\"links\">"),
        (".</b>.", ".</b>"),
        (".</p>.", ".</p>"),
        (".</a><p></p>.", ".</a><p></p>"),
        (".</a></div>.", ".</a></div>"),
        ("%2B", "+"),
    ]
    r = libcard
    for replace in replaces:
        r = r.replace(replace[0], replace[1])
    return r