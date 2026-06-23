import os
from owlready2 import *

PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))
onto = get_ontology(os.path.abspath("Ontologia_base.rdf")).load()

print("--- Inspecting John_Doe ---")
john = onto["John_Doe"]
if john is None:
    print("John_Doe not found!")
    exit(1)

print(f"Name: {john.name}")
print(f"Type: {[x.name for x in john.is_a if hasattr(x, 'name')]}")
print(f"hasDaysAbsent: {john.hasDaysAbsent}")
print(f"monitoredBy: {[x.name for x in john.monitoredBy]}")
print(f"participatesInScreening: {[x.name for x in john.participatesInScreening]}")
print(f"studentStudiesAtSession: {[x.name for x in john.studentStudiesAtSession]}")

print("\n--- Inspecting associated documents ---")
sheet = onto[f"SupportSheet_John_Doe"]
if sheet:
    print(f"SupportSheet: {sheet.name}")
    print(f"  sheetCreatedInScreening: {[x.name for x in sheet.sheetCreatedInScreening]}")
    print(f"  sheetParticipatesInIntervention: {[x.name for x in sheet.sheetParticipatesInIntervention]}")

report = onto[f"Report_John_Doe"]
if report:
    print(f"ActivityReport: {report.name}")
    print(f"  reportCreatedInScreening: {[x.name for x in report.reportCreatedInScreening]}")

study_plan = onto[f"StudyPlan_John_Doe"]
if study_plan:
    print(f"StudyPlan: {study_plan.name}")
    print(f"  planCreatedInIntervention: {[x.name for x in study_plan.planCreatedInIntervention]}")
    print(f"  planParticipatesInSession: {[x.name for x in study_plan.planParticipatesInSession]}")
    print(f"  planParticipatesInTrial: {[x.name for x in study_plan.planParticipatesInTrial]}")

record = onto[f"Record_John_Doe"]
if record:
    print(f"StudentRecord: {record.name}")
    print(f"  recordCreatedInTrial: {[x.name for x in record.recordCreatedInTrial]}")
    print(f"  deliveryTo: {record.deliveryTo.name if record.deliveryTo else None}")

print("\n--- Running HermiT Reasoner to see Inferred Classes ---")
with onto:
    sync_reasoner_hermit(infer_property_values=True)

print(f"\nAfter Reasoner - Inferred Classes for John_Doe: {[x.name for x in john.is_a if hasattr(x, 'name')]}")
print(f"  hasSupportSheet: {[x.name for x in john.hasSupportSheet]}")
print(f"  hasActivityReport: {[x.name for x in john.hasActivityReport]}")
print(f"  hasStudyPlan: {[x.name for x in john.hasStudyPlan]}")
print(f"  hasStudentRecord: {[x.name for x in john.hasStudentRecord]}")
