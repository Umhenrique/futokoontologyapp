"""
cqs_demo.py — Demonstração completa das CQs no modelo asserted e inferred

Cobre os 3 itens do Projeto 3:
  Tarefa 1 (4.0 pts): Tradução das CQs do ORSD em consultas SPARQL
  Tarefa 2 (3.0 pts): Consultas no modelo asserted (sem inferências)
  Tarefa 3 (3.0 pts): Consultas no modelo inferred (com HermiT)
"""

import os
from owlready2 import *

# ─────────────────────────────────────────────────────────────────────────────
# Configuração inicial
# ─────────────────────────────────────────────────────────────────────────────
PREDEFINED_ONTOLOGIES["http://purl.org/nemo/gufo#/1.0.0"] = os.path.abspath("gufo_base.rdf")
onto_path.append(os.path.abspath("."))

# Prefixos SPARQL padrão
PREFIXES = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX :     <http://example.com/school-ontology#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
"""

# ─────────────────────────────────────────────────────────────────────────────
# TAREFA 1: Tradução das CQs do ORSD em consultas SPARQL
# ─────────────────────────────────────────────────────────────────────────────
# As 6 queries abaixo são a tradução formal das Questões de Competência
# definidas no ORSD da ontologia SRO (School Refusal Ontology).

CQ1 = PREFIXES + """
SELECT ?student ?days WHERE {
  ?student rdf:type :AbsentStudent .
  OPTIONAL { ?student :hasDaysAbsent ?days }
}
"""
# Pergunta: Quais estudantes são classificados como em recusa escolar (Futoko)?
# AbsentStudent é uma classe equivalente inferida pelo HermiT com base em:
#   - hasDaysAbsent >= 30
#   - NOT hasAbsenceMotive some ExcludedFactor
#   - NOT hasStudentRecord some (StudentRecord and deliveryTo value Central_Office_MEXT)

CQ2 = PREFIXES + """
SELECT ?exclusionClass ?label WHERE {
  ?exclusionClass rdfs:subClassOf :ExcludedFactor .
  OPTIONAL { ?exclusionClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
# Pergunta: Quais motivos de ausência excluem a classificação de recusa escolar?

CQ3 = PREFIXES + """
SELECT ?agentClass ?label WHERE {
  ?agentClass rdfs:subClassOf :Person .
  OPTIONAL { ?agentClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
# Pergunta: Quais agentes administrativos registram ou atuam nas ausências escolares?

CQ4 = PREFIXES + """
SELECT ?docClass ?label WHERE {
  ?docClass rdfs:subClassOf :Document .
  OPTIONAL { ?docClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
# Pergunta: Quais instrumentos documentais formalizam a transferência de informações?

CQ5 = PREFIXES + """
SELECT ?session ?student ?facility WHERE {
  ?student :studentStudiesAtSession ?session .
  ?session :facilityOccursInSession ?facility .
}
"""
# Pergunta: Quais processos administrativos e locais externos contabilizam a frequência?

CQ6 = PREFIXES + """
SELECT ?eventClass ?label WHERE {
  ?eventClass rdfs:subClassOf gufo:Event .
  OPTIONAL { ?eventClass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
# Pergunta: Quais eventos marcam transições de estado no processo de suporte?

ALL_CQS = [
    ("CQ1 — Estudantes em recusa escolar (AbsentStudent)", CQ1),
    ("CQ2 — Motivos de ausência excludentes (ExcludedFactor)", CQ2),
    ("CQ3 — Agentes administrativos (subclasses de Person)", CQ3),
    ("CQ4 — Instrumentos documentais (subclasses de Document)", CQ4),
    ("CQ5 — Sessões de aprendizado alternativo e locais", CQ5),
    ("CQ6 — Eventos de transição de estado (subclasses de gufo:Event)", CQ6),
]


# ─────────────────────────────────────────────────────────────────────────────
# Função auxiliar de execução de queries
# ─────────────────────────────────────────────────────────────────────────────
def run_query(world, title, query_str):
    """Executa uma query SPARQL no world fornecido e imprime os resultados."""
    sep = "─" * 70
    print(sep)
    print(f"  {title}")
    print(sep)
    print("  Query SPARQL:")
    for line in query_str.strip().splitlines():
        print(f"    {line}")
    print()
    try:
        results = list(world.sparql(query_str))
        print(f"  → {len(results)} resultado(s) retornado(s):")
        if not results:
            print("    (nenhum resultado)")
        for row in results:
            formatted = [x.name if hasattr(x, "name") else str(x) for x in row]
            print("    " + " | ".join(formatted))
    except Exception as e:
        print(f"  ✗ Erro ao executar a query: {e}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TAREFA 2: Modelo Asserted (sem inferências)
# Consultas executadas ANTES do raciocinador — apenas fatos explícitos na base
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  TAREFA 2 — MODELO ASSERTED (sem inferências)                [3.0 pts]")
print("  Consultas retornam apenas fatos explicitamente declarados.")
print("  O raciocinador HermiT NÃO foi executado nesta seção.")
print("=" * 70)
print()

# Carregar em World isolado para o modelo asserted
w_asserted = World()
w_asserted.get_ontology("http://purl.org/nemo/gufo#/1.0.0").load(
    fileobj=open(os.path.abspath("gufo_base.rdf"), "rb")
)
onto_asserted = w_asserted.get_ontology(
    "file://" + os.path.abspath("Ontologia_base.rdf").replace("\\", "/")
).load()

for title, query in ALL_CQS:
    run_query(w_asserted, title, query)

print()
print("  NOTA sobre CQ1 no modelo asserted:")
print("  AbsentStudent é uma classe EQUIVALENTE — sua extensão só é populada")
print("  após a execução do raciocinador. Sem inferência, a query retorna vazio.")
print()


# ─────────────────────────────────────────────────────────────────────────────
# TAREFA 3: Modelo Inferred (com inferências do HermiT)
# Consultas executadas APÓS o raciocinador — inclui classificações inferidas
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  TAREFA 3 — MODELO INFERRED (com inferências HermiT)         [3.0 pts]")
print("  Consultas retornam fatos + classificações inferidas pelo reasoner.")
print("=" * 70)
print()

# Carregar em novo World isolado para o modelo inferred
w_inferred = World()
w_inferred.get_ontology("http://purl.org/nemo/gufo#/1.0.0").load(
    fileobj=open(os.path.abspath("gufo_base.rdf"), "rb")
)
onto_inferred = w_inferred.get_ontology(
    "file://" + os.path.abspath("Ontologia_base.rdf").replace("\\", "/")
).load()

print("  Executando raciocinador HermiT...")
try:
    sync_reasoner_hermit(w_inferred)
    print("  ✓ HermiT concluído com sucesso!\n")
except Exception as e:
    print(f"  ✗ Falha no raciocinador: {e}\n")

for title, query in ALL_CQS:
    run_query(w_inferred, title, query)

print()
print("  NOTA sobre CQ1 no modelo inferred:")
print("  Após o HermiT, estudantes com >= 30 dias de ausência, sem motivo")
print("  excludente e sem registro no MEXT são automaticamente classificados")
print("  como AbsentStudent — sem nenhuma declaração manual.")
print()
print("=" * 70)
print("  Demonstração concluída.")
print("=" * 70)
