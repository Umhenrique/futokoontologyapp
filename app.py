import os
from flask import Flask, jsonify, render_template, request
from owlready2 import *

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
                new_student.is_a.append(Not(onto.hasAbsenceMotive.some(onto.ExcludedFactor)))
            
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
