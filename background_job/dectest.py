


class Dec(object):
    def hello(self):
        def tt(func):
            print(func)
        print("hello, make sth.")
        return tt

    def h2(self, kw):
        def t2(func):
            print(func)
        print("h2")
        print(kw)
        return t2

    @staticmethod
    def h3():
        def t2(func):
            print(func)
        print("h2")

        return t2



# t = Dec()
#
#
# @t.hello()
# def ftest():
#     print("ftest()")

@Dec.h3()
def f2test():
    print("f2test")

if __name__=="__main__":
    print("main")
