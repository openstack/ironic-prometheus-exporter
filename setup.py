import re

from setuptools import setup, find_packages


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


setup(
    name='ironic_prometheus_exporter',
    version='1.0.0',
    description='Prometheus Exporter for Ironic Hardware Sensor data',
    url='',
    author='Iury Gregory Melo Ferreira',
    author_email='imelofer@redhat.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'oslo.messaging.notify.drivers': [
            'prometheus_exporter=\
             ironic_prometheus_exporter.messaging:PrometheusFileDriver',
            'file_exporter=\
             ironic_prometheus_exporter.messaging:SimpleFileDriver',
        ],
    },
)
