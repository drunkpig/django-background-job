from background_job.job import cron_job, delayed_job, interval_job, once_job, boot_job


@cron_job(name="my_func3", cron="*/1 * * * *")
def my_func3():
    print("my_func3()")
    return "this is func3"


# @cron_job(name="my_func", cron="*/2 * * * *", args=('X parameter',), kwargs={"name":"Jin", "age":23})
# def my_func(x, name="Jos", age=20):
#     print(f"my_func(x={x}, name={name}, age={age})")


@boot_job(name="my_func2", )
def my_func2():
    print("my_func2()")


@interval_job(name="间隔执行", enable=False, seconds=5, args=('NAME',"VALUE"))
def interval_func(name, value):
    print(f"interval_func({name}, {value})")
    return "interval_func ************************"


@once_job(name="once_job只运行一次", run_at="2021-02-16 23:39:00", args=("NAME",), kwargs={"key":"KEY"})
def run_once_func(name, value=33, key="xyz"):
    print(f"run_once_func({name}, {value}, {key})")


@delayed_job(name="测试用delayed_job", retry=-1, description="只是用在测试上")
def delayed_job_func(name, value):
    print(f"{delayed_job_func}({name}, {value})")


def common_func(name, value):
    print(f"interval_func({name}, {value})")
    return "hhhhhhh"