from setuptools import setup

setup(
    name='topper',
    author='Baptiste Azéma',
    author_email='baptiste@azema.tech',
    version='1.1.1',
    packages=['topper', 'topper.utils'],
    package_data={'topper.resources': ['*.json']},
    include_package_data=True,
    description='An application computing top songs by country or user_id over 7 days',
    license='LICENSE',
    entry_points={
        'console_scripts': ['topper=topper.__main__:main']
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
