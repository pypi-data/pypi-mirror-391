# src/duplifinder/ast_processor.py

"""AST file processor for definition extraction."""

import fnmatch
import logging
import tokenize
import re  # For exclude_names
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import ast

from .ast_visitor import EnhancedDefinitionVisitor
from .config import Config
from .utils import audit_log_event


def process_file_ast(py_file: Path, config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], str | None, int]:
    """Process a single Python file for definitions using AST; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        audit_log_event(config, "file_skipped", path=str_py_file, reason="exclude_pattern_match")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Audit: Log open attempt
        audit_log_event(config, "file_opened", path=str_py_file, action="ast_open")
        # Encoding-aware open with fallback
        with tokenize.open(py_file) as fh:  # Handles BOM/encoding
            text = fh.read()
        bytes_read = len(text)
        total_lines = len(text.splitlines())
        audit_log_event(config, "file_parsed", path=str_py_file, action="ast_success", bytes_read=bytes_read, lines=total_lines)
        
        tree = ast.parse(text, filename=str_py_file)
        lines = text.splitlines() if config.preview else []
        visitor = EnhancedDefinitionVisitor(config.types_to_search)
        visitor.visit(tree)
        definitions: Dict[str, Dict[str, List[Tuple[str, str]]]] = {t: defaultdict(list) for t in config.types_to_search}
        for t, items in visitor.definitions.items():
            for name, lineno, end_lineno, _ in items:
                if any(re.match(pat, name) for pat in config.exclude_names):
                    continue
                loc = f"{str_py_file}:{lineno}"
                snippet = ""
                if config.preview and lines:
                    snippet_lines = lines[lineno - 1 : end_lineno]
                    if snippet_lines:
                        # Find minimum indent, ignoring empty lines
                        indent = min((len(line) - len(line.lstrip())) for line in snippet_lines if line.strip())
                        snippet_lines = [line[indent:] for line in snippet_lines]
                        snippet = "\n".join(f"{i + 1} {line}" for i, line in enumerate(snippet_lines))
                definitions[t][name].append((loc, snippet))
        return definitions, None, total_lines
    
    # FIXED: Moved UnicodeDecodeError BEFORE ValueError
    except UnicodeDecodeError as e:
        reason = f"encoding_error: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}; try --encoding flag in future")
        return {}, str_py_file, 0
    except (SyntaxError, ValueError) as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file} due to parsing error: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file}: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0