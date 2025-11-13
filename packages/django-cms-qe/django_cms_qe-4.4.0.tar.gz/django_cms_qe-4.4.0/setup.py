import setuptools


setuptools.setup(
    name='django-cms-qe',
    version='4.4.0',
    packages=setuptools.find_packages(exclude=[
        '*.tests',
        '*.tests.*',
        'tests.*',
        'tests',
        'test_utils.*',
        'test_utils',
        '*.migrations',
        '*.migrations.*',
        'example.*',
        'example',
    ]),
    include_package_data=True,
    description=(
        'Django CMS Quick & Easy provides all important modules to run new page without'
        'a lot of coding. Aims to do it very easily and securely.'
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://websites.pages.nic.cz/django-cms-qe',
    author='CZ.NIC, z.s.p.o.',
    author_email='kontakt@nic.cz',
    license='BSD License',

    python_requires='>=3.10',  # https://github.com/django/django/blob/5.2.1/pyproject.toml#L8
    install_requires=[
        # Essential for Django CMS
        'django-cms>=4.1,<6',
        'django-filer~=3.3',
        'djangocms-admin-style~=3.3',
        'djangocms-alias>=2.0,<4',
        'djangocms-frontend~=2.2',
        'djangocms-text~=0.9',
        'djangocms-versioning~=2.4',
        'easy-thumbnails[svg]~=2.10',

        # Additional functionality
        'argon2-cffi~=25.1',
        'django-axes~=8.0',
        'django-constance~=4.3',
        'django-csp~=4.0',
        'django-import-export~=4.3',
        'django-tablib~=3.2',
        'djangocms-file~=3.0',
        'djangocms-deleted-pages~=1.0',
        'djangocms-googlemap~=2.2',
        'djangocms-icon~=2.1',
        'djangocms-link~=5.1',
        'djangocms-picture~=4.1',
        'python-environ~=0.4',

        # Forms and search
        'django-haystack~=3.3',
        'djangocms-aldryn-forms[captcha]~=8.3',
        'djangocms-aldryn-search~=3.1',
        'mailchimp3~=3.0',
        'whoosh~=2.7',

        # REST API
        'Markdown~=3.9',
        'django-filter~=25.2',
        'django-rest-knox~=5.0',
        'djangorestframework~=3.16',
        'drf-spectacular~=0.28',
    ],

    # Do not use test_require or build_require, because then it's not installed and is
    # able to be used only by setup.py util. We want to use it manually.
    # Actually it could be all in dev-requirements.txt but it's good to have it here
    # next to run dependencies and have it separated by purposes.
    extras_require={
        'dev': [
            'django-simple-captcha~=0.6',
            'django-debug-toolbar~=6.0',
            'django-extensions~=4.1',
        ],
        'test': [
            'flake8',
            'isort',
            'mypy',
            'pylint',
            'pylint-django',
            'pytest~=8.4',
            'pytest-cov~=7.0',
            'pytest-data~=0.4',
            'pytest-django~=4.11',
            'pytest-env~=1.2',
            'pytest-pythonpath~=0.7',
            'pytest-sugar~=1.1',
            'pytest-watch~=4.2',
            'PyVirtualDisplay~=3.0',
            'webdriverwrapper~=2.8',
            'django-simple-captcha~=0.6',
            'testfixtures',
            'tzdata',
        ],
        'build': [
            'Jinja2<3.1.0',
            'Sphinx==1.8.5',
        ],
        'psql': [
            'psycopg2',
        ],
        'mysql': [
            'mysqlclient~=2.2',
        ],
        'newsblog': [
            'djangocms-aldryn-newsblog~=4.0',
        ],
        'cms4': [
            'django-cms~=4.1',
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords=['django', 'cms'],
)
