from setuptools import setup


setup(
    name='em_tools',
    install_requires=[
        'raven',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
