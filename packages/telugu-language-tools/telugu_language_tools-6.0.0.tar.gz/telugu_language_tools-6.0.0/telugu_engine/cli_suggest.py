# telugu_engine/cli_suggest.py
import argparse
from .suggest import suggestions

def main():
    p = argparse.ArgumentParser(description="Telugu IME-like suggestions for a Roman word")
    p.add_argument("word", help="Roman word")
    p.add_argument("--limit", type=int, default=8, help="Max suggestions")
    args = p.parse_args()

    outs = suggestions(args.word, limit=args.limit)
    print("\nSuggestions:")
    for o in outs:
        print(" •", o)