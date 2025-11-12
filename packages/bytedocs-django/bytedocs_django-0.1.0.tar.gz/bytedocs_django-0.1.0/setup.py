"""
ByteDocs Django - Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read README
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='bytedocs-django',
    version='0.1.0',
    author='ByteDocs Team',
    author_email='support@bytedocs.com',
    description='Beautiful API documentation for Django - Alternative to Swagger/Scramble',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/bytedocs/bytedocs-django',
    packages=find_packages(exclude=['examples', 'tests', 'venv']),
    include_package_data=True,
    package_data={
        'bytedocs_django': [
            'ui/templates/*.html',
            'ui/templates/auth/*.html',
        ],
    },
    install_requires=[
        'Django>=3.2',
        'pyyaml>=6.0',
        'python-dotenv>=1.0.0',
    ],
    extras_require={
        'ai': [
            'openai>=2.0.0',
            'google-generativeai>=0.8.0',
            'anthropic>=0.70.0',
        ],
        'drf': [
            'djangorestframework>=3.14.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-django>=4.5.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    keywords='django api documentation swagger openapi rest-framework bytedocs',
    project_urls={
        'Bug Reports': 'https://github.com/bytedocs/bytedocs-django/issues',
        'Source': 'https://github.com/bytedocs/bytedocs-django',
        'Documentation': 'https://docs.bytedocs.com',
    },
)
