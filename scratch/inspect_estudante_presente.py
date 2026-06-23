import os
from owlready2 import *

PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))
onto = get_ontology(os.path.abspath("Ontologia_base.rdf")).load()

student_name = "Estudante_Presente_Da_Silva"
student = onto[student_name]

print(f"--- Checking {student_name} ---")
if student is None:
    print(f"Error: {student_name} not found in the ontology!")
    exit(1)

print(f"Name: {student.name}")
print(f"hasDaysAbsent: {student.hasDaysAbsent}")
print(f"monitoredBy: {[x.name for x in student.monitoredBy]}")
print(f"participatesInScreening: {[x.name for x in student.participatesInScreening]}")
print(f"is_a classes (Asserted): {[x.name for x in student.is_a if hasattr(x, 'name')]}")

# Run reasoner
with onto:
    sync_reasoner_hermit(infer_property_values=True)

print(f"is_a classes (Inferred): {[x.name for x in student.is_a if hasattr(x, 'name')]}")
