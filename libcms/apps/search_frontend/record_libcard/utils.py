def beautify_libcard(libcard: str):
    uni_libcard = libcard
    if isinstance(uni_libcard, bytes):
        uni_libcard = uni_libcard.decode('utf-8')

    replaces = [
        ('. :', '.:'),
        (', .', '. '),
        ('. .', '. '),
        ('.  .', '. '),
        ('— , ', '— '),
        # ('.. ', '. '),
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
        (".</div> .", ".</div>"),
        (".</a><p></p>.", ".</a><p></p>"),
        (".</a></div>.", ".</a></div>"),
        ("%2B", "+"),
        ('.—.—', '.—'),
        ('Перевод издания:', '<b>Перевод издания</b>:'),
    ]

    r = uni_libcard
    for replace in replaces:
        r = replace[1] \
            .join(
            r.split(replace[0])
        )
    return r