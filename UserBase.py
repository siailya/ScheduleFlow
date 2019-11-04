from pickle import load, dump


def from_base():
    with open('data/base.pickle', 'rb') as f:
        u = load(f)
    k = 0
    s = ''
    for i in u.keys():
        k += 1
        u[i].append(1)
        s += f'{str(k).ljust(4)};{str(i).ljust(11)};{u[i][0].ljust(10)[:10]};' \
             f'{u[i][1].ljust(15)[:15]};{u[i][2].ljust(4)[:4]};{str(u[i][3]).ljust(3)[:3]}' \
             f';{str(u[i][4]).ljust(3)[:3]}\n'
    return s


def write_csv(s):
    with open('data/base.csv', 'w', encoding='utf-8') as f:
        f.write(s)


def write_base():
    users = {}
    with open('data/base.csv', 'r', encoding='utf-8') as f:
        for i in f.read().split('\n'):
            a = i.split(';')
            if a[0]:
                n, uid, name, last, cls, st, auto = a
                n, uid, st, auto = int(n), int(uid), int(st), int(auto)
                name, last, cls = name.rstrip(), last.rstrip(), cls.rstrip()
                users.update({uid:[name, last, cls, st, auto]})
    with open('data/base.pickle', 'wb') as f:
        dump(users, f)


print(from_base())

