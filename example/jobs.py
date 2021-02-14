from job import cron_job


@cron_job(name="my_func", cron="* */2 * * *")
def my_func(x, name="jon", age=20):
    print("Inside actual function")
    print(f"name={name}, age={age}")


@cron_job(name="my_func2", cron="* */6 * * *")
def my_func2():
    print("Inside actual xxxx function")


# if __name__=="__main__":
#     print("main")
#     #f2test()
#     #ftest()
#     my_func()
#     #f3test()