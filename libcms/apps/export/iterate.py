def iterate(qs, package = 100000):
    offset = 0
    while True:
        limit = offset + package
        count = 0
        for model in qs[offset: limit].iterator():
            count += 1
            yield model

        offset += package
        if count == 0:
            break