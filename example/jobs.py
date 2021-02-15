from job import cron_job


@cron_job(name="my_func3", cron="*/1 * * * *")
def my_func3():
    print("my_func3()")


@cron_job(name="my_func", cron="*/2 * * * *", args=('X parameter',), kwargs={"name":"Xu", "age":33})
def my_func(x, name="jon", age=20):
    print(f"my_func(x={x}, name={name}, age={age})")


@cron_job(name="my_func2", cron="*/1 * * * *")
def my_func2():
    print("my_func2()")


# if __name__=="__main__":
#     print("main")
#     #f2test()
#     #ftest()
#     my_func()
#     #f3test()