from setuptools import setup


setup(
    name='em_tools',
    install_requires=[
        'raven',
        'prometheus_client',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
