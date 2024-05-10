from setuptools import setup


setup(
    name='vernacular',
    install_requires = [
        'frozendict',
        'pyhamcrest',
        'langcodes',
        'polib',
    ],
    extras_require={
        'test': [
            'WebTest',
            'pytest',
        ]
    }
)
