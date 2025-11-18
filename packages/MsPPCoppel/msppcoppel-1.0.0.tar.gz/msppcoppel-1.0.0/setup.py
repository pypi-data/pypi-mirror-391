import setuptools
from MsPPCoppel import version

with open("README.md", "r") as fh:
    long_description = ''  # fh.read()

setuptools.setup(
    name="MsPPCoppel",
    version=version,
    author="Carlos Baez",
    author_email="carlos.baez@coppel.com",
    description="Libreria para microservicios REST",
    long_description=long_description,

    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        'kafka-python==2.2.15',
        'Logbook==1.9.1',
        'asyncio-nats-client==0.10.0',
        'jaeger-client==4.3.0',
        'fluent-logger==0.11.1',
        # 'Flask==1.1.1',
        'bottle==0.13.4',
        'coloredlogs==15.0.1',
        'colorama==0.4.3',
        'Pygments==2.19.2',
        # 'event-signal==1.8.0',
        'waitress==3.0.2',
        "redis==7.0.1",
        'contextvars==2.4',
        "requests==2.32.5",
        "autodynatrace==1.0.75",
        "opentracing==2.4.0"
    ]
)
