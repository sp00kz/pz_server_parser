#!/usr/bin/env python3
"""Validate every parsed dataset in work/ against pzschema. Exit 0 = all conform, 1 = problems."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pzschema

def main():
    problems = pzschema.validate_all()
    for name in pzschema.DATASETS:
        if name in problems:
            errs = problems[name]
            print(f"FAIL {name}: {len(errs)} violation(s)")
            for e in errs[:25]:
                print(f"     {e}")
            if len(errs) > 25:
                print(f"     ... {len(errs)-25} more")
        else:
            recs = pzschema.records(name, validate=False)
            print(f"ok   {name}: {len(recs)} records, {len(pzschema.DATASETS[name].fields)} fields")
    print("\n" + ("ALL DATASETS CONFORM" if not problems else f"{len(problems)} DATASET(S) WITH VIOLATIONS"))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
