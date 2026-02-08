"""Unit tests for lic-cli core functions."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import httpx
from lic_cli.cli import (
    get_git_name,
    fetch_licenses,
    get_license,
    render_license,
    save_license,
    get_license_key_interactive,
    get_author_input,
    get_year_input,
)


@pytest.mark.unit
class TestGetGitName:
    """Tests for get_git_name function."""
    
    def test_get_git_name_success(self):
        """Test successful git name retrieval."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="John Doe\n"
            )
            result = get_git_name()
            assert result == "John Doe"
            mock_run.assert_called_once()
    
    def test_get_git_name_failure(self):
        """Test git name retrieval when git config fails."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout="")
            result = get_git_name()
            assert result is None
    
    def test_get_git_name_exception(self):
        """Test git name retrieval when subprocess raises exception."""
        with patch('subprocess.run', side_effect=Exception("Git not found")):
            result = get_git_name()
            assert result is None


@pytest.mark.unit
class TestFetchLicenses:
    """Tests for fetch_licenses function."""
    
    def test_fetch_licenses_success(self, httpx_mock, mock_licenses_response):
        """Test successful license fetching."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses",
            json=mock_licenses_response
        )
        
        result = fetch_licenses()
        
        assert isinstance(result, dict)
        assert "mit" in result
        assert "apache-2.0" in result
        assert "gpl-3.0" in result
        assert result["mit"]["name"] == "MIT License"
    
    def test_fetch_licenses_http_error(self, httpx_mock):
        """Test license fetching with HTTP error."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses",
            status_code=500
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            fetch_licenses()
    
    def test_fetch_licenses_timeout(self, httpx_mock):
        """Test license fetching with timeout."""
        httpx_mock.add_exception(
            httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(httpx.TimeoutException):
            fetch_licenses()


@pytest.mark.unit
class TestGetLicense:
    """Tests for get_license function."""
    
    def test_get_license_success(self, httpx_mock, mock_license_response):
        """Test successful single license fetching."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses/mit",
            json=mock_license_response
        )
        
        result = get_license("mit")
        
        assert "MIT License" in result
        assert "[year]" in result
        assert "[fullname]" in result
    
    def test_get_license_not_found(self, httpx_mock):
        """Test license fetching with invalid key."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses/invalid",
            status_code=404
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            get_license("invalid")
    
    def test_get_license_empty_body(self, httpx_mock):
        """Test license response with no body."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses/test",
            json={"key": "test", "name": "Test License"}
        )
        
        result = get_license("test")
        assert result == ""


@pytest.mark.unit
class TestRenderLicense:
    """Tests for render_license function."""
    
    def test_render_license_year_fullname(self, mock_mit_license_body, sample_author, sample_year):
        """Test license rendering with [year] and [fullname] placeholders."""
        result = render_license(mock_mit_license_body, sample_author, sample_year)
        
        assert "[year]" not in result
        assert "[fullname]" not in result
        assert sample_year in result
        assert sample_author in result
    
    def test_render_license_yyyy_copyright_owner(self, mock_apache_license_body, sample_author, sample_year):
        """Test license rendering with [yyyy] and [name of copyright owner] placeholders."""
        result = render_license(mock_apache_license_body, sample_author, sample_year)
        
        assert "[yyyy]" not in result
        assert "[name of copyright owner]" not in result
        assert sample_year in result
        assert sample_author in result
    
    def test_render_license_uppercase_owner(self):
        """Test license rendering with uppercase placeholder."""
        content = "Copyright [NAME OF COPYRIGHT OWNER]"
        result = render_license(content, "Jane Doe", "2025")
        
        assert "[NAME OF COPYRIGHT OWNER]" not in result
        assert "Jane Doe" in result
    
    def test_render_license_no_placeholders(self):
        """Test license rendering with no placeholders."""
        content = "This is a license with no placeholders."
        result = render_license(content, "John Doe", "2024")
        
        assert result == content


@pytest.mark.unit
class TestSaveLicense:
    """Tests for save_license function."""
    
    def test_save_license_creates_file(self, temp_license_dir):
        """Test that save_license creates LICENSE file."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            content = "MIT License\n\nCopyright (c) 2024 John Doe"
            save_license(content)
            
            license_file = Path("LICENSE")
            assert license_file.exists()
            assert license_file.read_text() == content
        finally:
            os.chdir(original_cwd)
    
    def test_save_license_overwrites_existing(self, temp_license_dir):
        """Test that save_license overwrites existing LICENSE file."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            # Create initial file
            Path("LICENSE").write_text("Old content")
            
            # Save new content
            new_content = "New license content"
            save_license(new_content)
            
            assert Path("LICENSE").read_text() == new_content
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestGetLicenseKeyInteractive:
    """Tests for get_license_key_interactive function."""
    
    def test_get_license_key_interactive_success(self, mock_licenses_response):
        """Test interactive license selection."""
        licenses = {lic["key"]: lic for lic in mock_licenses_response}
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "MIT License"
            
            result = get_license_key_interactive(licenses)
            
            assert result == "mit"
            mock_select.assert_called_once()
    
    def test_get_license_key_interactive_cancelled(self, mock_licenses_response):
        """Test interactive license selection when cancelled."""
        licenses = {lic["key"]: lic for lic in mock_licenses_response}
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = None
            
            result = get_license_key_interactive(licenses)
            
            assert result is None


@pytest.mark.unit
class TestGetAuthorInput:
    """Tests for get_author_input function."""
    
    def test_get_author_input_provided(self, sample_author):
        """Test author input when provided as argument."""
        with patch('lic_cli.cli.console') as mock_console:
            result = get_author_input(sample_author)
            
            assert result == sample_author
            mock_console.print.assert_called_once()
    
    def test_get_author_input_interactive_with_git(self):
        """Test interactive author input with git name available."""
        with patch('questionary.text') as mock_text, \
             patch('lic_cli.cli.get_git_name', return_value="Git User"), \
             patch('lic_cli.cli.console'):
            
            mock_text.return_value.ask.return_value = "Interactive User"
            
            result = get_author_input()
            
            assert result == "Interactive User"
            # Verify git name was used as default
            call_kwargs = mock_text.call_args[1]
            assert call_kwargs.get('default') == "Git User"
    
    def test_get_author_input_interactive_without_git(self):
        """Test interactive author input without git name."""
        with patch('questionary.text') as mock_text, \
             patch('lic_cli.cli.get_git_name', return_value=None), \
             patch('lic_cli.cli.console'):
            
            mock_text.return_value.ask.return_value = "Manual User"
            
            result = get_author_input()
            
            assert result == "Manual User"
            call_kwargs = mock_text.call_args[1]
            assert call_kwargs.get('default') == ""


@pytest.mark.unit
class TestGetYearInput:
    """Tests for get_year_input function."""
    
    def test_get_year_input_provided(self, sample_year):
        """Test year input when provided as argument."""
        with patch('lic_cli.cli.console') as mock_console:
            result = get_year_input(sample_year)
            
            assert result == sample_year
            mock_console.print.assert_called_once()
    
    def test_get_year_input_interactive(self, current_year):
        """Test interactive year input."""
        with patch('questionary.text') as mock_text, \
             patch('lic_cli.cli.console'):
            
            mock_text.return_value.ask.return_value = current_year
            
            result = get_year_input()
            
            assert result == current_year
            # Verify current year was used as default
            call_kwargs = mock_text.call_args[1]
            assert call_kwargs.get('default') == current_year
