from pickle import dump, load


def write_base(base, stat):
    pt = 'data/base.pickle'
    with open(pt, 'wb') as fi:
        dump(base, fi)

    pt = 'data/stat.pickle'
    with open(pt, 'wb') as fi:
        dump(stat, fi)


def open_base(base, stat):
    pt = 'data/base.pickle'
    with open(pt, 'rb') as fi:
        base = load(fi)

    pt = 'data/stat.pickle'
    with open(pt, 'wb') as fi:
        stat = load(fi)
