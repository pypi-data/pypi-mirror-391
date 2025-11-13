"""
Sandhi-Aware Telugu Word Combination System
============================================

Based on 18 sandhi types from Telugu Vyakaranam (pages 26-42).
Intelligently combines words following Telugu phonetic rules.
"""

from typing import List, Tuple, Optional
import re

# ═══════════════════════════════════════════════════════════════════════════
# TELUGU SANDHI RULES (from pages 26-42 of the grammar document)
# ═══════════════════════════════════════════════════════════════════════════

class TeluguSandhiEngine:
    """
    Implements Telugu sandhi rules for proper word combination.
    """
    
    def __init__(self):
        # Varga classifications for context-aware resolution
        self.varga_map = {
            'క': 'ఙ', 'ఖ': 'ఙ', 'గ': 'ఙ', 'ఘ': 'ఙ',  # Velar → ఙ
            'చ': 'ఞ', 'ఛ': 'ఞ', 'జ': 'ఞ', 'ఝ': 'ఞ',  # Palatal → ఞ
            'ట': 'ణ', 'ఠ': 'ణ', 'డ': 'ణ', 'ఢ': 'ణ',  # Retroflex → ణ
            'త': 'న', 'థ': 'న', 'ద': 'న', 'ధ': 'న',  # Dental → న
            'ప': 'మ', 'ఫ': 'మ', 'బ': 'మ', 'భ': 'మ',  # Labial → మ
        }
        
        # Harsh to soft consonant mapping (గసడదవ సంధి)
        self.harsh_to_soft = {
            'క': 'గ', 'చ': 'జ', 'ట': 'డ', 'త': 'ద', 'ప': 'బ'
        }
    
    def apply_athva_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply అత్వసంధి (a-kara sandhi).
        
        Rule: హ్రస్వ అకారం + అచ్చు → sandhi or యడాగమం
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Check if word1 ends with 'అ' and word2 starts with vowel
        if word1.endswith('అ'):
            first_char = word2[0] if word2 else ''
            vowels = 'అఆఇఈఉఊఋౠఌౡఎఏఐఒఓఔ'
            
            if first_char in vowels:
                # Can either do sandhi or యడాగమం
                # For simplicity, do యడాగమం
                return word1 + 'య' + word2
        
        return word1 + word2
    
    def apply_yadagama_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply యడాగమసంధి (y-insertion between vowels).
        
        Rule: అచ్చు + అచ్చు → అచ్చు + య + అచ్చు
        """
        if not word1 or not word2:
            return word1 + word2
        
        last_char = word1[-1] if word1 else ''
        first_char = word2[0] if word2 else ''
        
        vowels = 'అఆఇఈఉఊఋౠఌౡఎఏఐఒఓఔ'
        
        if last_char in vowels and first_char in vowels:
            return word1 + 'య' + word2
        
        return word1 + word2
    
    def apply_anusvara_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply అనునాసిక సంధి (homorganic nasal resolution).
        
        Rule: ం + క/చ/ట/త/ప → corresponding nasal
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Check if word1 ends with anusvara
        if word1.endswith('ం'):
            first_char = word2[0] if word2 else ''
            
            # Resolve anusvara based on following consonant
            if first_char in self.varga_map:
                nasal = self.varga_map[first_char]
                return word1[:-1] + nasal + word2
        
        return word1 + word2
    
    def apply_gasadadava_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply గసడదవ సంధి (harsh to soft consonant change).
        
        Rule: First person pronoun + harsh consonant → soft consonant
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Check if word1 is first person pronoun (నేను, మేము, etc.)
        first_person = ['నేను', 'మేము', 'నేన', 'మేమ']
        
        if word1 in first_person and word2:
            first_char = word2[0]
            if first_char in self.harsh_to_soft:
                soft = self.harsh_to_soft[first_char]
                return word1 + soft + word2[1:]
        
        return word1 + word2
    
    def apply_tugagama_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply టుగాగమసంధి (T-insertion in compound words).
        
        Rule: In compounds, ఉ-ending + vowel-starting → insert ట్
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Check if word1 ends with ఉ/ూ and word2 starts with vowel
        if word1.endswith('ఉ') or word1.endswith('ూ'):
            first_char = word2[0] if word2 else ''
            vowels = 'అఆఇఈఉఊఋౠఌౡఎఏఐఒఓఔ'
            
            if first_char in vowels:
                return word1 + 'ట' + word2
        
        return word1 + word2
    
    def apply_rugagama_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply రుగాగమ సంధి (r-insertion with 'ఆలు').
        
        Rule: పేదా + ఆలు → పేదరాలు
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Specific words that take ర insertion before ఆలు
        pedhadi_words = ['పేద', 'బీద', 'జవ', 'కొమ', 'బాలంత', 'మనుమ', 'గొడుడ', 'ముది']
        
        if word1 in pedhadi_words and word2 == 'ఆలు':
            return word1 + 'ర' + word2
        
        return word1 + word2
    
    def apply_durtha_sandhi(self, word1: str, word2: str) -> str:
        """
        Apply దుర్త ప్రాకృతిక సంధి (న-ending word sandhi).
        
        Rule: న్-ending + క/చ/ట/త/ప → homorganic nasal + soft
        """
        if not word1 or not word2:
            return word1 + word2
        
        # Check if word1 ends with న్
        if word1.endswith('న్'):
            first_char = word2[0] if word2 else ''
            
            # Apply homorganic nasal + soft consonant
            if first_char in self.varga_map:
                nasal = self.varga_map[first_char]
                if first_char in self.harsh_to_soft:
                    soft = self.harsh_to_soft[first_char]
                    return word1[:-1] + nasal + soft + word2[1:]
        
        return word1 + word2
    
    def intelligent_combine(self, word1: str, word2: str) -> List[str]:
        """
        Intelligently combine two words using applicable sandhi rules.
        
        Returns multiple possible combinations.
        """
        variants = []
        
        # Try each sandhi rule
        variants.append(self.apply_athva_sandhi(word1, word2))
        variants.append(self.apply_yadagama_sandhi(word1, word2))
        variants.append(self.apply_anusvara_sandhi(word1, word2))
        variants.append(self.apply_gasadadava_sandhi(word1, word2))
        variants.append(self.apply_tugagama_sandhi(word1, word2))
        variants.append(self.apply_rugagama_sandhi(word1, word2))
        variants.append(self.apply_durtha_sandhi(word1, word2))
        
        # Also include simple concatenation
        variants.append(word1 + word2)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for v in variants:
            if v not in seen:
                seen.add(v)
                unique_variants.append(v)
        
        return unique_variants


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH SUGGESTION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

def suggest_with_sandhi(words: List[str], transliterator_func) -> List[str]:
    """
    Generate suggestions using sandhi-aware combination.
    
    Args:
        words: List of Roman words to transliterate
        transliterator_func: Function to transliterate single word
    
    Returns:
        List of Telugu sentence variants with proper sandhi
    """
    if not words:
        return []
    
    # Transliterate each word
    telugu_words = [transliterator_func(word) for word in words]
    
    # Initialize sandhi engine
    sandhi_engine = TeluguSandhiEngine()
    
    # Combine words with sandhi rules
    if len(telugu_words) == 1:
        return telugu_words
    
    # For 2 words, apply all sandhi variants
    if len(telugu_words) == 2:
        return sandhi_engine.intelligent_combine(telugu_words[0], telugu_words[1])
    
    # For multiple words, combine progressively
    results = [telugu_words[0]]
    
    for i in range(1, len(telugu_words)):
        new_results = []
        for prev_result in results:
            variants = sandhi_engine.intelligent_combine(prev_result, telugu_words[i])
            new_results.extend(variants)
        
        # Keep only top 5 to avoid explosion
        results = new_results[:5]
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════

def demonstrate_sandhi_system():
    """Demonstrate the sandhi-aware combination system."""
    print("="*70)
    print("SANDHI-AWARE TELUGU WORD COMBINATION")
    print("="*70 + "\n")
    
    engine = TeluguSandhiEngine()
    
    # Test cases from the grammar document
    test_cases = [
        ('రామ', 'అయ్య', 'అత్వ సంధి'),
        ('మా', 'అమ్మ', 'యడాగమ సంధి'),
        ('పూచెన్', 'కలువలు', 'దుర్త సంధి'),
        ('పేద', 'ఆలు', 'రుగాగమ సంధి'),
        ('నేను', 'కొట్టు', 'గసడదవ సంధి'),
    ]
    
    print("Test Cases:")
    for word1, word2, rule_name in test_cases:
        variants = engine.intelligent_combine(word1, word2)
        print(f"\n{rule_name}:")
        print(f"  Input: {word1} + {word2}")
        print(f"  Variants:")
        for i, variant in enumerate(variants[:3], 1):
            print(f"    {i}. {variant}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    demonstrate_sandhi_system()
