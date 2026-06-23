import os
from owlready2 import *

PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))
onto = get_ontology(os.path.abspath("Ontologia_base.rdf")).load()

print("--- Classes ---")
for cls in sorted(list(onto.classes()), key=lambda x: x.name):
    print(cls.name)

print("\n--- Object Properties ---")
for prop in sorted(list(onto.object_properties()), key=lambda x: x.name):
    print(f"{prop.name} (domain: {prop.domain}, range: {prop.range})")

print("\n--- Data Properties ---")
for prop in sorted(list(onto.data_properties()), key=lambda x: x.name):
    print(f"{prop.name} (domain: {prop.domain}, range: {prop.range})")
