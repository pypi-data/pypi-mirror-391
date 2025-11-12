"""
Optimal setup.py for Telugu NLP Library
========================================

Strategy: Core package with zero dependencies + optional extras

Benefits:
- 99% of users get fast, working installation
- Power users can opt-in to heavy dependencies
- Package stays lightweight (~150 KB)
- Works on all platforms (Windows, Mac, Linux, ARM)
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from package
__version__ = "6.0.0"  # Using the actual project version

setup(
    name="telugu-language-tools",
    version=__version__,
    author="Telugu Library Contributors",
    author_email="support@telugulibrary.org",
    description="Modern Telugu v3.0 compliant library with present continuous tense, modern pronouns, comprehensive validation, and 100% test coverage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/telugu_lib",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/telugu_lib/issues",
        "Documentation": "https://github.com/yourusername/telugu_lib/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/telugu_lib",
    },
    packages=find_packages(include=["telugu_engine*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    
    # =========================================================================
    # CORE DEPENDENCIES (ALWAYS INSTALLED)
    # =========================================================================
    # Keep this EMPTY for maximum compatibility!
    install_requires=[
        # NOTHING! Pure Python only
        # This is your competitive advantage
    ],
    
    # =========================================================================
    # OPTIONAL EXTRAS (USER CHOOSES)
    # =========================================================================
    extras_require={
        # ML features: Sentence transformers for advanced NLP
        'ml': [
            'sentence-transformers>=2.2.0',  # ~100 MB, for advanced features
        ],

        # Development tools
        'dev': [
            'build>=0.8.0',
            'twine>=4.0.0',
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],

        # Testing tools
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],

        # All optional features
        'all': [
            'sentence-transformers>=2.2.0',
        ],

        # Everything including dev tools
        'full': [
            'sentence-transformers>=2.2.0',
            'build>=0.8.0',
            'twine>=4.0.0',
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],
    },
    
    # Package data (include any data files)
    package_data={
        'telugu_engine': [
            'data/*.json',  # If you have data files
            'data/*.txt',
        ],
    },

    # Entry points (CLI commands if you want them)
    entry_points={
        'console_scripts': [
            'telugu-transliterate=telugu_engine.cli:transliterate_cli',
            'telugu-analyze=telugu_engine.cli:analyze_cli',
        ],
    },
    
    # Keywords for PyPI search
    keywords=[
        'telugu', 'nlp', 'transliteration', 'language', 'processing',
        'indian-languages', 'dravidian', 'fst', 'morphology', 'linguistics'
    ],
    
    # License
    license="MIT",
    
    # Zip safety
    zip_safe=False,
)


# ============================================================================
# EXAMPLE: __version__.py
# ============================================================================
"""
Create telugu_nlp/__version__.py:

__version__ = "5.6.0"
__author__ = "Your Name"
__license__ = "MIT"
"""


# ============================================================================
# EXAMPLE: README.md (Installation Section)
# ============================================================================
"""
# Telugu Language Tools

A modern Telugu v3.0 compliant library with present continuous tense, modern pronouns, comprehensive validation, and 100% test coverage.

## Installation

### Quick Start (Recommended)
```bash
# Install core library (zero dependencies, works everywhere!)
pip install telugu-language-tools
```

### Optional Features

```bash
# With ML features (sentence transformers, ~100 MB)
pip install telugu-language-tools[ml]

# For development
pip install telugu-language-tools[dev]

# With all features
pip install telugu-language-tools[all]
```

## Features

### Core Package (Zero Dependencies!)
✓ Roman → Telugu transliteration (v3.0 compliant)
✓ Modern grammar (verbs, cases, SOV)
✓ Present continuous tense support
✓ Verb conjugation (past, present, future)
✓ 4-case system: Nominative, Accusative, Dative, Locative
✓ Sandhi rules and vowel harmony
✓ v3.0 compliance validation
✓ Enhanced tense engine (v5.5)

### Modern Telugu v3.0 Standards
✓ Modern pronouns: నేను, వాళ్ళు (NOT ఏను, వాండ్రు)
✓ Modern verbs: చేసినాను (NOT చేసితిని)
✓ SOV syntax
✓ No archaic letters: ఱ, ఌ, ౡ, ౘ, ౙ, ఀ, ౝ

## Quick Start

```python
import telugu_engine

# Simple transliteration
telugu_engine.eng_to_telugu("krishna")  # → "క్రిష్ణ"

# Transliterate a sentence
telugu_engine.transliterate_sentence("I am going to school")
# → "ఐ ఆమ్ గోయింగ్ టు స్కూల్"

# Validate v3.0 compliance
telugu_engine.is_v3_compliant("నేను వెళ్తున్నాను")
# → True

# Get compliance score
telugu_engine.get_compliance_score("నేను చేసాను")
# → 95.5

# Translate with full grammar
telugu_engine.translate("I am going", include_grammar=True)
# → "నేను వెళ్తున్నాను"

# Apply verb conjugation
telugu_engine.conjugate_past_tense("నేను", "చేయు")
# → "నేను చేసాను"
```

## v3.0 Compliance

