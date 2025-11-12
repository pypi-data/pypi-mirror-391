# telugu_engine/cli_suggest_sentence.py
import argparse
from .suggest_sentence import sentence_variants, per_token_suggestions

def main():
    p = argparse.ArgumentParser(description="Sentence-level Telugu suggestions from Roman input")
    p.add_argument("text", nargs="+", help="Roman sentence")
    p.add_argument("--mode", choices=["topn", "tokens"], default="topn",
                   help="topn = N best full sentences; tokens = per-word lists")
    p.add_argument("--topn", type=int, default=5, help="N best sentence variants")
    p.add_argument("--per-word", type=int, default=4, help="Candidates per token")
    p.add_argument("--beam", type=int, default=6, help="Beam width")
    args = p.parse_args()
    text = " ".join(args.text)

    if args.mode == "tokens":
        lists = per_token_suggestions(text, limit=args.per_word)
        for i, lst in enumerate(lists, 1):
            print(f"[{i}] {', '.join(lst)}")
    else:
        outs = sentence_variants(text, topn=args.topn, per_word=args.per_word, beam=args.beam)
        for i, s in enumerate(outs, 1):
            print(f"{i}. {s}")