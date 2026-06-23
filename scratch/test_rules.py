import os
from owlready2 import *

# Path configuration
ontology_dir = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python"
gufo_path = os.path.join(ontology_dir, "gufo_base.rdf")
ontology_path = os.path.join(ontology_dir, "Ontologia_base.rdf")

# Configure predefined ontologies mapping for gUFO
PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = gufo_path
onto_path.append(ontology_dir)

print("Loading ontology...")
onto = get_ontology(ontology_path).load()

# Let's inspect the current equivalent_to of AbsentStudent
print("Original AbsentStudent equivalent_to:")
print(onto.AbsentStudent.equivalent_to)

# Now, let's update it in a with onto block
with onto:
    onto.AbsentStudent.equivalent_to = [
        onto.Student & 
        Not(onto.hasAbsenceMotive.some(onto.ExcludedFactor)) & 
        onto.hasDaysAbsent.some(ConstrainedDatatype(int, min_inclusive=30)) &
        Not(onto.hasStudentRecord.some(onto.StudentRecord & onto.deliveryTo.value(onto.Central_Office_MEXT)))
    ]

print("\nUpdated AbsentStudent equivalent_to:")
print(onto.AbsentStudent.equivalent_to)
