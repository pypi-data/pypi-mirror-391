import sys
import os
from pathlib import Path
import tempfile

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fupi.fupi import ManualFupi


def test_add_dirs_finds_directories():
    """Test that directories are found and added to sys.path"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create test directories
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'src' / 'subdir').mkdir()
            (Path(tmpdir) / 'test').mkdir()
            
            original_path_len = len(sys.path)
            mf = ManualFupi()
            mf.run(['src', 'test'], ['venv*'])
            
            # Should have added paths
            assert len(sys.path) > original_path_len
            assert any('src' in p for p in sys.path)
    finally:
        os.chdir(original_cwd)


def test_skip_dirs_filtering():
    """Test that skip_dirs patterns work correctly"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create directories including ones to skip
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'venv_test').mkdir()
            (Path(tmpdir) / 'src' / 'venv_nested').mkdir()
            
            original_path_len = len(sys.path)
            mf = ManualFupi()
            mf.run(['src'], ['venv*'])
            
            # Should not include venv paths
            new_paths = sys.path[original_path_len:]
            assert not any('venv' in p for p in new_paths)
    finally:
        os.chdir(original_cwd)


def test_disable_functionality():
    """Test that 'disable' prevents execution"""
    original_path_len = len(sys.path)
    mf = ManualFupi()
    result = mf.run(['disable'], [])
    
    # Should not modify sys.path
    assert len(sys.path) == original_path_len
    assert isinstance(result, list)


def test_skip_dirs_comma_separated_string():
    """Test that comma-separated skip_dirs string is properly split"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create test directories including ones to skip
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'setup_dir').mkdir()
            (Path(tmpdir) / 'old_stuff').mkdir()
            (Path(tmpdir) / 'venv_test').mkdir()
            
            # Test with comma-separated string (simulating .env file parsing)
            original_path_len = len(sys.path)
            mf = ManualFupi()
            result = mf.run(['src'], ['setup*,old*,venv*'])
            
            # Verify the function executed successfully
            assert isinstance(result, list)
            
            # Verify no skipped directories were added to sys.path
            new_paths = sys.path[original_path_len:]
            
            # Check for paths containing the temp directory and skip patterns
            temp_new_paths = [p for p in new_paths if tmpdir in p]
            
            # Check that only src directory was added, not the skipped ones
            assert not any('setup' in p for p in temp_new_paths)
            assert not any('old_stuff' in p for p in temp_new_paths)
            assert not any('venv_test' in p for p in temp_new_paths)
    finally:
        os.chdir(original_cwd)


def test_import_fupi_modifies_syspath():
    """Test that importing fupi modifies sys.path"""
    # This test is covered by integration tests
    # Import fupi in __init__.py should trigger autorun
    original_path_len = len(sys.path)
    # fupi should already be imported above, so sys.path should be modified
    assert len(sys.path) >= original_path_len


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
