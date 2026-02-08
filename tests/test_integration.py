"""Integration tests for lic-cli end-to-end workflows."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock
import httpx
from lic_cli.cli import main


@pytest.mark.integration
class TestMainWorkflow:
    """Integration tests for the main CLI workflow."""
    
    def test_main_with_all_args(self, httpx_mock, mock_mit_license_body, temp_license_dir):
        """Test main workflow with all arguments provided."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            # Mock the license fetch
            httpx_mock.add_response(
                url="https://api.github.com/licenses/mit",
                json={"key": "mit", "body": mock_mit_license_body}
            )
            
            # Run with command-line arguments
            with patch.object(sys, 'argv', ['lic', '-l', 'mit', '-a', 'John Doe', '-y', '2024']):
                main()
            
            # Verify LICENSE file was created
            license_file = Path("LICENSE")
            assert license_file.exists()
            
            content = license_file.read_text()
            assert "MIT License" in content
            assert "2024" in content
            assert "John Doe" in content
            assert "[year]" not in content
            assert "[fullname]" not in content
        finally:
            os.chdir(original_cwd)
    
    def test_main_with_license_arg_only(self, httpx_mock, mock_mit_license_body, temp_license_dir):
        """Test main workflow with only license argument."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            httpx_mock.add_response(
                url="https://api.github.com/licenses/mit",
                json={"key": "mit", "body": mock_mit_license_body}
            )
            
            with patch.object(sys, 'argv', ['lic', '-l', 'mit']), \
                 patch('questionary.text') as mock_text, \
                 patch('lic_cli.cli.get_git_name', return_value=None):
                
                # Mock interactive inputs
                mock_text.return_value.ask.side_effect = ["Jane Smith", "2025"]
                
                main()
            
            license_file = Path("LICENSE")
            assert license_file.exists()
            
            content = license_file.read_text()
            assert "Jane Smith" in content
            assert "2025" in content
        finally:
            os.chdir(original_cwd)
    
    def test_main_interactive_mode(self, httpx_mock, mock_licenses_response, mock_mit_license_body, temp_license_dir):
        """Test main workflow in fully interactive mode."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            # Mock licenses list
            httpx_mock.add_response(
                url="https://api.github.com/licenses",
                json=mock_licenses_response
            )
            
            # Mock specific license
            httpx_mock.add_response(
                url="https://api.github.com/licenses/mit",
                json={"key": "mit", "body": mock_mit_license_body}
            )
            
            with patch.object(sys, 'argv', ['lic']), \
                 patch('questionary.select') as mock_select, \
                 patch('questionary.text') as mock_text, \
                 patch('lic_cli.cli.get_git_name', return_value="Git User"):
                
                # Mock license selection
                mock_select.return_value.ask.return_value = "MIT License"
                
                # Mock author and year inputs
                mock_text.return_value.ask.side_effect = ["Git User", "2024"]
                
                main()
            
            license_file = Path("LICENSE")
            assert license_file.exists()
            
            content = license_file.read_text()
            assert "Git User" in content
            assert "2024" in content
        finally:
            os.chdir(original_cwd)
    
    def test_main_cancelled_license_selection(self, httpx_mock, mock_licenses_response, capsys):
        """Test main workflow when user cancels license selection."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses",
            json=mock_licenses_response
        )
        
        with patch.object(sys, 'argv', ['lic']), \
             patch('questionary.select') as mock_select:
            
            # User cancels selection
            mock_select.return_value.ask.return_value = None
            
            main()
            
            # No exception should be raised
            captured = capsys.readouterr()
            # Should show cancelled message
    
    def test_main_keyboard_interrupt(self, httpx_mock, mock_licenses_response, capsys):
        """Test main workflow handles Ctrl+C gracefully."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses",
            json=mock_licenses_response
        )
        
        with patch.object(sys, 'argv', ['lic']), \
             patch('questionary.select') as mock_select:
            
            # Simulate Ctrl+C
            mock_select.return_value.ask.side_effect = KeyboardInterrupt()
            
            main()
            
            # Should handle gracefully without crashing


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling scenarios."""
    
    def test_main_api_error(self, httpx_mock):
        """Test main workflow when API returns error."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses",
            status_code=500
        )
        
        with patch.object(sys, 'argv', ['lic']), \
             pytest.raises(SystemExit) as exc_info:
            
            main()
        
        assert exc_info.value.code == 1
    
    def test_main_network_timeout(self, httpx_mock):
        """Test main workflow when network times out."""
        httpx_mock.add_exception(
            httpx.TimeoutException("Connection timeout")
        )
        
        with patch.object(sys, 'argv', ['lic']), \
             pytest.raises(SystemExit) as exc_info:
            
            main()
        
        assert exc_info.value.code == 1
    
    def test_main_invalid_license_key(self, httpx_mock):
        """Test main workflow with invalid license key."""
        httpx_mock.add_response(
            url="https://api.github.com/licenses/invalid",
            status_code=404
        )
        
        with patch.object(sys, 'argv', ['lic', '-l', 'invalid', '-a', 'Test', '-y', '2024']), \
             pytest.raises(SystemExit) as exc_info:
            
            main()
        
        assert exc_info.value.code == 1


@pytest.mark.integration
class TestArgumentParsing:
    """Integration tests for command-line argument parsing."""
    
    def test_help_argument(self):
        """Test --help argument."""
        with patch.object(sys, 'argv', ['lic', '--help']), \
             pytest.raises(SystemExit) as exc_info:
            
            main()
        
        # --help should exit with code 0
        assert exc_info.value.code == 0
    
    def test_license_short_arg(self, httpx_mock, mock_mit_license_body, temp_license_dir):
        """Test -l short argument for license."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            httpx_mock.add_response(
                url="https://api.github.com/licenses/apache-2.0",
                json={"key": "apache-2.0", "body": "Apache License\n\nCopyright [yyyy] [name of copyright owner]"}
            )
            
            with patch.object(sys, 'argv', ['lic', '-l', 'apache-2.0', '-a', 'Test User', '-y', '2024']):
                main()
            
            assert Path("LICENSE").exists()
        finally:
            os.chdir(original_cwd)
    
    def test_author_short_arg(self, httpx_mock, mock_mit_license_body, temp_license_dir):
        """Test -a short argument for author."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            httpx_mock.add_response(
                url="https://api.github.com/licenses/mit",
                json={"key": "mit", "body": mock_mit_license_body}
            )
            
            with patch.object(sys, 'argv', ['lic', '-l', 'mit', '-a', 'Short Arg Test', '-y', '2024']):
                main()
            
            content = Path("LICENSE").read_text()
            assert "Short Arg Test" in content
        finally:
            os.chdir(original_cwd)
    
    def test_year_short_arg(self, httpx_mock, mock_mit_license_body, temp_license_dir):
        """Test -y short argument for year."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_license_dir)
        
        try:
            httpx_mock.add_response(
                url="https://api.github.com/licenses/mit",
                json={"key": "mit", "body": mock_mit_license_body}
            )
            
            with patch.object(sys, 'argv', ['lic', '-l', 'mit', '-a', 'Year Test', '-y', '2030']):
                main()
            
            content = Path("LICENSE").read_text()
            assert "2030" in content
        finally:
            os.chdir(original_cwd)
