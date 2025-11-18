"""fupi package initializer.

Behavior:
- A plain `import fupi` will automatically run the path-adding side-effect
  (preserves existing behavior).
- A `from fupi import manual_config` (or any `from fupi import ...`) will
  suppress the automatic run so the user can configure manually.
- You can also set environment variables FUPI_ADD_DIR_NAMES and FUPI_SKIP_DIR_PATTERNS 
  to extend the default directory names and skip patterns used by either 
  manual or automatic runs.

This implements a small, best-effort detection by inspecting the importer's
call-site context. It's lightweight and intentionally conservative: if we
can't detect a `from fupi import` invocation (very rare) we default to 
auto-running to preserve backwards-compatibility.
"""

import os

try:
    # import the implementation module
    from . import fupi as _core
    from .fupi import autorun, ManualFupi

    # expose a helper name for manual configuration importers
    def manual_config(add_dirs=None, skip_dirs=None):
        """Optional convenience wrapper for manual configuration.

        Usage patterns:
        - `from fupi import manual_config` will *not* auto-run the package.
          Call `manual_config(add_dirs, skip_dirs)` to configure paths.
        - `import fupi` will auto-run as before.
        
        Note: For new code, prefer using the ManualFupi class:
        - `from fupi import ManualFupi`
        - `mf = ManualFupi()`
        - `mf.add_dir_names = ['src', 'test']`
        - `mf.skip_dir_patterns = ['venv*']`
        - `mf.run()`
        """
        # If called with parameters, perform configuration immediately; if
        # called with no arguments it is effectively a no-op (acts as a
        # sentinel import target to avoid auto-start).
        if add_dirs is not None and skip_dirs is not None:
            mf = ManualFupi()
            return mf.run(add_dir_names=add_dirs, skip_dir_patterns=skip_dirs)
        return None

    # Import the new constant names from core module
    from .fupi import DEFAULT_ADD_DIR_NAMES, DEFAULT_SKIP_DIR_PATTERNS

    __all__ = ['manual_config', 'ManualFupi', 'DEFAULT_ADD_DIR_NAMES', 'DEFAULT_SKIP_DIR_PATTERNS']

    # Lightweight heuristic to detect `from fupi import ...` vs `import fupi`.
    # We scan the import call stack for a textual `from fupi import` occurrence.
    # If found, suppress auto-run. If we can't find such a pattern we default
    # to auto-running to preserve existing behaviour.
    def _import_was_from_style() -> bool:
        """Return True if the import appears to be a `from fupi import ...` call.

        Heuristic: scan the call stack frames. If a source line containing
        `from fupi import` is found, return True. If a source line containing
        a plain `import fupi` is found before any `from` hint, return False.

        If we can't find any useful calling source, default to False (i.e.
        allow autorun) to preserve backwards-compatibility.
        """
        try:
            import inspect
            for frame_info in inspect.stack():
                ctx = frame_info.code_context
                joined = None
                if ctx:
                    joined = ''.join(ctx).strip()
                else:
                    # attempt to read the source file line if code_context is missing
                    try:
                        fn = frame_info.filename
                        ln = frame_info.lineno
                        if fn and fn != '<string>' and fn != '<stdin>' and os.path.exists(fn):
                            with open(fn, 'r') as _f:
                                lines = _f.readlines()
                                if 0 < ln <= len(lines):
                                    joined = lines[ln-1].strip()
                    except Exception:
                        joined = None

                if not joined:
                    continue

                # look for explicit patterns
                if 'from fupi import' in joined:
                    return True
                if 'import fupi' in joined:
                    return False
        except Exception:
            # Be conservative: if stack inspection fails, allow autorun
            return False

        # no clear evidence of a `from`-style import
        return False

    # decide whether to autorun: only run when not importing via `from fupi import ...`
    was_from_style = _import_was_from_style()
    
    # Record autostart state
    try:
        _core.autostarted = not was_from_style
    except Exception:
        pass

    if not was_from_style:
        try:
            autorun()
        except Exception as e:
            import traceback, sys as _sys
            print(f"Error importing or running fupi: {e}", file=_sys.stderr)
            traceback.print_exc()

except Exception as e:
    import traceback, sys as _sys
    print(f"Error importing fupi package: {e}", file=_sys.stderr)
    traceback.print_exc()
