from setuptools import setup


setup(
    name='vernacular',
    install_requires = [
        'frozendict',
        'pyhamcrest',
    ],
    extras_require={
        'test': [
            'WebTest',
            'pytest',
        ]
    }
)