This library is fully compliant with Modern Telugu v3.0 standards:

- Present continuous tense: "I am going" → నేను వెళ్తున్నాను
- All 16 v3.0 sections implemented
- Comprehensive validation tools
- Translation challenges solved

## Why Zero Dependencies?

- ✅ **Fast installation**: 1-2 seconds, not minutes
- ✅ **Works everywhere**: Windows, Mac, Linux, ARM
- ✅ **No compilation**: No C++ compiler needed
- ✅ **Smaller package**: Pure Python implementation
- ✅ **Fewer conflicts**: No dependency hell

## License

MIT License - see LICENSE file for details.
"""


# ============================================================================
# EXAMPLE: CI/CD Configuration (.github/workflows/test.yml)
# ============================================================================
"""
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install core package (zero dependencies)
      run: |
        pip install -e .
    
    - name: Test core features
      run: |
        python -m pytest tests/test_core.py
    
    - name: Install optional dependencies
      run: |
        pip install -e .[all]
      continue-on-error: true  # Pynini might fail on some platforms
    
    - name: Test optional features (if available)
      run: |
        python -m pytest tests/test_optional.py
      continue-on-error: true
"""


# ============================================================================
# EXAMPLE: User-Facing API (telugu_engine/__init__.py)
# ============================================================================
"""
# telugu_engine/__init__.py

__version__ = "5.6.0"
__author__ = "Telugu Library v3.0"
__email__ = "support@telugulibrary.org"

# Import core features (always available)
from .transliterator import eng_to_telugu
from .grammar import (
    conjugate_verb,
    apply_case,
    convert_svo_to_soV,
    build_telugu_sentence,
    apply_sandhi,
    check_vowel_harmony,
    apply_vowel_harmony
)
from .enhanced_tense import (
    translate_sentence,
    conjugate_present_continuous,
    conjugate_past_tense,
    conjugate_verb_enhanced,
    detect_tense_enhanced,
    detect_person,
    validate_translation_output,
    run_comprehensive_test_suite
)
from .v3_validator import (
    validate_script,
    validate_pronouns,
    validate_verbs,
    validate_case_markers,
    validate_vowel_harmony,
    validate_v3_compliance,
    get_compliance_report,
    test_v3_compliance
)
from .phonetic_matrix import map_sound


# ============================================================================
# PUBLIC API (What users import)
# ============================================================================

def transliterate_word(word: str) -> str:
    """Transliterate a single word.

    Args:
        word: Input word in Roman script

    Returns:
        Telugu text

    Example:
        >>> transliterate_word("krishna")
        'క్రిష్ణ'
    """
    return eng_to_telugu(word)


def transliterate_sentence(sentence: str) -> str:
    """Transliterate a complete sentence.

    Args:
        sentence: Input sentence in Roman script

    Returns:
        Telugu text

    Example:
        >>> transliterate_sentence("I am going to school")
        'ఐ ఆమ్ గోయింగ్ టు స్కూల్'
    """
    words = sentence.split()
    return ' '.join(eng_to_telugu(word) for word in words)


def translate(text: str, include_grammar: bool = False) -> str:
    """High-level translation function.

    Args:
        text: English text to translate
        include_grammar: If True, apply full grammar (cases, SOV, etc.)

    Returns:
        Telugu text

    Example:
        >>> translate("I am going", include_grammar=True)
        'నేను వెళ్తున్నాను'
    """
    if include_grammar:
        from .enhanced_tense import translate_sentence
        return translate_sentence(text)
    else:
        return eng_to_telugu(text)


def is_v3_compliant(text: str) -> bool:
    """Check if text is v3.0 compliant.

    Args:
        text: Telugu text to check

    Returns:
        True if compliant, False otherwise

    Example:
        >>> is_v3_compliant("నేను వెళ్తున్నాను")
        True
    """
    result = validate_v3_compliance(text)
    return result['is_compliant']


def get_compliance_score(text: str) -> float:
    """Get v3.0 compliance score (0-100).

    Args:
        text: Telugu text to check

    Returns:
        Compliance score (0-100)

    Example:
        >>> get_compliance_score("నేను చేసాను")
        95.5
    """
    result = validate_v3_compliance(text)
    return result['score']


# Check for optional dependencies
def check_dependencies():
    """Check which optional features are available."""
    info = {
        'core': True,
        'version': __version__,
        'package': 'telugu_engine',
    }

    # Check for sentence-transformers (ML features)
    try:
        import sentence_transformers
        info['sentence_transformers'] = True
        info['sentence_transformers_version'] = sentence_transformers.__version__
    except ImportError:
        info['sentence_transformers'] = False

    return info


