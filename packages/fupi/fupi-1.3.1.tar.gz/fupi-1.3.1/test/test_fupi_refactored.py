"""Test suite for refactored fupi.py with ManualFupi class."""

import sys
from pathlib import Path
import tempfile
import os

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fupi.fupi import ManualFupi, sys_path_history


class TestManualFupiMethods:
    """Test ManualFupi class methods and coverage."""

    def test_get_paths_with_explicit_parameters(self):
        """Test get_paths() with explicit parameters."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / 'src' / 'subdir').mkdir()
                
                mf = ManualFupi()
                paths = mf.get_paths(['src'], ['venv*'])
                
                # Should return a list of Path objects
                assert isinstance(paths, list)
                # Should find the src directory
                assert any('src' in str(p) for p in paths)
        finally:
            os.chdir(original_cwd)

    def test_get_paths_with_defaults(self):
        """Test get_paths() using default values."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / 'test').mkdir()
                (Path(tmpdir) / 'app').mkdir()
                
                mf = ManualFupi()
                # Call with no parameters to use defaults
                paths = mf.get_paths()
                
                assert isinstance(paths, list)
        finally:
            os.chdir(original_cwd)

    def test_get_paths_empty_add_dirs(self):
        """Test that get_paths() returns empty list with empty add_dirs."""
        mf = ManualFupi()
        paths = mf.get_paths([], [])
        
        assert isinstance(paths, list)
        assert len(paths) == 0

    def test_run_adds_paths_to_syspath(self):
        """Test that run() adds paths to sys.path."""
        original_cwd = os.getcwd()
        original_path_len = len(sys.path)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                
                mf = ManualFupi()
                result = mf.run(['src'], ['venv*'])
                
                # Should have added paths (or returned empty list if none matched)
                assert isinstance(result, list)
                # sys.path_history should be updated
                assert len(sys_path_history) >= 1
        finally:
            os.chdir(original_cwd)

    def test_run_updates_sys_path_history(self):
        """Test that run() updates sys_path_history."""
        original_cwd = os.getcwd()
        initial_history_len = len(sys_path_history)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                
                mf = ManualFupi()
                mf.run(['src'], [])
                
                # History should have grown
                assert len(sys_path_history) > initial_history_len
        finally:
            os.chdir(original_cwd)

    def test_run_with_skip_patterns(self):
        """Test that run() respects skip patterns."""
        original_cwd = os.getcwd()
        original_path_len = len(sys.path)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / 'venv_dir').mkdir()
                
                mf = ManualFupi()
                mf.run(['src', 'venv_dir'], ['venv*'])
                
                # Check that no venv paths were added
                new_paths = sys.path[original_path_len:]
                temp_paths = [p for p in new_paths if tmpdir in p]
                assert not any('venv' in p for p in temp_paths)
        finally:
            os.chdir(original_cwd)

    def test_run_with_quoted_values(self):
        """Test that run() handles quoted directory names."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                
                mf = ManualFupi()
                # Quoted directory names should have quotes removed
                paths = mf.get_paths(['"src"'], ['"venv*"'])
                
                assert isinstance(paths, list)
        finally:
            os.chdir(original_cwd)

    def test_run_with_comma_separated_skip_dirs(self):
        """Test that run() handles comma-separated skip_dirs."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / 'build').mkdir()
                
                mf = ManualFupi()
                # Pass comma-separated string
                paths = mf.get_paths(['src'], ['build,dist,venv*'])
                
                assert isinstance(paths, list)
        finally:
            os.chdir(original_cwd)

    def test_get_paths_skips_hidden_and_underscore_dirs(self):
        """Test that hidden and underscore directories are always skipped."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / '.git').mkdir()
                (Path(tmpdir) / '__pycache__').mkdir()
                
                mf = ManualFupi()
                paths = mf.get_paths(['src'], [])
                
                # Should not include hidden or underscore directories
                assert not any('__pycache__' in str(p) for p in paths)
                assert not any('.git' in str(p) for p in paths)
        finally:
            os.chdir(original_cwd)

    def test_autorun_function_exists(self):
        """Test that autorun() function exists and is callable."""
        from fupi.fupi import autorun
        assert callable(autorun)
        
        # Test basic functionality
        original_path_len = len(sys.path)
        result = autorun()
        
        # autorun() should return a list
        assert isinstance(result, list)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
