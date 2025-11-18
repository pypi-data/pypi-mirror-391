"""Test suite for the ManualFupi class."""

import sys
import tempfile
import os
from pathlib import Path

from fupi import ManualFupi, DEFAULT_ADD_DIR_NAMES, DEFAULT_SKIP_DIR_PATTERNS


class TestManualFupiClass:
    """Test the ManualFupi class API and behavior."""
    
    def test_manual_fupi_instantiation(self):
        """Test that ManualFupi can be instantiated with defaults."""
        mf = ManualFupi()
        assert mf.add_dir_names == DEFAULT_ADD_DIR_NAMES
        assert mf.skip_dir_patterns == DEFAULT_SKIP_DIR_PATTERNS
    
    def test_manual_fupi_defaults_not_shared(self):
        """Test that each instance has independent copies of default lists."""
        mf1 = ManualFupi()
        mf2 = ManualFupi()
        
        # Modify mf1's lists
        mf1.add_dir_names.append('extra_dir')
        mf1.skip_dir_patterns.append('extra_pattern')
        
        # mf2 should still have original defaults
        assert mf2.add_dir_names == DEFAULT_ADD_DIR_NAMES
        assert mf2.skip_dir_patterns == DEFAULT_SKIP_DIR_PATTERNS
        assert 'extra_dir' not in mf2.add_dir_names
        assert 'extra_pattern' not in mf2.skip_dir_patterns
    
    def test_manual_fupi_set_attributes(self):
        """Test setting attributes on ManualFupi instance."""
        mf = ManualFupi()
        mf.add_dir_names = ['custom_src', 'custom_test']
        mf.skip_dir_patterns = ['custom_skip']
        
        assert mf.add_dir_names == ['custom_src', 'custom_test']
        assert mf.skip_dir_patterns == ['custom_skip']
    
    def test_manual_fupi_run_with_attributes(self):
        """Test that run() uses instance attributes when no parameters provided."""
        original_path_len = len(sys.path)
        
        mf = ManualFupi()
        mf.add_dir_names = ['src']
        mf.skip_dir_patterns = ['build', 'dist']
        
        result = mf.run()
        
        # Result should be a list of paths
        assert isinstance(result, list)
    
    def test_manual_fupi_run_with_parameters(self):
        """Test that run() accepts and uses parameters."""
        mf = ManualFupi()
        original_dir_names = mf.add_dir_names.copy()
        
        result = mf.run(add_dir_names=['test_src'], skip_dir_patterns=['test_skip'])
        
        # Parameters should override instance attributes
        assert mf.add_dir_names == ['test_src']
        assert mf.skip_dir_patterns == ['test_skip']
        assert mf.add_dir_names != original_dir_names
        # Result should be a list of paths
        assert isinstance(result, list)
    
    def test_manual_fupi_run_partial_parameters(self):
        """Test that run() can accept only some parameters."""
        mf = ManualFupi()
        mf.add_dir_names = ['original_src']
        mf.skip_dir_patterns = ['original_skip']
        
        # Only override add_dir_names
        result = mf.run(add_dir_names=['new_src'])
        
        assert mf.add_dir_names == ['new_src']
        # Skip patterns should remain unchanged
        assert mf.skip_dir_patterns == ['original_skip']
    
    def test_manual_fupi_multiple_runs(self):
        """Test that ManualFupi can be run multiple times with different configs."""
        mf = ManualFupi()
        
        # First run
        result1 = mf.run(add_dir_names=['src'], skip_dir_patterns=['venv*'])
        len_1 = len(result1)
        
        # Second run
        result2 = mf.run(add_dir_names=['test'], skip_dir_patterns=['build'])
        len_2 = len(result2)
        
        # Both results should be lists
        assert isinstance(result1, list)
        assert isinstance(result2, list)
    
    def test_manual_fupi_returns_sys_path_history(self):
        """Test that run() returns a list of paths that were added."""
        mf = ManualFupi()
        result = mf.run(add_dir_names=['src'])
        
        # Result should be a list of Path objects
        assert isinstance(result, list)
    
    def test_manual_fupi_get_paths_preview(self):
        """Test that get_paths() returns paths without modifying sys.path."""
        original_cwd = os.getcwd()
        original_path_len = len(sys.path)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                (Path(tmpdir) / 'test').mkdir()
                
                mf = ManualFupi()
                # get_paths should not modify sys.path
                paths = mf.get_paths(['src', 'test'], ['venv*'])
                
                assert len(sys.path) == original_path_len
                assert isinstance(paths, list)
        finally:
            os.chdir(original_cwd)
    
    def test_manual_fupi_get_paths_uses_attributes(self):
        """Test that get_paths() uses instance attributes when no parameters provided."""
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                (Path(tmpdir) / 'src').mkdir()
                
                mf = ManualFupi()
                mf.add_dir_names = ['src']
                
                paths = mf.get_paths()
                
                assert isinstance(paths, list)
        finally:
            os.chdir(original_cwd)
    
    def test_environment_variable_extension(self):
        """Test that FUPI_ADD_DIR_NAMES and FUPI_SKIP_DIR_PATTERNS extend defaults."""
        # Save original env vars
        original_add = os.getenv('FUPI_ADD_DIR_NAMES')
        original_skip = os.getenv('FUPI_SKIP_DIR_PATTERNS')
        
        try:
            # Set environment variables
            os.environ['FUPI_ADD_DIR_NAMES'] = 'custom_src,custom_app'
            os.environ['FUPI_SKIP_DIR_PATTERNS'] = 'custom_build,custom_dist'
            
            # Create new instance - should pick up env vars
            mf = ManualFupi()
            
            # Verify defaults are included
            assert 'src' in mf.add_dir_names
            assert 'app' in mf.add_dir_names
            
            # Verify env vars are appended
            assert 'custom_src' in mf.add_dir_names
            assert 'custom_app' in mf.add_dir_names
            
            # Verify skip patterns
            assert 'setup' in mf.skip_dir_patterns
            assert 'venv*' in mf.skip_dir_patterns
            assert 'custom_build' in mf.skip_dir_patterns
            assert 'custom_dist' in mf.skip_dir_patterns
        finally:
            # Restore original env vars
            if original_add is None:
                os.environ.pop('FUPI_ADD_DIR_NAMES', None)
            else:
                os.environ['FUPI_ADD_DIR_NAMES'] = original_add
            
            if original_skip is None:
                os.environ.pop('FUPI_SKIP_DIR_PATTERNS', None)
            else:
                os.environ['FUPI_SKIP_DIR_PATTERNS'] = original_skip
    
    def test_environment_variable_with_simple_values(self):
        """Test that environment variables with simple comma-separated values work."""
        original_add = os.getenv('FUPI_ADD_DIR_NAMES')
        
        try:
            # Set env var with simple comma-separated values
            os.environ['FUPI_ADD_DIR_NAMES'] = 'custom_src,custom_app'
            
            mf = ManualFupi()
            
            # Verify values are added
            assert 'custom_src' in mf.add_dir_names
            assert 'custom_app' in mf.add_dir_names
        finally:
            if original_add is None:
                os.environ.pop('FUPI_ADD_DIR_NAMES', None)
            else:
                os.environ['FUPI_ADD_DIR_NAMES'] = original_add
    
    def test_init_with_add_dir_names_parameter(self):
        """Test that ManualFupi can be initialized with add_dir_names parameter."""
        mf = ManualFupi(add_dir_names=['custom_src', 'custom_lib'])
        assert mf.add_dir_names == ['custom_src', 'custom_lib']
        assert mf.skip_dir_patterns == DEFAULT_SKIP_DIR_PATTERNS
    
    def test_init_with_skip_dir_patterns_parameter(self):
        """Test that ManualFupi can be initialized with skip_dir_patterns parameter."""
        mf = ManualFupi(skip_dir_patterns=['custom_skip', 'temp*'])
        assert mf.add_dir_names == DEFAULT_ADD_DIR_NAMES
        assert mf.skip_dir_patterns == ['custom_skip', 'temp*']
    
    def test_init_with_both_parameters(self):
        """Test that ManualFupi can be initialized with both parameters."""
        mf = ManualFupi(
            add_dir_names=['src', 'lib'],
            skip_dir_patterns=['build', 'dist']
        )
        assert mf.add_dir_names == ['src', 'lib']
        assert mf.skip_dir_patterns == ['build', 'dist']
    
    def test_init_parameters_extend_with_environment_variables(self):
        """Test that init parameters extend with environment variables."""
        original_add = os.getenv('FUPI_ADD_DIR_NAMES')
        
        try:
            os.environ['FUPI_ADD_DIR_NAMES'] = 'env_src,env_lib'
            
            mf = ManualFupi(add_dir_names=['param_src'])
            
            # Should have both the parameter and the environment variable
            assert 'param_src' in mf.add_dir_names
            assert 'env_src' in mf.add_dir_names
            assert 'env_lib' in mf.add_dir_names
        finally:
            if original_add is None:
                os.environ.pop('FUPI_ADD_DIR_NAMES', None)
            else:
                os.environ['FUPI_ADD_DIR_NAMES'] = original_add
    
    def test_init_empty_lists_use_defaults(self):
        """Test that empty lists in init parameters use defaults instead."""
        # When empty lists are passed, defaults should be used
        mf = ManualFupi(add_dir_names=[], skip_dir_patterns=[])
        assert mf.add_dir_names == DEFAULT_ADD_DIR_NAMES
        assert mf.skip_dir_patterns == DEFAULT_SKIP_DIR_PATTERNS


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
