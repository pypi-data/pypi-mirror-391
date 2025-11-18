from pathlib import Path
import sys, re, os 

# Default configuration lists - accessible for manual configuration and extended via environment variables
DEFAULT_ADD_DIR_NAMES = ['src', 'app', 'main', 'test', 'tests']
DEFAULT_SKIP_DIR_PATTERNS = ['setup', 'venv*', '*egg*', 'old*', '*old', '*bkup', '*backup']

# Environment variables: FUPI_ADD_DIR_NAMES and FUPI_SKIP_DIR_PATTERNS can extend the defaults
# when creating a ManualFupi instance. This allows configuration without code changes.

sys_path_history = [sys.path.copy()]  # Simple list capturing snapshots of sys.path state
autostarted = True  # Flag to track if auto-run was executed (updated in __init__.py)


class ManualFupi:
    """Manual configuration class for fupi path management.
    
    Usage:
        mf = ManualFupi()
        mf.add_dir_names = ['src', 'test']
        mf.skip_dir_patterns = ['venv*', 'build']
        
        # Preview paths before running
        paths = mf.get_paths()
        print(f"Will add {len(paths)} paths to sys.path")
        
        # Execute configuration
        mf.run()
        
        # Or in one call with parameters:
        mf.run(add_dir_names=['src'], skip_dir_patterns=['venv*'])
    """
    add_dir_names: list = []
    skip_dir_patterns: list = []
    
    def __init__(self, add_dir_names=[], skip_dir_patterns=[], autorun: bool = False):
        """Initialize ManualFupi with default configuration.
        
        Configuration can be extended via environment variables:
        - FUPI_ADD_DIR_NAMES: Comma-separated directory names to append to defaults
        - FUPI_SKIP_DIR_PATTERNS: Comma-separated patterns to append to defaults
        
        Environment variables support optional wrapping with quotes/brackets:
        e.g., FUPI_ADD_DIR_NAMES="src,test" or FUPI_ADD_DIR_NAMES=['src','test']
        """
        # Start with copies of defaults (ensures instance independence)
        self.add_dir_names     = add_dir_names     if add_dir_names     else DEFAULT_ADD_DIR_NAMES.copy()
        self.skip_dir_patterns = skip_dir_patterns if skip_dir_patterns else DEFAULT_SKIP_DIR_PATTERNS.copy()

        def unwrap(env_var: str) -> str:
            """Remove wrapping quotes and brackets from environment variable value."""
            fw = ['"', "'", '[', '(', '{']
            bw = ['"', "'", ']', ')', '}']
            val = env_var.strip()
            # Unwrap outer layer while both sides match
            while val and val[:1] in fw and val[-1:] in bw:
                val = val[1:-1].strip()
            return val

        # Extend defaults with environment variables if set
        env_add_dirs_str = os.getenv('FUPI_ADD_DIR_NAMES', '').strip()
        env_skip_dirs_str = os.getenv('FUPI_SKIP_DIR_PATTERNS', '').strip()
        
        if env_add_dirs_str:
            # Unwrap the entire value first, then split on commas and unwrap each
            unwrapped = unwrap(env_add_dirs_str)
            env_add_dirs = [unwrap(v.strip()) for v in unwrapped.split(',') if v.strip()]
            self.add_dir_names.extend(env_add_dirs)
        
        if env_skip_dirs_str:
            # Unwrap the entire value first, then split on commas and unwrap each
            unwrapped = unwrap(env_skip_dirs_str)
            env_skip_dirs = [unwrap(v.strip()) for v in unwrapped.split(',') if v.strip()]
            self.skip_dir_patterns.extend(env_skip_dirs)
        
        if autorun: self.run()
        
        
    
    def get_paths(self, add_dir_names=None, skip_dir_patterns=None) -> list:
        """Get the list of paths that will be added to sys.path.
        
        This allows previewing what paths will be added without modifying sys.path.
        
        Args:
            add_dir_names: List of dir names to add. If None, uses self.add_dir_names
            skip_dir_patterns: List of patterns to skip. If None, uses self.skip_dir_patterns
            
        Returns:
            list: Paths that would be added to sys.path
        """
        # Use provided params or fall back to instance variables
        add_dirs = list(set(add_dir_names if add_dir_names is not None else self.add_dir_names))
        if not add_dirs: return [] 
        skip_dirs = list(set(skip_dir_patterns if skip_dir_patterns is not None else self.skip_dir_patterns))
    
        # make sure there are no residual quotes around anything:
        quotes = ['"',"'"]
        add_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in add_dirs]
        skip_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in skip_dirs]
        
        skip_dirs.extend([r'\.*'])  # always skip paths that begin with a period (e.g., `.git`)
        skip_dirs.extend([r'\_*'])  # always skip paths that begin with an underscore (e.g., `__pycache__`)

        # ADD all paths that contain one of our add_dirs (as direct matched strings)
        allpaths = []
        for dirname in add_dirs: 
            tdir = Path.cwd().resolve()
            found_paths = [pth for pth in tdir.rglob('*/') if dirname in pth.parts]
            allpaths.extend(found_paths)

        # REMOVE any paths that matches one of our skip_dirs patterns (as regex patterns)
        skip_dirs_re = [re.compile(f'^{pth}$'.replace('*', '.*')) for pth in skip_dirs]
        allpaths = [pth for pth in allpaths if not any([s.match(part) for part in pth.parts for s in skip_dirs_re])]

        return allpaths
    
    def run(self, add_dir_names=None, skip_dir_patterns=None) -> list:
        """Execute path configuration with given or preset directories.
        
        This gets the qualifying paths and adds them to sys.path.
        
        Args:
            add_dir_names: List of dir names to add. If None, uses self.add_dir_names
            skip_dir_patterns: List of patterns to skip. If None, uses self.skip_dir_patterns
            
        Returns:
            list: Paths that were added to sys.path
        """
        global sys_path_history
        
        # Use provided params or fall back to instance variables
        if add_dir_names is not None:
            self.add_dir_names = list(add_dir_names)
        if skip_dir_patterns is not None:
            self.skip_dir_patterns = list(skip_dir_patterns)
        
        # Get the paths to add
        allpaths = self.get_paths(self.add_dir_names, self.skip_dir_patterns)
        
        # add allpaths to the sys.path for the current process
        sys.path.extend([str(pth) for pth in allpaths if str(pth) not in sys.path])

        # add another entry for our tracking: 
        sys_path_history.append(sys.path.copy())

        return allpaths


def autorun():
    """Auto-run path configuration using default or preset values.
    
    This is called automatically on `import fupi` to add directories to sys.path
    without requiring explicit user configuration.
    
    Returns:
        list: Paths that were added to sys.path
    """
    global autostarted
    mf = ManualFupi()
    result = mf.run()
    return result
