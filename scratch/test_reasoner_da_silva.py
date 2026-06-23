import sys
import os
sys.path.append(os.path.abspath("."))
from app import load_ontology
from owlready2 import *

onto, w = load_ontology()

student = onto["Estudante_Presente_Da_Silva"]
if student:
    # 1. Close motives
    negation_motive = Not(onto.hasAbsenceMotive.some(onto.ExcludedFactor))
    if negation_motive not in student.is_a:
        student.is_a.append(negation_motive)
        
    # 2. Close student record to MEXT
    negation_record = Not(onto.hasStudentRecord.some(onto.StudentRecord & onto.deliveryTo.value(onto.Central_Office_MEXT)))
    if negation_record not in student.is_a:
        student.is_a.append(negation_record)
    
    # Save
    onto.save(file=os.path.abspath("Ontologia_base.rdf"))

# Re-run reasoner on w
print("Running HermiT...")
sync_reasoner_hermit(w)

# Check classes
print("Classes of Estudante_Presente_Da_Silva after reasoning:", student.is_a)
for cls in student.is_a:
    if hasattr(cls, "name"):
        print(f"  Class name: {cls.name}")
