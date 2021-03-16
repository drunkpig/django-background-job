from setuptools import find_packages, setup

setup(
    name='django-background-job',
    version='0.0.1',
    description='APScheduler for Django',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
    ],
    keywords='django background task, background job',
    url='https://github.com/drunkpig/django-background-job.git',
    author='drunkpig',
    author_email='xuchaoo@gmail.com',
    license='MIT',
    packages=find_packages(
        exclude=("tests", )
    ),
    install_requires=[
        'django>=1.11',
        'apscheduler',
        'crontab'
    ],
    zip_safe=False
)
