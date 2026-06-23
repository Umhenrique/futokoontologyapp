import sys
import os
sys.path.append(os.path.abspath("."))
from app import load_ontology
from owlready2 import *

onto, w = load_ontology()
sync_reasoner_hermit(w)

print("--- INDIVIDUAL CLASSIFICATIONS ---")
for s in onto.individuals():
    print(f"Individual: {s.name}")
    print(f"  Types: {s.is_a}")
    inferred_types = s.is_a
    # Filter for concept classes
    classes = []
    for cls in inferred_types:
        if hasattr(cls, "name"):
            classes.append(cls.name)
    print(f"  Concept Classes: {classes}")
