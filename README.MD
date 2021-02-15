# django-background-job

include all features of apscheduler and django-apscheduler, but more than that:

- delayed job
- cron
- interval until
- once  at
- distributed deploy with etcd
- less db pressure



## arch

![docs/arch.png](docs/arch.png)



## references

- [django-background-task](https://github.com/lilspikey/django-background-task)
- [cron trigger](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html)
- [once trigger](https://apscheduler.readthedocs.io/en/stable/modules/triggers/date.html#module-apscheduler.triggers.date)
- [interval interval](https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html#module-apscheduler.triggers.interval)