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
    print("=" * 70)
    print(f"TESTE: {title}")
    print("=" * 70)
    print("Query SPARQL:")
    print(query_str.strip())
    print("-" * 70)
    try:
        # Executar a query SPARQL
        # default_world.sparql() retorna um gerador de resultados (linhas contendo tuplas)
        results = list(default_world.sparql(query_str))
        print("Resultado: SUCESSO!")
        print(f"Total de linhas retornadas: {len(results)}")
        if len(results) == 0:
            print("Nenhum registro retornado.")
        else:
            # Imprime os resultados formatados
            for row in results:
                # Se for um objeto do Owlready, mostra apenas o nome curto (.name)
                formatted_row = [
                    x.name if hasattr(x, 'name') else str(x)
                    for x in row
                ]
                print(" | ".join(formatted_row))
    except Exception as e:
        print("Resultado: FALHA (Erro capturado com sucesso!)")
        print(f"Erro retornado: {e}")
    print("\n")

# PREFIXOS padrão para facilitar as consultas
prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://example.com/school-ontology#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
"""

# Teste 1: SELECT simples de Estudantes e seus dias de ausência
query1 = prefixes + """
SELECT ?student ?days
WHERE {
    ?student rdf:type :Student .
    ?student :hasDaysAbsent ?days .
}
"""
run_query("1. SELECT Simples (Lista de Estudantes e dias ausentes)", query1)

# Teste 2: FILTER (Apenas estudantes com mais de 10 dias ausentes)
query2 = prefixes + """
SELECT ?student ?days
WHERE {
    ?student rdf:type :Student .
    ?student :hasDaysAbsent ?days .
    FILTER(?days > 10)
}
"""
run_query("2. FILTER (Estudantes com mais de 10 dias ausentes)", query2)

# Teste 3: OPTIONAL (Estudantes com seus motivos de ausência se existirem)
query3 = prefixes + """
SELECT ?student ?days ?motive
WHERE {
    ?student rdf:type :Student .
    ?student :hasDaysAbsent ?days .
    OPTIONAL { ?student :hasAbsenceMotive ?motive . }
}
"""
run_query("3. OPTIONAL (Estudantes e seus motivos de ausência, se houver)", query3)

# Teste 4: AGGREGATION (Total de Estudantes e Média de dias ausentes)
query4 = prefixes + """
SELECT (COUNT(?student) AS ?total) (AVG(?days) AS ?avgDays)
WHERE {
    ?student rdf:type :Student .
    ?student :hasDaysAbsent ?days .
}
"""
run_query("4. AGGREGATION (Contagem de estudantes e média de faltas)", query4)

# Teste 5: Hierarquia de Classes (Subclasses de ExcludedFactor e rótulos em português)
query5 = prefixes + """
SELECT ?subclass ?label
WHERE {
    ?subclass rdfs:subClassOf :ExcludedFactor .
    OPTIONAL { ?subclass rdfs:label ?label . FILTER(lang(?label) = "pt-br") }
}
"""
run_query("5. Hierarquia de Classes (Subclasses de ExcludedFactor e seus rótulos)", query5)

# Teste 6: Query com ERRO sintático proposital para demonstrar como a falha ocorre
query_error = prefixes + """
SELECT ?student
WHERE {
    ?student rdf:type :Student 
    # Erro proposital: falta o ponto final e o fechamento da chave }
"""
run_query("6. Teste de erro sintático (SPARQL malformado)", query_error)
