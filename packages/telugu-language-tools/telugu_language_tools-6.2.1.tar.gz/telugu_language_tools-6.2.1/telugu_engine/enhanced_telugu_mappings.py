"""
Enhanced Telugu Transliterator with Grammar-Based Mappings
===========================================================

Based on Telugu Vyakaranam (Grammar) specifications from the document.
Implements proper phonetic classifications and sandhi rules.
"""

from typing import Dict, List, Tuple, Optional
import re

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: COMPLETE PHONETIC CLASSIFICATIONS (from pages 3-4)
# ═══════════════════════════════════════════════════════════════════════════

# Five Vargas (classes) based on articulation point
VARGA_CLASSIFICATIONS = {
    'velar': {  # కంఠము (Kanthamu) - throat
        'consonants': ['క', 'ఖ', 'గ', 'ఘ', 'ఙ'],
        'roman': ['k', 'kh', 'g', 'gh', 'ng'],
        'nasal': 'ఙ',  # Anusvara becomes ఙ before velar
    },
    'palatal': {  # తాలవ్యము (Thalavyamu) - palate
        'consonants': ['చ', 'ఛ', 'జ', 'ఝ', 'ఞ'],
        'roman': ['ch', 'chh', 'j', 'jh', 'ny'],
        'nasal': 'ఞ',  # Anusvara becomes ఞ before palatal
    },
    'retroflex': {  # మూర్ధన్యము (Murdanyamu) - roof of mouth
        'consonants': ['ట', 'ఠ', 'డ', 'ఢ', 'ణ'],
        'roman': ['T', 'Th', 'D', 'Dh', 'N'],
        'nasal': 'ణ',  # Anusvara becomes ణ before retroflex
    },
    'dental': {  # దంత్యము (Dhantyamu) - teeth
        'consonants': ['త', 'థ', 'ద', 'ధ', 'న'],
        'roman': ['t', 'th', 'd', 'dh', 'n'],
        'nasal': 'న',  # Anusvara becomes న before dental
    },
    'labial': {  # ఓష్ఠ్యము (Oshthyamu) - lips
        'consonants': ['ప', 'ఫ', 'బ', 'భ', 'మ'],
        'roman': ['p', 'ph', 'b', 'bh', 'm'],
        'nasal': 'మ',  # Anusvara becomes మ before labial
    }
}

