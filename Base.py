from pickle import dump


def write_base(base, stat):
    pt = 'data/base.pickle'
    with open(pt, 'wb') as fi:
        dump(base, fi)

    pt = 'data/stat.pickle'
    with open(pt, 'wb') as fi:
        dump(stat, fi)
