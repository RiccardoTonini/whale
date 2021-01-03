from os import path
import setuptools
from setuptools import find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="whale-pipelines",
    version="1.3.3",
    author="Robert Yi",
    author_email="robert@ryi.me",
    description="A pared-down metadata scraper + SQL runner.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dataframehq/whale",
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "aadict",
        "amundsen-databuilder",
        "asn1crypto",
        "asset",
        "azure-common",
        "azure-core",
        "azure-storage-blob",
        "boto3",
        "botocore",
        "cachetools",
        "certifi",
        "cffi",
        "chardet",
        "colored",
        "cryptography",
        "elasticsearch",
        "future",
        "globre",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "google-cloud-bigquery",
        "google-cloud-core",
        "google-cloud-datacatalog",
        "google-cloud-spanner",
        "google-crc32c",
        "google-resumable-media",
        "googleapis-common-protos",
        "grpcio",
        "grpcio-gcp",
        "httplib2",
        "idna",
        "isodate",
        "Jinja2",
        "jmespath",
        "msrest",
        "neo4j-driver",
        "neobolt",
        "neotime",
        "numpy",
        "oauthlib",
        "oscrypto",
        "pandas",
        "proto-plus",
        "protobuf",
        "psycopg2-binary",
        "pyasn1",
        "pyasn1-modules",
        "pybigquery",
        "pycparser",
        "pycryptodomex",
        "PyHive",
        "pyhocon",
        "PyJWT",
        "pyOpenSSL",
        "pyparsing",
        "python-dateutil",
        "pytz",
        "PyYAML",
        "requests",
        "requests-oauthlib",
        "retrying",
        "rsa",
        "s3transfer",
        "six",
        "snowflake-connector-python",
        "snowflake-sqlalchemy",
        "SQLAlchemy",
        "statsd",
        "termcolor",
        "Unidecode",
        "uritemplate",
        "urllib3",
    ],
    include_package_data=True,
)