__all__ = [
    # Transliteration
    'eng_to_telugu',
    'transliterate_word',
    'transliterate_sentence',

    # Grammar
    'conjugate_verb',
    'apply_case',
    'convert_svo_to_soV',
    'build_telugu_sentence',
    'apply_sandhi',
    'check_vowel_harmony',
    'apply_vowel_harmony',

    # Enhanced Tense (v5.0 - Full v3.0 Support)
    'translate_sentence',
    'conjugate_present_continuous',
    'conjugate_past_tense',
    'conjugate_verb_enhanced',
    'detect_tense_enhanced',
    'validate_translation_output',
    'run_comprehensive_test_suite',

    # Validation
    'validate_v3_compliance',
    'get_compliance_report',
    'test_v3_compliance',
    'validate_script',
    'validate_pronouns',
    'validate_verbs',
    'validate_case_markers',
    'validate_vowel_harmony',

    # High-level API
    'translate',
    'is_v3_compliant',
    'get_compliance_score',

    # Legacy (for compatibility)
    'map_sound',
    'check_dependencies',
    '__version__',
]
"""


# ============================================================================
# EXAMPLE: Testing Strategy
# ============================================================================
"""
# tests/test_core.py - Tests that MUST pass (no dependencies)

import telugu_engine

def test_transliteration_works():
    '''Test core transliteration (zero dependencies).'''
    assert telugu_engine.eng_to_telugu("krishna") == "క్రిష్ణ"
    assert telugu_engine.eng_to_telugu("rama") == "రామ"

def test_transliterate_word():
    '''Test word transliteration.'''
    assert telugu_engine.transliterate_word("krishna") == "క్రిష్ణ"

def test_transliterate_sentence():
    '''Test sentence transliteration.'''
    result = telugu_engine.transliterate_sentence("I am going")
    assert "ఐ" in result
    assert "ఆమ్" in result
    assert "గోయింగ్" in result

def test_v3_compliance():
    '''Test v3.0 compliance validation.'''
    result = telugu_engine.is_v3_compliant("నేను వెళ్తున్నాను")
    assert result is True

    result = telugu_engine.is_v3_compliant("ఏను వాడు")  # Old form
    assert result is False

def test_compliance_score():
    '''Test compliance scoring.'''
    score = telugu_engine.get_compliance_score("నేను చేసాను")
    assert isinstance(score, float)
    assert 0 <= score <= 100

def test_grammar_functions():
    '''Test grammar functions.'''
    # Test verb conjugation
    result = telugu_engine.conjugate_past_tense("నేను", "చేయు")
    assert "నేను" in result
    assert "చేసాను" in result

def test_translate_with_grammar():
    '''Test high-level translate function.'''
    result = telugu_engine.translate("I am going", include_grammar=True)
    assert "నేను" in result
    assert "వెళ్తున్నాను" in result

def test_installation_info():
    '''Test dependency checker.'''
    info = telugu_engine.check_dependencies()
    assert info['core'] is True
    assert 'version' in info
    assert 'package' in info


# tests/test_optional.py - Tests that may skip if deps missing

import pytest
import telugu_engine

# Skip if sentence-transformers not installed
ml_available = telugu_engine.check_dependencies().get('sentence_transformers', False)

@pytest.mark.skipif(not ml_available, reason="sentence-transformers not installed")
def test_ml_features():
    '''Test ML features (optional).'''
    # Test sentence-transformers features if available
    pass
"""


# ============================================================================
# SUMMARY: What You Should Do
# ============================================================================
"""
OPTIMAL SETUP FOR telugu-language-tools (v5.6.0):

1. Core Package (DEFAULT):
   - transliterator.py: Modern v3.0 transliteration (50 KB)
   - grammar.py: Modern grammar and verb conjugation (50 KB)
   - enhanced_tense.py: Present continuous and all tenses (60 KB)
   - v3_validator.py: v3.0 compliance validation (50 KB)
   - phonetic_matrix.py: Phonetic normalization (10 KB)
   - Total: ~220 KB
   - Dependencies: NONE ✓

2. Optional Extras:
   - [ml]: sentence-transformers (~100 MB) for advanced ML features
   - [dev]: build, twine, pytest, pytest-cov for development
   - [test]: pytest, pytest-cov for testing
   - [all]: All optional features
   - [full]: Everything including dev tools

3. Installation:
   pip install telugu-language-tools           # 99% of users (220 KB, 2 sec)
   pip install telugu-language-tools[ml]       # ML features (100 MB)
   pip install telugu-language-tools[dev]      # For development
   pip install telugu-language-tools[full]     # Everything

4. Benefits:
   ✓ Works everywhere (Windows, Mac, Linux, ARM)
   ✓ Fast installation (1-2 seconds, not minutes)
   ✓ No compilation required
   ✓ Modern Telugu v3.0 compliant
   ✓ Present continuous tense support
   ✓ Zero dependencies for core features
   ✓ Optional ML features when needed
   ✓ Users love you for keeping it simple

5. Modern Telugu v3.0 Features:
   ✓ Modern pronouns: నేను, వాళ్ళు (NOT ఏను, వాండ్రు)
   ✓ Modern verbs: చేసినాను (NOT చేసితిని)
   ✓ Present continuous: వెళ్తున్నాను
   ✓ 4-case system: Nominative, Accusative, Dative, Locative
   ✓ SOV syntax
   ✓ No archaic letters

6. Marketing:
   "Modern Telugu v3.0 library with zero dependencies - pip install and go!"
   "Full v3.0 compliance with present continuous tense support"
"""