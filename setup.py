#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='django-admin-kubi',
    version='1.0.9',
    description='A Django admin template replacement focused on flexibility and user experience',
    author='Rafael Fernandes',
    author_email='rafael@dengun.com',
    url='https://github.com/dengunorg/django-admin-kubi',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description=open('description.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    requires=['Django(>=4.0)'],
    install_requires=[],
    zip_safe=False,
)
