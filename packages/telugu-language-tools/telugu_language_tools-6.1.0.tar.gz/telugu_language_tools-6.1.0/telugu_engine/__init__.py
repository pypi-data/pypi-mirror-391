"""
Telugu Library v6.0 - Streamlined Telugu Engine
===============================================

Complete v3.0 compliant Telugu processing library with streamlined architecture:
- transliterator: Modern transliteration (no archaic letters)
- grammar: Modern grammar (verbs, cases, SOV)
- enhanced_tense: v5.5 enhanced tense with all tenses (present continuous, past, future)
- v3_validator: v3.0 compliance validation
- phonetic_matrix: Phonetic normalization
- combo_pipeline: Comprehensive pipeline for all transliteration workflows

All modules use modern Vyāvahārika standards:
- Modern pronouns: నేను, వాళ్ళు (NOT ఏను, వాండ్రు)
- Modern verbs: చేసినాను (NOT చేసితిని)
- 4-case system: Nominative, Accusative, Dative, Locative
- SOV syntax
- No archaic letters: ఱ, ఌ, ౡ, ౘ, ౙ, ఀ, ౝ

v6.0 Features:
- Present continuous tense: "I am going" → నేను వెళ్తున్నాను
- All 16 v3.0 sections implemented
- Comprehensive test suites
- Translation challenges solved
- Error prevention checklist
- Streamlined architecture with focused modules
"""

# Main API - transliteration
from .transliterator import (
    eng_to_telugu,
)

def transliterate_word(word: str) -> str:
    """Transliterate a single word."""
    return eng_to_telugu(word)

def transliterate_sentence(sentence: str) -> str:
    """Transliterate a complete sentence."""
    words = sentence.split()
    return ' '.join(eng_to_telugu(word) for word in words)

def validate_v3_compliance(text: str) -> dict:
    """Validate v3 compliance using the v3_validator module."""
    from .v3_validator import validate_v3_compliance as validator
    return validator(text)

# Grammar module
from .grammar import (
    conjugate_verb,
    apply_case,
    convert_svo_to_soV,
    build_telugu_sentence,
    apply_sandhi,
    check_vowel_harmony,
    apply_vowel_harmony
)

# v3.0 validator
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

# Enhanced tense engine (v5.0 - full v3.0 support)
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

# Phonetic matrix (kept for compatibility)
from .phonetic_matrix import map_sound

# Suggestion module (required by combo_pipeline)
from .suggest import suggestions
from .suggest_sentence import sentence_variants, per_token_suggestions

# Combo pipeline - comprehensive workflow engine
from .combo_pipeline import (
    process_english_words_input,
    process_english_sentence_input,
    process_telugu_word_in_english_script,
    process_telugu_sentence_in_english_script
)

# Public API
__version__ = "6.1.0"
__author__ = "Telugu Library v3.0"
__email__ = "support@telugulibrary.org"

__all__ = [
    # Transliteration
    "eng_to_telugu",
    "transliterate_word",
    "transliterate_sentence",

    # Grammar
    "conjugate_verb",
    "apply_case",
    "convert_svo_to_soV",
    "build_telugu_sentence",
    "apply_sandhi",
    "check_vowel_harmony",
    "apply_vowel_harmony",

    # Enhanced Tense (v5.0 - Full v3.0 Support)
    "translate_sentence",
    "conjugate_present_continuous",
    "conjugate_past_tense",
    "conjugate_verb_enhanced",
    "detect_tense_enhanced",
    "validate_translation_output",
    "run_comprehensive_test_suite",

    # Validation
    "validate_v3_compliance",
    "get_compliance_report",
    "test_v3_compliance",
    "validate_script",
    "validate_pronouns",
    "validate_verbs",
    "validate_case_markers",
    "validate_vowel_harmony",

    # Legacy (for compatibility)
    "map_sound",

    # Suggestions
    "suggestions",
    "sentence_variants", 
    "per_token_suggestions",

    # Combo Pipeline
    "process_english_words_input",
    "process_english_sentence_input",
    "process_telugu_word_in_english_script",
    "process_telugu_sentence_in_english_script",
]

# Convenience functions
def translate(text: str, include_grammar: bool = False) -> str:
    """
    High-level translation function.

    Args:
        text: English text to translate
        include_grammar: If True, apply full grammar (cases, SOV, etc.)

    Returns:
        Telugu text
    """
    if include_grammar:
        # Apply full grammar processing using enhanced tense engine
        from .enhanced_tense import translate_sentence
        return translate_sentence(text)
    else:
        # Just transliterate
        return eng_to_telugu(text)


def is_v3_compliant(text: str) -> bool:
    """
    Check if text is v3.0 compliant.

    Args:
        text: Telugu text to check

    Returns:
        True if compliant, False otherwise
    """
    result = validate_v3_compliance(text)
    return result['is_compliant']


def get_compliance_score(text: str) -> float:
    """
    Get v3.0 compliance score (0-100).

    Args:
        text: Telugu text to check

    Returns:
        Compliance score (0-100)
    """
    result = validate_v3_compliance(text)
    return result['score']


# Check for optional dependencies
def check_dependencies():
    """
    Check which optional features are available.

    Returns:
        Dict with information about available features
    """
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


def get_word_suggestions(word: str, limit: int = 8) -> list:
    """
    Get multiple Telugu suggestions for a Roman word.
    
    Args:
        word: Roman word to suggest Telugu variants for
        limit: Maximum number of suggestions to return
        
    Returns:
        List of suggested Telugu spellings
    """
    return suggestions(word, limit=limit)


def get_sentence_suggestions(text: str, topn: int = 5, per_word: int = 4, beam: int = 6) -> list:
    """
    Get multiple Telugu sentence suggestions for Roman input.
    
    Args:
        text: Roman sentence to suggest Telugu variants for
        topn: Number of top sentence variants to return
        per_word: Candidates per token
        beam: Beam width for search
        
    Returns:
        List of suggested Telugu sentences
    """
    return sentence_variants(text, topn=topn, per_word=per_word, beam=beam)


def get_token_suggestions(text: str, limit: int = 6) -> list:
    """
    Get per-token suggestions for a Roman sentence.
    
    Args:
        text: Roman sentence to get per-token suggestions for
        limit: Maximum number of suggestions per token
        
    Returns:
        List of lists, each containing suggestions for a token
    """
    return per_token_suggestions(text, limit=limit)


def get_english_word_variants(word: str, limit: int = 8) -> list:
    """
    Get Telugu variants for English word using combo pipeline.

    Args:
        word: English word to get Telugu variants for
        limit: Maximum number of variants to return

    Returns:
        List of Telugu variants
    """
    result = process_english_words_input(word, per_word_limit=limit)
    return result["combined_word_variants"][:limit]


def get_english_sentence_variants(sentence: str, topn: int = 5, per_word: int = 4, beam: int = 6) -> list:
    """
    Get Telugu sentence variants for English sentence using combo pipeline.

    Args:
        sentence: English sentence to get Telugu variants for
        topn: Number of top sentence variants to return
        per_word: Candidates per token
        beam: Beam width for search

    Returns:
        List of Telugu sentence variants
    """
    result = process_english_sentence_input(sentence, per_word_limit=per_word, beam=beam)
    return result["sentence_variants"][:topn]


# Add to public API
__all__.extend([
    "translate",
    "is_v3_compliant",
    "get_compliance_score",
    "check_dependencies",
    "get_word_suggestions",
    "get_sentence_suggestions",
    "get_token_suggestions",
    "get_english_word_variants",
    "get_english_sentence_variants",
])
