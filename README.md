# FutokoOntology — Painel Administrativo de Recusa Escolar (SRO)

Este repositório contém a implementação da **Ontologia SRO (School Refusal Ontology)** baseada na fundamentação gUFO, projetada para modelar, povoar e validar as etapas do processo administrativo japonês relacionado ao fenômeno *Futoko* (recusa escolar).

O projeto conta com um **Painel Web Editorial Acadêmico** que permite a inserção interativa de dados (estudantes, sessões de aprendizado alternativo), o acionamento do motor de inferência (HermiT) e a auditoria de Questões de Competência (CQs) da ORSD individualmente.

---

## 1. Estrutura do Repositório

```text
├── app.py                  # Backend em Flask (API e rotas)
├── Ontologia_base.rdf      # Ontologia principal (SRO em formato RDF/XML)
├── gufo_base.rdf           # Ontologia gUFO local (convertida para RDF/XML compatível)
├── requirements.txt        # Dependências do Python
├── templates/
│   └── index.html          # Interface HTML5 semântica
├── static/
│   ├── style.css           # Folha de estilo (Design Editorial Acadêmico)
│   └── script.js           # Lógica JavaScript assíncrona (Fetch API)
├── populate_ontology.py    # Script utilitário para repovoar a base local via terminal
├── answer_cqs.py           # Script para executar as CQs diretamente no terminal
└── README.md               # Este arquivo
```

---

## 2. Requisitos Prévios

1.  **Python 3.10+** instalado na máquina.
2.  **Java JRE/JDK (versão 8 ou superior)** instalado e configurado na variável de ambiente `PATH` do sistema. O motor de inferência **HermiT** (utilizado pela biblioteca `owlready2`) é executado em Java e falhará se o comando `java` não estiver acessível no terminal.

---

## 3. Instalação e Configuração

Siga os passos abaixo para configurar o ambiente no computador da faculdade:

1.  **Clone o repositório ou baixe a pasta do projeto.**
2.  **Crie e ative um ambiente virtual (opcional, mas recomendado):**
    ```powershell
    # No Windows (PowerShell):
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    # No Linux/macOS:
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Instale as dependências listadas no `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 4. Como Executar

### Opção A: Pelo Painel Web Interativo (Recomendado)

1.  Inicie o servidor Flask:
    ```bash
    python app.py
    ```
2.  Abra o navegador no endereço local:
    **`http://127.0.0.1:5000`**
3.  **Fluxo de Teste Sugerido:**
    *   No painel **Povoamento Manual**, adicione um novo estudante (ex: `Rei_Ayanami_Test`) com mais de 30 dias de ausência e sem motivos excludentes.
    *   No card **Motor de Inferência (Reasoner)**, clique em **"Rodar Raciocinador HermiT"** para recalcular a classificação lógica.
    *   No painel de **Questões de Competência**, clique em **"Executar Consulta"** no card da **CQ1** (Classificação de Recusa Escolar). O estudante criado aparecerá no console como classificado em `AbsentStudent`.

### Opção B: Pelo Console de Linha de Comando

Se preferir rodar os scripts utilitários em lote diretamente no terminal:

*   Para povoar a base com um conjunto de teste inicial:
    ```bash
    python populate_ontology.py
    ```
*   Para rodar todas as Questões de Competência (CQs) sequencialmente no console:
    ```bash
    python answer_cqs.py
    ```

---

## 5. Questões de Competência (CQs) Validadas

O painel responde às seguintes questões de competência definidas no documento de requisitos (ORSD):
*   **CQ1:** Quais critérios formais/estudantes são classificados como em recusa escolar (`AbsentStudent`)?
*   **CQ2:** Quais motivos de ausência excluem a classificação de recusa escolar? (Subclasses de `ExcludedFactor`).
*   **CQ3:** Quais agentes administrativos registram ou atuam nas ausências? (Subclasses de `Person`).
*   **CQ4:** Quais instrumentos documentais formalizam a transferência de informações? (Subclasses de `Document`).
*   **CQ5:** Quais processos administrativos e locais externos contabilizam a frequência?
*   **CQ6:** Quais eventos marcam transições de estado no processo de suporte? (Subclasses de `gufo:Event`).
