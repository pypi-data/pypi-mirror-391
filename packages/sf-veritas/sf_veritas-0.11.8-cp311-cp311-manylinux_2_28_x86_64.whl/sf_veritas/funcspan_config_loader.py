"""
Function Span Config Loader

Scans directory tree for .sailfish files and inline pragmas.
Builds C hash tables for ultra-fast runtime lookups (<5ns).

Configuration hierarchy (highest to lowest priority):
1. HTTP Header X-Sf3-FunctionSpanCaptureOverride
2. Decorator @capture_function_spans()
3. Function config in .sailfish (functions: section)
4. File pragma # sailfish-funcspan:
5. File config in .sailfish (files: section)
6. Directory .sailfish (cascades down)
7. Parent directory .sailfish (inherited)
8. Environment variables SF_FUNCSPAN_*
9. Hard-coded defaults
"""

import json
import os
import re
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Set

from .env_vars import (
    SF_FUNCSPAN_ARG_LIMIT_MB,
    SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
    SF_FUNCSPAN_CAPTURE_ARGUMENTS,
    SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
    SF_FUNCSPAN_RETURN_LIMIT_MB,
    SF_DEBUG,
)


class FunctionSpanConfigLoader:
    """
    Scans directory tree for .sailfish files at startup.
    Parses YAML/TOML/JSON and inline pragmas.
    Builds C hash tables for ultra-fast runtime lookups.
    """

    def __init__(self, root_paths: List[str]):
        try:
            from . import _sffuncspan_config
            self._c_config = _sffuncspan_config
        except ImportError as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Failed to import _sffuncspan_config: {e}",
                    log=False,
                )
            self._c_config = None

        # Also import _sffuncspan for cache pre-population
        try:
            from . import _sffuncspan
            self._c_profiler = _sffuncspan
        except ImportError as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Failed to import _sffuncspan: {e}",
                    log=False,
                )
            self._c_profiler = None

        self.root_paths = root_paths
        self.configs: Dict[str, Dict] = {}  # path -> config
        self.resolved_configs: Dict[str, Dict] = {}  # resolved with inheritance

    def load_all_configs(self):
        """Scan and load all .sailfish files + pragmas"""
        if not self._c_config:
            if SF_DEBUG:
                print(
                    "[[DEBUG]] Config loader: C extension not available, skipping",
                    log=False,
                )
            return

        # Debug: Show what root paths we're scanning
        print(
            f"[FuncSpanDebug] Scanning for .sailfish files in root paths:",
            log=False,
        )
        for root in self.root_paths:
            print(f"[FuncSpanDebug]   - {root} (exists={os.path.exists(root)})", log=False)

        # 1. Walk directory trees for .sailfish files
        sailfish_files_found = []
        for root in self.root_paths:
            if not os.path.exists(root):
                continue

            for dirpath, _, filenames in os.walk(root):
                if '.sailfish' in filenames:
                    config_path = os.path.join(dirpath, '.sailfish')
                    sailfish_files_found.append(config_path)
                    self._load_config_file(config_path, dirpath)

        print(
            f"[FuncSpanDebug] Found {len(sailfish_files_found)} .sailfish files:",
            log=False,
        )
        for sf_file in sailfish_files_found:
            print(f"[FuncSpanDebug]   - {sf_file}", log=False)

        # 2. Scan all Python files for pragmas (only first 50 lines, ONE per file!)
        for root in self.root_paths:
            if not os.path.exists(root):
                continue

            for py_file in Path(root).rglob('*.py'):
                self._scan_pragma(str(py_file))

        # 3. Resolve inheritance and build C tables
        self._resolve_inheritance()
        self._build_c_tables()

        print(
            f"[FuncSpanDebug] Config loader: Loaded {len(self.resolved_configs)} resolved configs",
            log=False,
        )

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Config loader: Loaded {len(self.resolved_configs)} configs",
                log=False,
            )

    def _load_config_file(self, path: str, dirpath: str):
        """Load .sailfish file (auto-detect YAML/TOML/JSON format)"""
        try:
            with open(path, 'r') as f:
                content = f.read()
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Failed to read {path}: {e}",
                    log=False,
                )
            return

        # Try to parse in order: YAML, TOML, JSON
        config = None

        # Try YAML first (most common)
        try:
            import yaml
            config = yaml.safe_load(content)
        except Exception:
            pass

        # Try TOML if YAML failed
        if config is None:
            try:
                try:
                    import tomllib  # Python 3.11+
                except ImportError:
                    import tomli as tomllib  # fallback for older Python
                config = tomllib.loads(content)
            except Exception:
                pass

        # Try JSON if both YAML and TOML failed
        if config is None:
            try:
                config = json.loads(content)
            except Exception as e:
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Config loader: Failed to parse {path} as YAML/TOML/JSON: {e}",
                        log=False,
                    )
                return

        # Extract funcspan section (optional wrapper)
        # Support both wrapped (funcspan: {...}) and unwrapped formats
        funcspan_config = config.get('funcspan', config)

        # Check if this looks like a funcspan config (has expected keys)
        expected_keys = {'default', 'files', 'functions'}
        if not any(key in funcspan_config for key in expected_keys):
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: No funcspan config in {path}",
                    log=False,
                )
            return

        # Store with directory context
        self.configs[f"DIR:{dirpath}"] = funcspan_config

        # Debug: Show what patterns/keys are in this config
        print(
            f"[FuncSpanDebug] Loaded config from {path}:",
            log=False,
        )
        print(f"[FuncSpanDebug]   Directory: {dirpath}", log=False)
        print(f"[FuncSpanDebug]   Keys in config: {list(funcspan_config.keys())}", log=False)
        if 'default' in funcspan_config:
            print(f"[FuncSpanDebug]   Has 'default' config: {funcspan_config['default']}", log=False)
        # Show all non-default, non-functions keys (these are file patterns)
        file_patterns = [k for k in funcspan_config.keys() if k not in ('default', 'functions', 'files')]
        if file_patterns:
            print(f"[FuncSpanDebug]   File patterns found: {file_patterns}", log=False)
            for pattern in file_patterns:
                print(f"[FuncSpanDebug]     Pattern '{pattern}': {funcspan_config[pattern]}", log=False)

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Config loader: Loaded config from {path}",
                log=False,
            )

    def _scan_pragma(self, file_path: str):
        """Scan file for inline pragma (first 50 lines, ONE per file!)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i > 50:  # Only check first 50 lines
                        break

                    # Match: # sailfish-funcspan: include_arguments=false, sample_rate=0.1
                    if match := re.match(r'#\s*sailfish-funcspan:\s*(.+)', line):
                        config = self._parse_pragma(match.group(1))
                        if config:
                            # Store file-level config
                            self.configs[f"FILE:{file_path}"] = config
                            if SF_DEBUG:
                                print(
                                    f"[[DEBUG]] Config loader: Found pragma in {file_path}: {config}",
                                    log=False,
                                )
                            return  # Only ONE pragma per file!
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Error scanning {file_path}: {e}",
                    log=False,
                )

    def _parse_pragma(self, pragma_str: str) -> Optional[Dict]:
        """Parse pragma: include_arguments=false, sample_rate=0.1"""
        config = {}

        try:
            for part in pragma_str.split(','):
                if '=' not in part:
                    continue

                key, value = part.strip().split('=', 1)
                key = key.strip()
                value = value.strip()

                # Type conversion
                if value.lower() in ('true', 'false'):
                    config[key] = value.lower() == 'true'
                elif '.' in value:
                    config[key] = float(value)
                else:
                    config[key] = int(value)

            return config if config else None
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Failed to parse pragma '{pragma_str}': {e}",
                    log=False,
                )
            return None

    def _resolve_inheritance(self):
        """Resolve directory hierarchy and glob patterns"""
        resolved = {}

        # Determine default config based on whether user has .sailfish files (opt-in)
        if len(self.configs) == 0:
            # No .sailfish files = no opt-in = capture NOTHING by default
            # Headers, decorators, and pragmas can still enable capture
            default_config = {
                'include_arguments': False,
                'include_return_value': False,
                'autocapture_all_children': False,
                'arg_limit_mb': 1,
                'return_limit_mb': 1,
                'sample_rate': 1.0,
            }
            if SF_DEBUG:
                print(
                    "[[DEBUG]] Config loader: No .sailfish files found, default capture disabled",
                    log=False,
                )
        else:
            # Has .sailfish files = user opted in = use env var defaults
            default_config = {
                'include_arguments': SF_FUNCSPAN_CAPTURE_ARGUMENTS,
                'include_return_value': SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
                'autocapture_all_children': SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
                'arg_limit_mb': SF_FUNCSPAN_ARG_LIMIT_MB,
                'return_limit_mb': SF_FUNCSPAN_RETURN_LIMIT_MB,
                'sample_rate': 1.0,
            }
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Found {len(self.configs)} .sailfish configs, using env var defaults",
                    log=False,
                )

        # Process directory configs (cascade down)
        dir_configs = sorted([k for k in self.configs.keys() if k.startswith('DIR:')])

        for key in dir_configs:
            dirpath = key[4:]  # Remove 'DIR:' prefix
            parent_config = self._get_parent_config(dirpath, resolved)

            # Get the base directory config (default + inherited)
            dir_base_config = {**default_config, **parent_config}

            # Apply the 'default' section if present
            config_data = self.configs[key]
            if 'default' in config_data:
                dir_base_config = {**dir_base_config, **config_data['default']}

            resolved[key] = dir_base_config

            # Expand glob patterns in files: section
            if 'files' in config_data:
                self._expand_file_globs(dirpath, config_data['files'], resolved, dir_base_config)

            # IMPORTANT: Also process TOP-LEVEL patterns (not under files:)
            # These are patterns like "*.py", "app.py", "**/*.py" at the root of the config
            top_level_patterns = {
                k: v for k, v in config_data.items()
                if k not in ('default', 'files', 'functions')
            }
            if top_level_patterns:
                print(
                    f"[FuncSpanDebug] Processing top-level patterns for {dirpath}: {list(top_level_patterns.keys())}",
                    log=False,
                )
                self._expand_file_globs(dirpath, top_level_patterns, resolved, dir_base_config)

        # Add file-level configs (pragmas)
        for key in self.configs.keys():
            if key.startswith('FILE:'):
                # Get directory config as base
                file_path = key[5:]  # Remove 'FILE:' prefix
                dir_config = self._get_directory_config_for_file(file_path, resolved)
                resolved[key] = {**default_config, **dir_config, **self.configs[key]}

        self.resolved_configs = resolved

        # Debug: Show summary of resolved configs
        file_configs = [k for k in resolved.keys() if k.startswith('FILE:')]
        print(
            f"[FuncSpanDebug] Resolved {len(file_configs)} file-specific configs",
            log=False,
        )

        # Check if app.py got a config
        app_py_configs = [k for k in file_configs if 'app.py' in k]
        if app_py_configs:
            print(
                f"[FuncSpanDebug] Found {len(app_py_configs)} config(s) for app.py files:",
                log=False,
            )
            for cfg_key in app_py_configs:
                print(f"[FuncSpanDebug]   - {cfg_key[5:]}", log=False)  # Remove FILE: prefix
                print(f"[FuncSpanDebug]     Config: {resolved[cfg_key]}", log=False)
        else:
            print(
                "[FuncSpanDebug] WARNING: No config found for any app.py files!",
                log=False,
            )

    def _get_parent_config(self, dirpath: str, resolved: Dict) -> Dict:
        """Get parent directory's config for inheritance"""
        parent = os.path.dirname(dirpath)

        # Keep walking up until we find a config or reach root
        while parent and parent != dirpath:
            parent_key = f"DIR:{parent}"
            if parent_key in resolved:
                return resolved[parent_key]
            dirpath = parent
            parent = os.path.dirname(parent)

        return {}

    def _get_directory_config_for_file(self, file_path: str, resolved: Dict) -> Dict:
        """Get the directory config that applies to this file"""
        dirpath = os.path.dirname(file_path)

        # Walk up directory tree until we find a config
        while dirpath:
            dir_key = f"DIR:{dirpath}"
            if dir_key in resolved:
                return resolved[dir_key]

            parent = os.path.dirname(dirpath)
            if parent == dirpath:  # Reached root
                break
            dirpath = parent

        return {}

    def _expand_file_globs(self, dirpath: str, file_patterns: Dict, resolved: Dict, base_config: Dict):
        """Expand glob patterns to actual file paths"""
        for pattern, config in file_patterns.items():
            full_pattern = os.path.join(dirpath, pattern)

            print(
                f"[FuncSpanDebug] Expanding glob pattern: '{pattern}' in {dirpath}",
                log=False,
            )
            print(f"[FuncSpanDebug]   Full pattern: {full_pattern}", log=False)

            try:
                matched_files = glob(full_pattern, recursive=True)
                print(
                    f"[FuncSpanDebug]   Matched {len(matched_files)} files",
                    log=False,
                )

                for matched_file in matched_files:
                    # Normalize path
                    matched_file = os.path.normpath(matched_file)
                    resolved[f"FILE:{matched_file}"] = {**base_config, **config}

                    # Show first few matches and last match
                    if len(matched_files) <= 5 or matched_files.index(matched_file) < 3 or matched_files.index(matched_file) >= len(matched_files) - 1:
                        print(f"[FuncSpanDebug]     - {matched_file}", log=False)
                    elif matched_files.index(matched_file) == 3:
                        print(f"[FuncSpanDebug]     ... ({len(matched_files) - 4} more files) ...", log=False)

                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Config loader: Matched file {matched_file} with pattern {pattern}",
                            log=False,
                        )
            except Exception as e:
                print(
                    f"[FuncSpanDebug]   ERROR expanding glob: {e}",
                    log=False,
                )
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Config loader: Failed to expand glob {full_pattern}: {e}",
                        log=False,
                    )

    def _build_c_tables(self):
        """Build C hash tables for ultra-fast lookups"""
        if not self._c_config:
            return

        # 1. Initialize C config system with defaults
        # Use same logic as _resolve_inheritance: no .sailfish = no default capture
        if len(self.configs) == 0:
            default_config = {
                'include_arguments': False,
                'include_return_value': False,
                'autocapture_all_children': False,
                'arg_limit_mb': 1,
                'return_limit_mb': 1,
                'sample_rate': 1.0,
            }
        else:
            default_config = {
                'include_arguments': SF_FUNCSPAN_CAPTURE_ARGUMENTS,
                'include_return_value': SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
                'arg_limit_mb': SF_FUNCSPAN_ARG_LIMIT_MB,
                'return_limit_mb': SF_FUNCSPAN_RETURN_LIMIT_MB,
                'autocapture_all_children': SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
                'sample_rate': 1.0,
            }

        try:
            self._c_config.init(default_config)
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Failed to initialize C config: {e}",
                    log=False,
                )
            return

        # 2. Add all file configs
        file_count = 0
        print(
            f"[FuncSpanDebug] Building C config tables from {len(self.resolved_configs)} resolved configs",
            log=False,
        )
        for key, config in self.resolved_configs.items():
            if key.startswith('FILE:'):
                file_path = key[5:]  # Remove 'FILE:' prefix
                print(
                    f"[FuncSpanDebug] Adding file config to C: {file_path}",
                    log=False,
                )
                print(
                    f"[FuncSpanDebug]   Config: {config}",
                    log=False,
                )
                try:
                    self._c_config.add_file(file_path, config)
                    file_count += 1
                    print(
                        f"[FuncSpanDebug]   ✓ Successfully added to C config system",
                        log=False,
                    )
                except Exception as e:
                    print(
                        f"[FuncSpanDebug]   ✗ FAILED to add to C config: {e}",
                        log=False,
                    )
                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Config loader: Failed to add file config for {file_path}: {e}",
                            log=False,
                        )

        # 3. Add all function configs
        func_count = 0
        for key in self.configs.keys():
            if key.startswith('DIR:'):
                dirpath = key[4:]
                config = self.resolved_configs[key]

                if 'functions' in self.configs[key]:
                    for func_pattern, func_config in self.configs[key]['functions'].items():
                        # Merge with directory base config
                        merged_config = {**config, **func_config}
                        self._add_function_configs(dirpath, func_pattern, merged_config)
                        func_count += 1

        print(
            f"[FuncSpanDebug] Built C tables with {file_count} file configs and {func_count} function configs",
            log=False,
        )

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Config loader: Built C tables with {file_count} file configs and {func_count} function configs",
                log=False,
            )

        # 4. Pre-populate the C profiler cache to avoid Python calls during profiling
        self._prepopulate_profiler_cache()

    def _add_function_configs(self, dirpath: str, pattern: str, config: Dict):
        """Add function configs (handle wildcards)"""
        if not self._c_config:
            return

        # For exact matches (no wildcards), add directly to C table
        if '*' not in pattern:
            # Pattern should be: "module.function" or "file.function"
            # We need to resolve the module to a file path

            # Try to find Python files that match
            parts = pattern.rsplit('.', 1)
            if len(parts) == 2:
                module_pattern, func_name = parts

                # Convert module pattern to file pattern
                # e.g., "api.handlers" -> "api/handlers.py"
                file_pattern = module_pattern.replace('.', os.sep) + '.py'
                full_pattern = os.path.join(dirpath, file_pattern)

                try:
                    matched_files = glob(full_pattern)
                    for matched_file in matched_files:
                        matched_file = os.path.normpath(matched_file)
                        try:
                            self._c_config.add_function(matched_file, func_name, config)

                            if SF_DEBUG:
                                print(
                                    f"[[DEBUG]] Config loader: Added function config {matched_file}:{func_name}",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG:
                                print(
                                    f"[[DEBUG]] Config loader: Failed to add function config {matched_file}:{func_name}: {e}",
                                    log=False,
                                )
                except Exception as e:
                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Config loader: Failed to resolve function pattern {pattern}: {e}",
                            log=False,
                        )

        else:
            # Wildcard patterns - we'll need to compile regex and match at runtime
            # For now, we'll skip wildcards and just log
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Config loader: Skipping wildcard function pattern {pattern} (not yet supported)",
                    log=False,
                )

    def _prepopulate_profiler_cache(self):
        """Pre-populate the C profiler cache to avoid Python calls during profiling"""
        if not self._c_profiler:
            if SF_DEBUG:
                print(
                    "[[DEBUG]] Config loader: C profiler not available, skipping cache pre-population",
                    log=False,
                )
            return

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Config loader: Starting cache pre-population with {len(self.resolved_configs)} resolved configs",
                log=False,
            )

        cache_count = 0

        # Pre-populate cache for all file-level configs (pragmas and .sailfish file patterns)
        for key, config in self.resolved_configs.items():
            if key.startswith('FILE:'):
                file_path = key[5:]  # Remove 'FILE:' prefix

                # Extract config values
                include_arguments = int(config.get('include_arguments', True))
                include_return_value = int(config.get('include_return_value', True))
                autocapture_all_children = int(config.get('autocapture_all_children', True))
                arg_limit_mb = int(config.get('arg_limit_mb', 1))
                return_limit_mb = int(config.get('return_limit_mb', 1))
                sample_rate = float(config.get('sample_rate', 1.0))

                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Config loader: Caching config for {file_path}: args={include_arguments} ret={include_return_value}",
                        log=False,
                    )

                # Cache with "<MODULE>" as function name to indicate file-level config
                try:
                    self._c_profiler.cache_config(
                        file_path,
                        "<MODULE>",
                        include_arguments,
                        include_return_value,
                        autocapture_all_children,
                        arg_limit_mb,
                        return_limit_mb,
                        sample_rate
                    )
                    cache_count += 1
                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Config loader: Successfully cached config for {file_path}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Config loader: Failed to cache config for {file_path}: {e}",
                            log=False,
                        )

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Config loader: Pre-populated profiler cache with {cache_count} file-level configs",
                log=False,
            )


def get_default_config() -> Dict:
    """Get default config from environment variables"""
    return {
        'include_arguments': SF_FUNCSPAN_CAPTURE_ARGUMENTS,
        'include_return_value': SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
        'arg_limit_mb': SF_FUNCSPAN_ARG_LIMIT_MB,
        'return_limit_mb': SF_FUNCSPAN_RETURN_LIMIT_MB,
        'autocapture_all_children': SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
        'sample_rate': 1.0,
    }
