import os
import subprocess
from owlready2 import *

# Path configuration
ontology_dir = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python"
gufo_path = os.path.join(ontology_dir, "gufo_base.rdf")
ontology_path = os.path.join(ontology_dir, "Ontologia_base.rdf")

PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = gufo_path
onto_path.append(ontology_dir)

onto = get_ontology(ontology_path).load()

# Run manually to get output
import tempfile
import owlready2.reasoning

fd, name = tempfile.mkstemp(suffix=".owl")
os.close(fd)
try:
    print(f"Saving temporary ontology for reasoner to {name}...")
    onto.save(file=name)
    
    # Run HermiT
    hermit_jar = os.path.join(os.path.dirname(owlready2.reasoning.__file__), "hermit", "HermiT.jar")
    command = ["java", "-Xmx2000M", "-cp", f"{os.path.dirname(owlready2.reasoning.__file__)}/hermit;{hermit_jar}", "org.semanticweb.HermiT.cli.CommandLine", "-c", "-O", "-D", "-I", f"file:///{name.replace('\\', '/')}", "-Y"]
    print("Running command:", " ".join(command))
    res = subprocess.run(command, capture_output=True, text=True)
    print("\n--- HERMIT STDOUT ---")
    print(res.stdout)
    print("\n--- HERMIT STDERR ---")
    print(res.stderr)
finally:
    if os.path.exists(name):
        os.remove(name)
