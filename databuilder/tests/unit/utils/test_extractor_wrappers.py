import google
import googleapiclient
import google_auth_httplib2
import http

from mock import patch

from databuilder import Scoped
from whalebuilder.models.connection_config import ConnectionConfigSchema
from whalebuilder.engine.sql_alchemy_engine import SQLAlchemyEngine
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from whalebuilder.extractor.bigquery_metadata_extractor import BaseBigQueryExtractor
from whalebuilder.utils.extractor_wrappers import \
    configure_bigquery_extractors, \
    configure_neo4j_extractors, \
    configure_presto_extractors
from databuilder.extractor.neo4j_extractor import Neo4jExtractor

TEST_PRESTO_CONNECTION_CONFIG = ConnectionConfigSchema(
    name='test_connection',
    username='mock_username',
    password='mock_password',
    uri='mock_uri',
    port='9999',
    metadata_source='presto',
    cluster='mock_cluster',
    included_schemas='mock_schema_included',
    excluded_schemas='mock_schema_excluded',
)

TEST_BIGQUERY_CONNECTION_CONFIG = ConnectionConfigSchema(
    metadata_source='bigquery',
    key_path='mock_key_path',
    project_id='mock_project_id',
    page_size=10,
    filter_key='mock_filter_key'
)

TEST_NEO4J_CONNECTION_CONFIG = ConnectionConfigSchema(
    name='test_connection',
    username='mock_username',
    password='mock_password',
    uri='mock_uri',
    port='9999',
    metadata_source='presto',
    cluster='mock_cluster',
    included_keys=['mock_key_included'],
    excluded_keys=['mock_key_excluded'],
)


# @patch.object(SQLAlchemyEngine, '_get_connection')
@patch.object(SQLAlchemyExtractor, '_execute_query')
def test_configure_presto_extractor(mock_settings):
    """
    Test that the extractor can initialize.
    """
    extractors, conf = \
        configure_presto_extractors(TEST_PRESTO_CONNECTION_CONFIG)
    extractor = extractors[0]
    scoped_conf = Scoped.get_scoped_conf(conf, extractor.get_scope())
    assert extractor.init(scoped_conf) == None


@patch.object(BaseBigQueryExtractor, 'init')
def test_configure_bigquery_extractor(*mock_settings):
    """
    Test that the extractor can initialize.
    """
    extractors, conf = \
        configure_bigquery_extractors(TEST_BIGQUERY_CONNECTION_CONFIG)
    extractor = extractors[0]
    scoped_conf = Scoped.get_scoped_conf(conf, extractor.get_scope())
    assert extractor.init(scoped_conf) == None


@patch.object(Neo4jExtractor, '_get_driver')
def test_configure_neo4j_extractor(mock_settings):
    """
    Test that the extractor can initialize.
    """
    extractors, conf = \
        configure_neo4j_extractors(TEST_NEO4J_CONNECTION_CONFIG)
    extractor = extractors[0]
    scoped_conf = Scoped.get_scoped_conf(conf, extractor.get_scope())
    assert extractor.init(scoped_conf) == None