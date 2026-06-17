import os
from owlready2 import *

# Configurar o mapeamento da gUFO
PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))

# Carregar ontologia
print("Carregando a ontologia...")
onto = get_ontology(os.path.abspath("Ontologia_base.rdf")).load()
print("Ontologia carregada com sucesso!\n")

def run_query(title, query_str):
    print("=" * 80)
    print(f"CQ: {title}")
    print("=" * 80)
    try:
        results = list(default_world.sparql(query_str))
        print(f"Total de resultados: {len(results)}")
        if len(results) == 0:
            print("Nenhum resultado retornado.")
        for row in results:
            formatted_row = [
                x.name if hasattr(x, 'name') else str(x)
                for x in row
            ]
            print(" | ".join(formatted_row))
    except Exception as e:
        print(f"Erro ao executar a query: {e}")
    print("\n")

prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://example.com/school-ontology#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
"""

# CQ1: Quais critérios formais/estudantes são classificados como em recusa escolar (AbsentStudent)?
query_cq1 = prefixes + """
SELECT ?student ?days WHERE {
  ?student rdf:type :AbsentStudent .
  OPTIONAL { ?student :hasDaysAbsent ?days }
}
"""
print("--- 1. CONSULTANDO CQ1 SEM RACIOCINADOR ---")
run_query("CQ1 (Sem Raciocinador)", query_cq1)

# Executando o raciocinador HermiT para fazer a inferência e classificar os alunos equivalentes
print("Executando o raciocinador HermiT para inferência de classe equivalente...")
try:
    sync_reasoner_hermit()
    print("Raciocínio HermiT concluído com sucesso!\n")
except Exception as e:
    print(f"Erro ao executar o raciocinador: {e}\n")

print("--- 2. CONSULTANDO CQ1 APÓS O RACIOCINADOR ---")
run_query("CQ1 (Com Raciocinador)", query_cq1)


# CQ2: Quais motivos de ausência excluem a classificação de recusa escolar?
query_cq2 = prefixes + """
SELECT ?exclusionClass ?label WHERE {
  ?exclusionClass rdfs:subClassOf :ExcludedFactor .
  OPTIONAL { ?exclusionClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
run_query("CQ2: Motivos de ausência excludentes", query_cq2)


# CQ3: Quais agentes administrativos registram as ausências escolares?
query_cq3 = prefixes + """
SELECT ?agentClass ?label WHERE {
  ?agentClass rdfs:subClassOf :Person .
  OPTIONAL { ?agentClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
run_query("CQ3: Agentes administrativos (Subclasses de Person)", query_cq3)


# CQ4: Quais instrumentos documentais formalizam a transferência de informações?
query_cq4 = prefixes + """
SELECT ?docClass ?label WHERE {
  ?docClass rdfs:subClassOf :Document .
  OPTIONAL { ?docClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
run_query("CQ4: Instrumentos documentais (Subclasses de Document)", query_cq4)


# CQ5: Quais processos administrativos contabilizam a frequência em estruturas externas?
# Consulta que tenta encontrar estudantes participando de sessões alternativas e suas instalações
query_cq5 = prefixes + """
SELECT ?session ?student ?facility WHERE {
  ?student :studentStudiesAtSession ?session .
  ?session :facilityOccursInSession ?facility .
}
"""
run_query("CQ5: Relação de sessões de aprendizado alternativo e locais", query_cq5)

# CQ6: Quais eventos marcam transições de estado?
query_cq6 = prefixes + """
SELECT ?eventClass ?label WHERE {
  ?eventClass rdfs:subClassOf gufo:Event .
  OPTIONAL { ?eventClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
run_query("CQ6: Eventos de transição de estado", query_cq6)
