import os
from flask import Flask, jsonify, render_template, request
from owlready2 import *
from werkzeug.utils import secure_filename
import pdf_parser

app = Flask(__name__)

# Configurar o mapeamento da gUFO
PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))

# Carregar ontologia com isolamento por World
def load_ontology():
    w = World()
    # Mapear e carregar a gUFO localmente para evitar download remoto
    w.get_ontology("http://purl.org/nemo/gufo#/1.0.0").load(fileobj=open(os.path.abspath("gufo_base.rdf"), "rb"))
    onto = w.get_ontology("file://" + os.path.abspath("Ontologia_base.rdf").replace("\\", "/")).load()
    return onto, w

# Prefixo padrão para consultas SPARQL
prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://example.com/school-ontology#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        onto, w = load_ontology()
        
        # 1. Recuperar instalações de aprendizado (indivíduos ou classes)
        facilities = []
        learning_facility_cls = onto["LearningFacility"]
        if learning_facility_cls:
            for subclass in learning_facility_cls.subclasses():
                for inst in subclass.instances():
                    if isinstance(inst, ThingClass):
                        continue
                    if inst.name not in facilities:
                        facilities.append(inst.name)
            for inst in learning_facility_cls.instances():
                if isinstance(inst, ThingClass):
                    continue
                if inst.name not in facilities:
                    facilities.append(inst.name)
                
        # 2. Recuperar motivos de exclusão (indivíduos das subclasses de ExcludedFactor)
        motives = []
        excluded_factor_cls = onto["ExcludedFactor"]
        if excluded_factor_cls:
            for subclass in excluded_factor_cls.subclasses():
                for inst in subclass.instances():
                    if isinstance(inst, ThingClass):
                        continue
                    if inst.name not in motives:
                        motives.append(inst.name)
            for inst in excluded_factor_cls.instances():
                if isinstance(inst, ThingClass):
                    continue
                if inst.name not in motives:
                    motives.append(inst.name)

        # 3. Recuperar estudantes existentes e seus dias de ausência
        students = []
        student_cls = onto["Student"]
        if student_cls:
            for s in student_cls.instances():
                if isinstance(s, ThingClass):
                    continue
                days = s.hasDaysAbsent[0] if s.hasDaysAbsent else 0
                if not isinstance(days, (int, float)):
                    try:
                        days = int(days)
                    except:
                        days = str(days)
                # Obter motivos
                motive_names = [m.name for m in s.hasAbsenceMotive]
                students.append({
                    "name": s.name,
                    "days": days,
                    "motives": motive_names
                })

        # 4. Calcular Estatísticas Dinâmicas para a barra inferior
        classes_count = len(list(onto.classes()))
        
        absent_student_cls = onto["AbsentStudent"]
        regular_student_cls = onto["RegularStudent"]
        
        absent_instances = set(absent_student_cls.instances()) if absent_student_cls else set()
        regular_instances = set(regular_student_cls.instances()) if regular_student_cls else set()
        
        # Filtrar apenas indivíduos reais (ignorar metaclasses punadas)
        absent_instances = {x for x in absent_instances if not isinstance(x, ThingClass)}
        regular_instances = {x for x in regular_instances if not isinstance(x, ThingClass)}
        
        total_students_count = len(students)
        classified_count = len(absent_instances.union(regular_instances))
        conformity_percentage = int((classified_count / total_students_count) * 100) if total_students_count > 0 else 0

        return jsonify({
            "facilities": sorted(facilities),
            "motives": sorted(motives),
            "students": students,
            "stats": {
                "students_count": total_students_count,
                "classes_count": classes_count,
                "reasoners_count": 1,
                "cqs_count": 6,
                "conformity_percentage": conformity_percentage
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add_student', methods=['POST'])
def add_student():
    try:
        data = request.json
        name = data.get('name', '').strip()
        days_absent = data.get('days_absent')
        motive = data.get('motive')

        if not name:
            return jsonify({"error": "Nome do estudante é obrigatório."}), 400
        if days_absent is None:
            return jsonify({"error": "Dias de ausência são obrigatórios."}), 400

        onto, w = load_ontology()
        
        with onto:
            # Verificar se já existe
            if onto[name] is not None:
                return jsonify({"error": f"O indivíduo '{name}' já existe na ontologia."}), 400
            
            # Criar estudante
            new_student = onto.Student(name)
            new_student.hasDaysAbsent.append(int(days_absent))
            
            # Associar motivo se houver
            if motive and motive != "None":
                motive_individual = onto[motive]
                if motive_individual:
                    new_student.hasAbsenceMotive.append(motive_individual)
            else:
                # Fechar o mundo para o motivo de ausência (Open World Assumption):
                # declara explicitamente que o estudante não possui motivos excludentes.
                negation_motive = Not(onto.hasAbsenceMotive.some(onto.ExcludedFactor))
                if negation_motive not in new_student.is_a:
                    new_student.is_a.append(negation_motive)
            
            # Novo estudante adicionado manualmente não possui de início sessão/registro escolar,
            # então fechamos a OWA para o registro escolar entregue ao MEXT.
            negation_record = Not(onto.hasStudentRecord.some(onto.StudentRecord & onto.deliveryTo.value(onto["Central_Office_MEXT"])))
            if negation_record not in new_student.is_a:
                new_student.is_a.append(negation_record)
            
            # Salvar ontologia
            onto.save(file=os.path.abspath("Ontologia_base.rdf"))
            
        return jsonify({"success": f"Estudante '{name}' adicionado com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add_session', methods=['POST'])
def add_session():
    try:
        data = request.json
        student_name = data.get('student_name')
        facility_name = data.get('facility_name')
        session_name = data.get('session_name', '').strip()

        if not student_name or not facility_name or not session_name:
            return jsonify({"error": "Estudante, local e nome da sessão são obrigatórios."}), 400

        onto, w = load_ontology()

        with onto:
            # Verificar se a sessão já existe
            if onto[session_name] is not None:
                return jsonify({"error": f"A sessão '{session_name}' já existe."}), 400

            student = onto[student_name]
            facility = onto[facility_name]

            if not student:
                return jsonify({"error": f"Estudante '{student_name}' não encontrado."}), 404
            if not facility:
                return jsonify({"error": f"Instalação '{facility_name}' não encontrada."}), 404

            # Criar a sessão de aprendizado alternativo
            session = onto.AlternativeLearningSession(session_name)
            
            # Criar um plano de estudos padrão para associar à sessão e amarrar o fluxo
            study_plan_name = f"Plan_{session_name}"
            study_plan = onto.StudyPlan(study_plan_name)
            
            # Criar um julgamento de diretor correspondente
            trial_name = f"Trial_{session_name}"
            directors_trial = onto.DirectorsTrial(trial_name)
            
            # Criar um histórico escolar correspondente
            record_name = f"Record_{session_name}"
            student_record = onto.StudentRecord(record_name)

            # Associar relações
            student.studentStudiesAtSession.append(session)
            session.facilityOccursInSession.append(facility)
            study_plan.planParticipatesInSession.append(session)
            
            # Relações do Julgamento do Diretor
            study_plan.planParticipatesInTrial.append(directors_trial)
            student_record.recordCreatedInTrial.append(directors_trial)
            
            # Mapear entrega do registro para o MEXT (atribuição direta/funcional)
            mext = onto["Central_Office_MEXT"]
            if mext:
                student_record.deliveryTo = mext

            # Se a sessão for registrada, o estudante passa a ter registro escolar entregue ao MEXT.
            # Removemos a negação da OWA do registro escolar se ela existir.
            negation_record = Not(onto.hasStudentRecord.some(onto.StudentRecord & onto.deliveryTo.value(onto["Central_Office_MEXT"])))
            if negation_record in student.is_a:
                student.is_a.remove(negation_record)

            # Salvar ontologia
            onto.save(file=os.path.abspath("Ontologia_base.rdf"))

        return jsonify({"success": f"Sessão '{session_name}' e fluxos associados criados com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run_reasoner', methods=['POST'])
def run_reasoner():
    try:
        onto, w = load_ontology()
        # 1. Executar HermiT no mundo isolado
        sync_reasoner_hermit(w)
        
        # 2. Capturar classificações conceituais dos estudantes
        inferred = {}
        for s in onto.individuals():
            inferred[s.name] = [
                cls.name for cls in s.is_a
                if hasattr(cls, 'name') and cls.name in ['AbsentStudent', 'RegularStudent']
            ]
            
        # 3. Recarregar em um novo World limpo para forçar gravação física no RDF
        clean_onto, clean_w = load_ontology()
        for name, classes in inferred.items():
            s = clean_onto[name]
            if s:
                for cls_name in classes:
                    cls = clean_onto[cls_name]
                    if cls not in s.is_a:
                        with clean_onto:
                            s.is_a.append(cls)
                            
        # 4. Salvar as inferências persistidas no arquivo físico
        clean_onto.save(file=os.path.abspath("Ontologia_base.rdf"))
        
        return jsonify({"success": "Raciocínio HermiT concluído com sucesso e inferências salvas!"})
    except Exception as e:
        return jsonify({"error": f"Falha no Raciocinador: {str(e)}"}), 500

@app.route('/api/run_cq', methods=['POST'])
def run_cq():
    try:
        data = request.json
        cq_num = data.get('cq_num')

        queries = {
            1: prefixes + """
                SELECT ?student ?days WHERE {
                  ?student rdf:type :AbsentStudent .
                  OPTIONAL { ?student :hasDaysAbsent ?days }
                }
            """,
            2: prefixes + """
                SELECT ?exclusionClass ?label WHERE {
                  ?exclusionClass rdfs:subClassOf :ExcludedFactor .
                  OPTIONAL { ?exclusionClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
                }
            """,
            3: prefixes + """
                SELECT ?agentClass ?label WHERE {
                  ?agentClass rdfs:subClassOf :Person .
                  OPTIONAL { ?agentClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
                }
            """,
            4: prefixes + """
                SELECT ?docClass ?label WHERE {
                  ?docClass rdfs:subClassOf :Document .
                  OPTIONAL { ?docClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
                }
            """,
            5: prefixes + """
                SELECT ?session ?student ?facility WHERE {
                  ?student :studentStudiesAtSession ?session .
                  ?session :facilityOccursInSession ?facility .
                }
            """,
            6: prefixes + """
                SELECT ?eventClass ?label WHERE {
                  ?eventClass rdfs:subClassOf gufo:Event .
                  OPTIONAL { ?eventClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
                }
            """
        }

        query = queries.get(cq_num)
        if not query:
            return jsonify({"error": "Questão de Competência inválida."}), 400

        onto, w = load_ontology()  # Garantir carregamento mais recente das inferências
        
        results = list(w.sparql(query))
        
        # Formatar a tabela de saída
        formatted_results = []
        for row in results:
            formatted_row = [
                x.name if hasattr(x, 'name') else str(x)
                for x in row
            ]
            formatted_results.append(formatted_row)

        return jsonify({
            "query": query.strip(),
            "results": formatted_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado."}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado."}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Apenas arquivos PDF são suportados."}), 400
            
        # Garantir diretório de upload
        upload_dir = os.path.join(os.path.abspath("."), "scratch", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Parse PDF
        data = pdf_parser.parse_pdf_form(filepath)
        
        # Limpar arquivo temporário
        if os.path.exists(filepath):
            os.remove(filepath)
            
        # Popular ontologia
        onto, w = load_ontology()
        
        student_name = data.get("student_name", "").strip()
        school_name = data.get("school_name", "").strip()
        homeroom_teacher = data.get("homeroom_teacher", "").strip()
        administrator = data.get("administrator", "").strip()
        absent_days = data.get("absent_days", 30)
        support_facility = data.get("support_facility", "").strip()
        facility_type = data.get("facility_type", "EducationSupportCenter").strip()
        
        if not student_name or student_name == "Unknown Student":
            return jsonify({"error": "Não foi possível extrair o nome do estudante do PDF."}), 400
            
        with onto:
            # Normalizar IDs
            student_id = student_name.replace(" ", "_")
            school_id = school_name.replace(" ", "_") if school_name else "Unknown_School"
            teacher_id = homeroom_teacher.replace(" ", "_") if homeroom_teacher else "Unknown_Teacher"
            admin_id = administrator.replace(" ", "_") if administrator else "Unknown_Administrator"
            
            # Criar/recuperar entidades
            student = onto[student_id]
            if student is None:
                student = onto.Student(student_id)
            student.hasDaysAbsent = [int(absent_days)]

            # Fechar o mundo para o motivo de ausência (Open World Assumption):
            # declara explicitamente que o estudante não possui motivos excludentes.
            negation_motive = Not(onto.hasAbsenceMotive.some(onto.ExcludedFactor))
            if negation_motive not in student.is_a:
                student.is_a.append(negation_motive)
                
            # Se não houver local de apoio (não foi matriculado em centro de apoio),
            # o estudante não possui um registro escolar entregue ao MEXT.
            # Fechamos a OWA para o registro escolar correspondente.
            negation_record = Not(onto.hasStudentRecord.some(onto.StudentRecord & onto.deliveryTo.value(onto["Central_Office_MEXT"])))
            if not support_facility:
                if negation_record not in student.is_a:
                    student.is_a.append(negation_record)
            else:
                # Se tiver local de apoio, removemos a negação (se existir) para permitir a classificação como RegularStudent
                if negation_record in student.is_a:
                    student.is_a.remove(negation_record)
            
            school = onto[school_id]
            if school is None:
                school = onto.School(school_id)
                
            teacher = onto[teacher_id]
            if teacher is None:
                teacher = onto.Teacher(teacher_id)
                
            director = onto[admin_id]
            if director is None:
                director = onto.Director(admin_id)
                
            # TeamSchool
            team_id = f"{school_id}_TeamSchool"
            team_school = onto[team_id]
            if team_school is None:
                team_school = onto.TeamSchool(team_id)
                
            # Links de estrutura escolar
            if school not in team_school.isComponentOfSchool:
                team_school.isComponentOfSchool.append(school)
            if team_school not in teacher.isMemberOfTeamSchool:
                teacher.isMemberOfTeamSchool.append(team_school)
            if team_school not in student.monitoredBy:
                student.monitoredBy.append(team_school)
                
            # Screening
            screening_id = f"Screening_{student_id}"
            screening = onto[screening_id]
            if screening is None:
                screening = onto.Screening(screening_id)
            if screening not in student.participatesInScreening:
                student.participatesInScreening.append(screening)
            if screening not in teacher.participatesInScreening:
                teacher.participatesInScreening.append(screening)
            if screening not in team_school.participatesInScreening:
                team_school.participatesInScreening.append(screening)
                
            # SupportSheet
            sheet_id = f"SupportSheet_{student_id}"
            support_sheet = onto[sheet_id]
            if support_sheet is None:
                support_sheet = onto.SupportSheet(sheet_id)
            if screening not in support_sheet.sheetCreatedInScreening:
                support_sheet.sheetCreatedInScreening.append(screening)
                
            # ActivityReport
            report_id = f"Report_{student_id}"
            activity_report = onto[report_id]
            if activity_report is None:
                activity_report = onto.ActivityReport(report_id)
            if screening not in activity_report.reportCreatedInScreening:
                activity_report.reportCreatedInScreening.append(screening)
                
            # Se tiver instalação de apoio, preencher o fluxo de intervenção e acompanhamento
            if support_facility:
                facility_id = support_facility.replace(" ", "_")
                facility_cls = onto[facility_type]
                if facility_cls is None:
                    facility_cls = onto.EducationSupportCenter
                
                facility = onto[facility_id]
                if facility is None:
                    facility = facility_cls(facility_id)
                    
                # Intervention
                intervention_id = f"Intervention_{student_id}"
                intervention = onto[intervention_id]
                if intervention is None:
                    intervention = onto.InterventionPlanning(intervention_id)
                if intervention not in support_sheet.sheetParticipatesInIntervention:
                    support_sheet.sheetParticipatesInIntervention.append(intervention)
                    
                # StudyPlan
                study_plan_id = f"StudyPlan_{student_id}"
                study_plan = onto[study_plan_id]
                if study_plan is None:
                    study_plan = onto.StudyPlan(study_plan_id)
                if intervention not in study_plan.planCreatedInIntervention:
                    study_plan.planCreatedInIntervention.append(intervention)
                    
                # AlternativeLearningSession
                session_id = f"AlternativeLearningSession_{student_id}"
                session = onto[session_id]
                if session is None:
                    session = onto.AlternativeLearningSession(session_id)
                if session not in student.studentStudiesAtSession:
                    student.studentStudiesAtSession.append(session)
                if facility not in session.facilityOccursInSession:
                    session.facilityOccursInSession.append(facility)
                if session not in study_plan.planParticipatesInSession:
                    study_plan.planParticipatesInSession.append(session)
                    
                # DirectorsTrial
                trial_id = f"Trial_{student_id}"
                directors_trial = onto[trial_id]
                if directors_trial is None:
                    directors_trial = onto.DirectorsTrial(trial_id)
                if directors_trial not in study_plan.planParticipatesInTrial:
                    study_plan.planParticipatesInTrial.append(directors_trial)
                if directors_trial not in director.directorParticipatesInTrial:
                    director.directorParticipatesInTrial.append(directors_trial)
                    
                # StudentRecord
                record_id = f"Record_{student_id}"
                student_record = onto[record_id]
                if student_record is None:
                    student_record = onto.StudentRecord(record_id)
                if directors_trial not in student_record.recordCreatedInTrial:
                    student_record.recordCreatedInTrial.append(directors_trial)
                    
                # Entregar ao MEXT para disparar a transição de AbsentStudent para RegularStudent
                mext = onto["Central_Office_MEXT"]
                if mext:
                    student_record.deliveryTo = mext
                    
            # Salvar ontologia
            onto.save(file=os.path.abspath("Ontologia_base.rdf"))
            
        return jsonify({
            "success": f"Ontologia populada com sucesso a partir do documento de '{student_name}'!",
            "data": data
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro no processamento do arquivo: {str(e)}"}), 500

@app.route('/api/download_fillable', methods=['GET'])
def download_fillable():
    try:
        pdf_path = os.path.abspath("docs/Student Understanding Model Sheet - Fillable (English).pdf")
        if not os.path.exists(pdf_path):
            import subprocess
            subprocess.run(["python", "docs/generate_fillable_pdf.py"], check=True)
            
        from flask import send_file
        return send_file(pdf_path, as_attachment=True, download_name="Student_Understanding_Model_Sheet_Fillable.pdf")
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar ou baixar o PDF preenchível: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
