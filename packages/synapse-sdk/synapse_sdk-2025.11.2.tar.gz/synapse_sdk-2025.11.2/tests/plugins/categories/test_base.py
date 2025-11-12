"""Tests for Action.plugin_url property with HTTP → Ray GCS conversion."""

from unittest.mock import Mock, patch

import pytest


class TestActionPluginUrl:
    """Test suite for Action.plugin_url property."""

    @pytest.fixture
    def mock_action(self):
        """Create a mock Action instance."""
        action = Mock()
        action.debug = False
        action.plugin_release = Mock()
        action.plugin_storage_url = 'http://django.local/media/'
        action.envs = {}
        return action

    # Debug mode tests (existing behavior)

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_https(self, mock_archive, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with https:// URL returns unchanged."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'https://example.com/plugin.zip'}

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'https://example.com/plugin.zip'
        mock_archive.assert_not_called()

    @patch('synapse_sdk.plugins.categories.base.download_and_upload')
    def test_plugin_url_debug_http(self, mock_download_upload, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with http:// URL calls download_and_upload."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'http://example.com/plugin.zip'}
        mock_download_upload.return_value = 's3://bucket/uploaded.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/uploaded.zip'
        mock_download_upload.assert_called_once_with('http://example.com/plugin.zip', mock_action.plugin_storage_url)

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_local_path(self, mock_archive, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with local path calls archive_and_upload."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': '/local/path/to/plugin'}
        mock_archive.return_value = 's3://bucket/archived.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/archived.zip'
        mock_archive.assert_called_once_with('/local/path/to/plugin', mock_action.plugin_storage_url)

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_default_path(self, mock_archive, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH defaults to current directory."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {}  # No SYNAPSE_DEBUG_PLUGIN_PATH set
        mock_archive.return_value = 's3://bucket/archived.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/archived.zip'
        mock_archive.assert_called_once_with('.', mock_action.plugin_storage_url)

    # Production mode tests (new behavior)

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_http_converts_to_gcs(self, mock_convert, mock_action):
        """Test that HTTP URLs are converted to Ray GCS in production mode."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/abc123.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_xyz789.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gcs://_ray_pkg_xyz789.zip'
        mock_convert.assert_called_once_with('http://django.local/media/plugins/abc123.zip')

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_https_converts_to_gcs(self, mock_convert, mock_action):
        """Test that HTTPS URLs are converted to Ray GCS in production mode."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'https://django.local/media/plugins/abc123.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_xyz789.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gcs://_ray_pkg_xyz789.zip'
        mock_convert.assert_called_once_with('https://django.local/media/plugins/abc123.zip')

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_s3_no_conversion(self, mock_convert, mock_action):
        """Test that s3:// URLs are not converted (already Ray-compatible)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 's3://my-bucket/plugins/abc123.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://my-bucket/plugins/abc123.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_gs_no_conversion(self, mock_convert, mock_action):
        """Test that gs:// URLs are not converted (already Ray-compatible)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'gs://my-bucket/plugins/abc123.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gs://my-bucket/plugins/abc123.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_gcs_no_conversion(self, mock_convert, mock_action):
        """Test that gcs:// URLs are not converted (already Ray GCS format)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'gcs://_ray_pkg_existing.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gcs://_ray_pkg_existing.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_conversion_called_with_correct_url(self, mock_convert, mock_action):
        """Test that convert_http_to_ray_gcs is called with the exact URL from storage."""
        # Arrange
        expected_url = 'http://custom-domain.com/media/special/plugin-v2.0.zip'
        mock_action.plugin_release.get_url.return_value = expected_url
        mock_convert.return_value = 'gcs://_ray_pkg_custom.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gcs://_ray_pkg_custom.zip'
        mock_convert.assert_called_once_with(expected_url)

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_multiple_calls_caching(self, mock_convert, mock_action):
        """Test that plugin_url can be called multiple times (property behavior)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/test.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_test.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url1 = Action.plugin_url.fget(mock_action)
        url2 = Action.plugin_url.fget(mock_action)

        # Assert
        assert url1 == 'gcs://_ray_pkg_test.zip'
        assert url2 == 'gcs://_ray_pkg_test.zip'
        # Should be called twice since it's a property, not cached
        assert mock_convert.call_count == 2

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_conversion_error_propagates(self, mock_convert, mock_action):
        """Test that errors from convert_http_to_ray_gcs propagate correctly."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/test.zip'
        mock_convert.side_effect = RuntimeError('Ray not initialized')

        # Act & Assert
        from synapse_sdk.plugins.categories.base import Action

        with pytest.raises(RuntimeError) as exc_info:
            Action.plugin_url.fget(mock_action)

        assert 'Ray not initialized' in str(exc_info.value)

    def test_plugin_url_production_calls_get_url_with_storage_url(self, mock_action):
        """Test that plugin_release.get_url is called with plugin_storage_url."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 's3://bucket/plugin.zip'
        expected_storage_url = 'http://custom-storage.local/path/'
        mock_action.plugin_storage_url = expected_storage_url

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/plugin.zip'
        mock_action.plugin_release.get_url.assert_called_once_with(expected_storage_url)
