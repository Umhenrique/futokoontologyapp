import os
from owlready2 import *

# Configurar o mapeamento da gUFO
PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))

# Carregar ontologia
print("Carregando a ontologia...")
onto = get_ontology(os.path.abspath("Ontologia_base.rdf")).load()
print("Ontologia carregada com sucesso!")

# Povoando a ontologia com indivíduos e relacionamentos
with onto:
    # 1. Recuperar indivíduos existentes
    shinji = onto["Ikari_Shinji"]
    ritsuko = onto["Akagi_Ritsuko"]
    gendo = onto["Ikari_Gendo"]
    misato = onto["Katsuragi_Misato"]
    fuyutsuki = onto["Fuyutsuki_Kouzou"]
    nerv = onto["Nerv"]
    gainax = onto["Gainax"]
    mext = onto["Central_Office_MEXT"]

    print("\nIndivíduos recuperados com sucesso:")
    print(f"- Estudante: {shinji.name}")
    print(f"- Conselheira: {ritsuko.name}")
    print(f"- Diretor/Pai: {gendo.name}")
    print(f"- Professora: {misato.name}")
    print(f"- Assistente Social: {fuyutsuki.name}")
    print(f"- Escola: {nerv.name}")
    print(f"- Escola Livre: {gainax.name}")
    print(f"- MEXT: {mext.name}")

    # 2. Criar novos indivíduos para o processo administrativo
    print("\nCriando novos indivíduos para o processo de Shinji...")
    
    # Equipe Escolar (TeamSchool)
    team_school = onto.TeamSchool("Nerv_TeamSchool")
    
    # Evento de Triagem (Screening) e seus documentos
    screening = onto.Screening("Screening_Shinji")
    support_sheet = onto.SupportSheet("SupportSheet_Shinji")
    activity_report = onto.ActivityReport("Report_Shinji")
    
    # Checkup Digital/SOS
    digital_checkup = onto.DigitalCheckupSOS("DigitalCheckup_Shinji")
    
    # Classificação de Recusa Escolar e seus fatores
    classification = onto.SchoolRefusalClassification("Classification_Shinji")
    absence_duration = onto.AbsenceDuration("AbsenceDuration_Shinji")
    psychosocial_factor = onto.PsychosocialFactor("PsychosocialFactor_Shinji")
    
    # Planejamento de Intervenção e Plano de Estudos
    intervention = onto.InterventionPlanning("Intervention_Shinji")
    study_plan = onto.StudyPlan("StudyPlan_Shinji")
    
    # Sessão de Aprendizagem Alternativa
    alternative_session = onto.AlternativeLearningSession("AlternativeLearningSession_Shinji")
    
    # Julgamento do Diretor e Histórico Escolar resultante
    directors_trial = onto.DirectorsTrial("Trial_Shinji")
    student_record = onto.StudentRecord("Record_Shinji")

    print("Indivíduos criados com sucesso!")

    # 3. Estabelecer os relacionamentos (Object Properties)
    print("\nAssociando os relacionamentos na ontologia...")

    # Membros da Equipe Escolar e associação com a Escola
    ritsuko.isMemberOfTeamSchool.append(team_school)
    misato.isMemberOfTeamSchool.append(team_school)
    fuyutsuki.isMemberOfTeamSchool.append(team_school)
    team_school.isComponentOfSchool.append(nerv)

    # Monitoramento do Aluno
    shinji.monitoredBy.append(team_school)

    # Participação no Screening
    ritsuko.participatesInScreening.append(screening)
    misato.participatesInScreening.append(screening)
    gendo.participatesInScreening.append(screening) # Como pai do Shinji
    shinji.participatesInScreening.append(screening)
    team_school.participatesInScreening.append(screening)

    # Documentos criados na Triagem
    support_sheet.sheetCreatedInScreening.append(screening)
    activity_report.reportCreatedInScreening.append(screening)

    # Gatilhos e Checkup Digital
    screening.triggers.append(digital_checkup)
    digital_checkup.performs.append(shinji)
    digital_checkup.informedBy.append(team_school)

    # Classificação de Recusa Escolar e Fatores
    shinji.studentParticipatesInRefusalClassification.append(classification)
    classification.comparativeAbsenceDuration.append(absence_duration)
    classification.comparativePsychosocial.append(psychosocial_factor)

    # Planejamento de Intervenção
    fuyutsuki.socialWorkerParticipatesInIntervention.append(intervention)
    support_sheet.sheetParticipatesInIntervention.append(intervention)
    study_plan.planCreatedInIntervention.append(intervention)

    # Sessão de Aprendizagem Alternativa
    shinji.studentStudiesAtSession.append(alternative_session)
    alternative_session.facilityOccursInSession.append(gainax)
    study_plan.planParticipatesInSession.append(alternative_session)

    # Julgamento do Diretor e entrega do documento
    gendo.directorParticipatesInTrial.append(directors_trial)
    study_plan.planParticipatesInTrial.append(directors_trial)
    student_record.recordCreatedInTrial.append(directors_trial)
    
    # Relação funcional (atribuição direta)
    student_record.deliveryTo = mext

    print("Relacionamentos associados com sucesso!")

# Salvar a ontologia populada de volta no arquivo
print("\nSalvando a ontologia de volta para Ontologia_base.rdf...")
onto.save(file=os.path.abspath("Ontologia_base.rdf"))
print("Ontologia salva com sucesso!")
