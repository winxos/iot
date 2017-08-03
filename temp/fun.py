def f():
    a = 10
    b = {}

    def f2(a, b):
        a = 8
        b['a'] = 0
        yield 'f2'

    c = f2(a, b)
    r = next(c)
    print(r)
    print(a)
    print(b)


f()
