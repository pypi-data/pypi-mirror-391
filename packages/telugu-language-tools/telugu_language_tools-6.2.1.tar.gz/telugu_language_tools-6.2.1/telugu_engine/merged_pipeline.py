"""
merged_pipeline.py

Integration of enhanced Telugu mappings with the fixed combo pipeline.
This file acts as the main entry point that combines all enhanced features.

Features integrated:
- Enhanced validation using is_valid_telugu_word
- Context-aware anusvara resolution using resolve_anusvara_context_aware
- Sandhi rules using apply_athva_sandhi and apply_yadagama_sandhi
- Grammar-based scoring using enhanced_word_scoring
- Candidate filtering using filter_and_rank_candidates
- Anusvara sequence fixing using fix_anusvara_sequence
"""

from __future__ import annotations
from typing import List, Dict, Optional
import logging

# Import from the enhanced fixed pipeline
from .fixed_combo_pipeline import (
    process_english_words_input,
    process_english_sentence_input,
    process_telugu_word_in_english_script,
    process_telugu_sentence_in_english_script,
    is_valid_telugu_word,
    resolve_anusvara_context_aware,
    apply_athva_sandhi,
    apply_yadagama_sandhi,
    classify_word_by_ending,
    get_varga_for_consonant,
    get_consonant_nature,
    fix_anusvara_sequence,
    filter_and_rank_candidates,
    enhanced_word_scoring
)

logger = logging.getLogger(__name__)

class MergedPipeline:
    """
    Merged pipeline that combines all enhanced Telugu mapping features
    with the robust fixed combo pipeline structure.
    """
    
    def __init__(self, per_word_limit: int = 6, beam: int = 6):
        self.per_word_limit = per_word_limit
        self.beam = beam

    def process_word(self, word: str) -> Dict:
        """Process a single word with all enhanced features."""
        return process_english_words_input(
            word, 
            letter_tokenize=True, 
            per_word_limit=self.per_word_limit
        )
    
    def process_sentence(self, sentence: str) -> Dict:
        """Process a sentence with all enhanced features."""
        return process_english_sentence_input(
            sentence, 
            per_word_limit=self.per_word_limit, 
            beam=self.beam
        )
    
    def validate_telugu_word(self, word: str) -> bool:
        """Validate Telugu word structure using grammar rules."""
        return is_valid_telugu_word(word)
    
    def resolve_anusvara(self, following_char: str) -> str:
        """Resolve anusvara based on following consonant."""
        return resolve_anusvara_context_aware(following_char)
    
    def apply_athva(self, word1: str, word2: str) -> str:
        """Apply athva sandhi between two words."""
        return apply_athva_sandhi(word1, word2)
    
    def apply_yadagama(self, word1: str, word2: str) -> str:
        """Apply yadagama sandhi between two words."""
        return apply_yadagama_sandhi(word1, word2)
    
    def score_word(self, word: str) -> int:
        """Score a word using enhanced grammar-based heuristics."""
        return enhanced_word_scoring(word)
    
    def fix_anusvara_sequence_in_tokens(self, tokens: List[str]) -> List[str]:
        """Fix anusvara sequences across token boundaries."""
        return fix_anusvara_sequence(tokens)
    
    def rank_candidates(self, candidates: List[str]) -> List[str]:
        """Rank candidates using enhanced validation."""
        return filter_and_rank_candidates(candidates)


# Convenience functions for direct use
def transliterate_word(word: str, per_word_limit: int = 6) -> Dict:
    """Direct function to transliterate a single word."""
    return process_english_words_input(
        word, 
        letter_tokenize=True, 
        per_word_limit=per_word_limit
    )


def transliterate_sentence(sentence: str, per_word_limit: int = 6, beam: int = 6) -> Dict:
    """Direct function to transliterate a sentence with enhanced features."""
    return process_english_sentence_input(
        sentence, 
        per_word_limit=per_word_limit, 
        beam=beam
    )


def validate_word_structure(word: str) -> bool:
    """Validate Telugu word structure using grammar rules."""
    return is_valid_telugu_word(word)


def resolve_anusvara_for_context(following_char: str) -> str:
    """Resolve anusvara based on following character context."""
    return resolve_anusvara_context_aware(following_char)


if __name__ == "__main__":
    # Example usage
    print("Enhanced Telugu Merged Pipeline - Example Usage")
    print("=" * 50)
    
    # Test word processing
    word_result = transliterate_word("namaste", per_word_limit=4)
    print(f"Word 'namaste' -> {word_result['combined_word_variants'][:2]}")
    
    # Test sentence processing  
    sentence_result = transliterate_sentence("namaste krishna", per_word_limit=3, beam=3)
    print(f"Sentence 'namaste krishna' -> {sentence_result['sentence_variants'][:2]}")
    
    # Test validation
    print(f"Validation of 'రామ': {validate_word_structure('రామ')}")
    print(f"Validation of 'invalid': {validate_word_structure('invalid')}")
    
    # Test anusvara resolution
    print(f"Anusvara before 'క': {resolve_anusvara_for_context('క')}")
    print(f"Anusvara before 'చ': {resolve_anusvara_for_context('చ')}")
    
    print("\nMerged pipeline is ready for use!")