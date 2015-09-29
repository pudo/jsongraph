from setuptools import setup, find_packages


setup(
    name='jsongraph',
    version='0.2.2',
    description="Library for data integration using a JSON/RDF object graph.",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='schema jsonschema json rdf graph sna networks',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/jsongraph',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={
        '': ['jsongraph/schemas/*.json']
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'jsonmapping',
        'mqlparser',
        'url',
        'jsonschema',
        'rdflib',
        'sparqlquery',
        'requests>=2.0',
        'normality',
        'pyyaml',
        'six'
    ],
    tests_require=[
        'nose',
        'coverage',
        'wheel',
        'unicodecsv'
    ]
)