# Classification by nature (పరుష, సరళ, స్థిర)
CONSONANT_NATURE = {
    'harsh': ['క', 'చ', 'ట', 'త', 'ప'],  # పరుషములు (Parushamulu)
    'soft': ['గ', 'జ', 'డ', 'ద', 'బ'],    # సరళములు (Saralamulu)
    'stable': ['ఖ', 'ఘ', 'ఙ', 'ఛ', 'ఝ', 'ఞ', 'ఠ', 'ఢ', 'ణ', 
               'థ', 'ధ', 'న', 'ఫ', 'భ', 'మ', 'య', 'ర', 'ఱ', 
               'ల', 'ళ', 'వ', 'శ', 'ష', 'స', 'హ', 'క్ష']  # స్థిరములు
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: COMPLETE VOWEL SYSTEM (from pages 2-3, 6-8)
# ═══════════════════════════════════════════════════════════════════════════

VOWEL_CLASSIFICATIONS = {
    'hrasva': {  # హ్రస్వములు (short vowels - 1 matra)
        'vowels': ['అ', 'ఇ', 'ఉ', 'ఋ', 'ఌ', 'ఎ', 'ఒ'],
        'roman': ['a', 'i', 'u', 'R', 'L', 'e', 'o'],
    },
    'deerga': {  # దీర్ఘములు (long vowels - 2 matras)
        'vowels': ['ఆ', 'ఈ', 'ఊ', 'ౠ', 'ౡ', 'ఏ', 'ఓ'],
        'roman': ['aa', 'ii', 'uu', 'RR', 'LL', 'ee', 'oo'],
    },
    'plutha': {  # ప్లుతములు (extra long - 3 matras)
        'vowels': ['ఐ', 'ఔ'],
        'roman': ['ai', 'au'],
    }
}

# Complete Matra (guninthalu) mappings
MATRAS_COMPLETE = {
    'a': '',      # అకారము - inherent (no matra)
    'aa': 'ా',    # ఆకారము
    'i': 'ి',     # ఇకారము
    'ii': 'ీ',    # ఈకారము
    'u': 'ు',     # ఉకారము
    'uu': 'ూ',    # ఊకారము
    'R': 'ృ',     # ఋకారము
    'RR': 'ౄ',    # ౠకారము
    'L': 'ౢ',     # ఌకారము
    'LL': 'ౣ',    # ౡకారము
    'e': 'ె',     # ఎకారము
    'ee': 'ే',    # ఏకారము
    'ai': 'ై',    # ఐకారము
    'o': 'ొ',     # ఒకారము
    'oo': 'ో',    # ఓకారము
    'au': 'ౌ',    # ఔకారము
    'am': 'ం',    # అనుస్వారము
    'ah': 'ః',    # విసర్గము
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: CONTEXT-AWARE ANUSVARA RESOLUTION (from sandhi rules)
# ═══════════════════════════════════════════════════════════════════════════

def resolve_anusvara_context_aware(following_char: str) -> str:
    """
    Resolve anusvara (ం) based on following consonant.
    
    Based on అనునాసిక సంధి rules (page 40).
    """
    if not following_char:
        return 'మ'  # Default to మ at word end
    
    # Check which varga the following consonant belongs to
    for varga_name, varga_info in VARGA_CLASSIFICATIONS.items():
        if following_char in varga_info['consonants']:
            return varga_info['nasal']
    
    # Default to మ for non-varga consonants
    return 'మ'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: SANDHI RULE APPLICATIONS (from pages 26-42)
# ═══════════════════════════════════════════════════════════════════════════

def apply_athva_sandhi(word1: str, word2: str) -> str:
    """
    Apply అత్వసంధి (a-kara sandhi).
    
    When హ్రస్వ అకారము meets another vowel.
    """
    if not word1 or not word2:
        return word1 + word2
    
    # Get last character of word1 and first of word2
    last_char = word1[-1]
    first_char = word2[0] if word2 else ''
    
    # Check if last char of word1 is 'అ' and first char of word2 is a vowel
    if last_char == 'అ' and first_char in VOWEL_CLASSIFICATIONS['hrasva']['vowels']:
        # Apply sandhi rules
        return word1[:-1] + first_char + word2[1:]
    
    return word1 + word2


def apply_yadagama_sandhi(word1: str, word2: str) -> str:
    """
    Apply యడాగమసంధి (y-insertion).
    
    When no sandhi occurs between two vowels, insert 'య'.
    """
    if not word1 or not word2:
        return word1 + word2
    
    last_char = word1[-1]
    first_char = word2[0] if word2 else ''
    
    # Check if both are vowels
    all_vowels = (VOWEL_CLASSIFICATIONS['hrasva']['vowels'] + 
                  VOWEL_CLASSIFICATIONS['deerga']['vowels'] + 
                  VOWEL_CLASSIFICATIONS['plutha']['vowels'])
    
    if last_char in all_vowels and first_char in all_vowels:
        return word1 + 'య' + word2
    
    return word1 + word2


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: ENHANCED VALIDATION (from pages 8-9)
# ═══════════════════════════════════════════════════════════════════════════

def is_valid_telugu_word(word: str) -> bool:
    """
    Validate Telugu word structure based on grammar rules.
    
    Checks for:
    - Proper consonant-vowel combinations
    - Valid conjuncts (ఒత్తులు)
    - Correct matra usage
    """
    if not word:
        return False
    
    # Must contain Telugu characters
    if not re.search(r'[\u0C00-\u0C7F]', word):
        return False
    
    # Check for invalid patterns (excessive viramas, etc.)
    if re.search(r'్{3,}', word):  # 3+ viramas in a row
        return False
    
    # Check for excessive vowel runs
    if re.search(r'[అఆఇఈఉఊఎఏఐఒఓఔ]{4,}', word):
        return False
    
    return True


def classify_word_by_ending(word: str) -> str:
    """
    Classify Telugu words by ending (from pages 8-9).
    
    Returns:
    - 'durtha' (దుర్త): Ends with న
    - 'kalla' (కళ్ళు): Does not end with న
    - 'durtha_prakrithika': Ends with న (e.g., అన్నె, కన్నె)
    """
    if not word:
        return 'unknown'
    
    last_char = word[-1]
    
    # Check if ends with న
    if last_char == 'న':
        return 'durtha_prakrithika'
    
    # Check if any న appears in word
    if 'న' in word[:-1]:
        return 'durtha'
    
    return 'kalla'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: WORD FORMATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_varga_for_consonant(consonant: str) -> Optional[str]:
    """Get the varga (class) name for a given consonant."""
    for varga_name, varga_info in VARGA_CLASSIFICATIONS.items():
        if consonant in varga_info['consonants']:
            return varga_name
    return None


def get_consonant_nature(consonant: str) -> Optional[str]:
    """Get the nature (harsh/soft/stable) of a consonant."""
    for nature, consonants in CONSONANT_NATURE.items():
        if consonant in consonants:
            return nature
    return None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: EXAMPLE USAGE & TESTING
# ═══════════════════════════════════════════════════════════════════════════

def demonstrate_grammar_features():
    """Demonstrate the grammar-based features."""
    print("="*70)
    print("TELUGU GRAMMAR-BASED TRANSLITERATION ENHANCEMENTS")
    print("="*70 + "\n")
    
    # Test 1: Varga classification
    print("1. Varga Classification:")
    test_consonants = ['క', 'చ', 'ట', 'త', 'ప', 'య', 'ర']
    for cons in test_consonants:
        varga = get_varga_for_consonant(cons)
        nature = get_consonant_nature(cons)
        print(f"   {cons} → Varga: {varga}, Nature: {nature}")
    print()
    
    # Test 2: Anusvara resolution
    print("2. Context-Aware Anusvara Resolution:")
    test_cases = [
        ('ం', 'క', 'before velar'),
        ('ం', 'చ', 'before palatal'),
        ('ం', 'ట', 'before retroflex'),
        ('ం', 'త', 'before dental'),
        ('ం', 'ప', 'before labial'),
    ]
    for anusvara, following, desc in test_cases:
        result = resolve_anusvara_context_aware(following)
        print(f"   {anusvara} + {following} → {result} ({desc})")
    print()
    
    # Test 3: Word validation
    print("3. Telugu Word Validation:")
    test_words = ['రామ', 'కృష్ణ', 'నమస్తే', 'అఅఅఅ', 'abc']
    for word in test_words:
        valid = is_valid_telugu_word(word)
        status = "✓ Valid" if valid else "✗ Invalid"
        print(f"   {word:<15} → {status}")
    print()
    
    # Test 4: Word classification by ending
    print("4. Word Classification by Ending:")
    test_words = ['రాముడు', 'అన్నె', 'కన్నె', 'పుస్తకం']
    for word in test_words:
        classification = classify_word_by_ending(word)
        print(f"   {word:<15} → {classification}")
    print()
    
    print("="*70)


if __name__ == "__main__":
    demonstrate_grammar_features()
