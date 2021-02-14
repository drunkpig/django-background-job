import logging
from logging.config import fileConfig

from example.jobs import *


if __name__=="__main__":

    fileConfig("../logging.ini")
    logger = logging.getLogger()

    print("***********************")
    my_func(3, name="xu")
    print("---------------------------")
    my_func(5)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    my_func2()
