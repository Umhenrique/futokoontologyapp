document.addEventListener('DOMContentLoaded', () => {
    // Carregar opções iniciais
    loadOptions();
});

// Alternar entre abas de Povoamento
function switchTab(tabName) {
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Forms
    document.querySelectorAll('.tab-content').forEach(form => form.classList.remove('active'));
    document.getElementById(`form-${tabName}`).classList.add('active');
}

// Carregar dinamicamente dados do backend
async function loadOptions() {
    try {
        const response = await fetch('/api/options');
        if (!response.ok) throw new Error('Falha ao obter opções da ontologia.');
        const data = await response.json();

        // 1. Povoar dropdown de motivos excludentes (Estudante)
        const studentMotiveSelect = document.getElementById('student-motive');
        // Manter a primeira opção ("Nenhum")
        studentMotiveSelect.innerHTML = '<option value="None">Nenhum (Potencial Recusa Escolar)</option>';
        data.motives.forEach(motive => {
            const opt = document.createElement('option');
            opt.value = motive;
            opt.textContent = motive;
            studentMotiveSelect.appendChild(opt);
        });

        // 2. Povoar dropdown de estudantes (Sessão)
        const sessionStudentSelect = document.getElementById('session-student');
        sessionStudentSelect.innerHTML = '<option value="" disabled selected>Selecione um estudante...</option>';
        data.students.forEach(student => {
            const opt = document.createElement('option');
            opt.value = student.name;
            opt.textContent = `${student.name} (${student.days} faltas)`;
            sessionStudentSelect.appendChild(opt);
        });

        // 3. Povoar dropdown de instalações (Sessão)
        const sessionFacilitySelect = document.getElementById('session-facility');
        sessionFacilitySelect.innerHTML = '<option value="" disabled selected>Selecione um local...</option>';
        data.facilities.forEach(facility => {
            const opt = document.createElement('option');
            opt.value = facility;
            opt.textContent = facility;
            sessionFacilitySelect.appendChild(opt);
        });

        // 4. Renderizar a tabela de estudantes
        const tableBody = document.getElementById('students-table-body');
        tableBody.innerHTML = '';
        data.students.forEach(student => {
            const tr = document.createElement('tr');
            
            const tdName = document.createElement('td');
            tdName.textContent = student.name;
            tr.appendChild(tdName);

            const tdDays = document.createElement('td');
            tdDays.textContent = student.days;
            tr.appendChild(tdDays);

            const tdMotives = document.createElement('td');
            tdMotives.textContent = student.motives.length > 0 ? student.motives.join(', ') : 'Nenhum';
            tr.appendChild(tdMotives);

            tableBody.appendChild(tr);
        });

        // 5. Atualizar Estatísticas na Barra Inferior
        if (data.stats) {
            const statSts = document.getElementById('stat-students');
            const statCls = document.getElementById('stat-classes');
            const statRea = document.getElementById('stat-reasoners');
            const statCqs = document.getElementById('stat-cqs');
            
            if (statSts) statSts.textContent = data.stats.students_count;
            if (statCls) statCls.textContent = data.stats.classes_count;
            if (statRea) statRea.textContent = data.stats.reasoners_count;
            if (statCqs) statCqs.textContent = data.stats.cqs_count;
            
            const metaContainer = document.getElementById('stat-students-meta');
            if (metaContainer) {
                metaContainer.innerHTML = `<span class="trend-green">▲ ${data.stats.conformity_percentage}%</span> classificados`;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar opções:', error);
    }
}

// Submeter formulário de Novo Estudante
async function submitStudent(event) {
    event.preventDefault();
    const btn = document.getElementById('btn-submit-student');
    btn.disabled = true;

    const studentData = {
        name: document.getElementById('student-name').value,
        days_absent: parseInt(document.getElementById('student-days').value),
        motive: document.getElementById('student-motive').value
    };

    try {
        const response = await fetch('/api/add_student', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
        const result = await response.json();

        if (response.ok) {
            alert(result.success);
            document.getElementById('form-student').reset();
            await loadOptions(); // Recarregar dropdowns e tabela
        } else {
            alert(`Erro: ${result.error}`);
        }
    } catch (error) {
        alert(`Falha de comunicação: ${error.message}`);
    } finally {
        btn.disabled = false;
    }
}

// Submeter formulário de Nova Sessão Alternativa
async function submitSession(event) {
    event.preventDefault();
    const btn = document.getElementById('btn-submit-session');
    btn.disabled = true;

    const sessionData = {
        student_name: document.getElementById('session-student').value,
        facility_name: document.getElementById('session-facility').value,
        session_name: document.getElementById('session-name').value
    };

    try {
        const response = await fetch('/api/add_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sessionData)
        });
        const result = await response.json();

        if (response.ok) {
            alert(result.success);
            document.getElementById('form-session').reset();
            await loadOptions(); // Recarregar
        } else {
            alert(`Erro: ${result.error}`);
        }
    } catch (error) {
        alert(`Falha de comunicação: ${error.message}`);
    } finally {
        btn.disabled = false;
    }
}

// Rodar o Raciocinador HermiT
async function runReasoner() {
    const btn = document.getElementById('btn-run-reasoner');
    const btnText = document.getElementById('reasoner-btn-text');
    const spinner = document.getElementById('reasoner-spinner');
    const statusBox = document.getElementById('reasoner-status');

    // Estado Carregando
    btn.disabled = true;
    spinner.classList.remove('hidden');
    btnText.textContent = 'Executando HermiT...';
    statusBox.textContent = 'Processando consistência lógica e classificações equivalentes...';
    statusBox.className = 'status-box';

    try {
        const response = await fetch('/api/run_reasoner', { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            statusBox.textContent = result.success;
            statusBox.className = 'status-box success';
            await loadOptions(); // Recarregar dados após inferência
        } else {
            statusBox.textContent = result.error;
            statusBox.className = 'status-box error';
        }
    } catch (error) {
        statusBox.textContent = `Erro de rede: ${error.message}`;
        statusBox.className = 'status-box error';
    } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
        btnText.textContent = 'Rodar Raciocinador HermiT';
    }
}

// Executar Questão de Competência (CQ) individual
async function runCQ(cqNum) {
    const consoleOutput = document.getElementById('console-output');
    const consoleQuery = document.getElementById('console-query');
    const consoleBadge = document.getElementById('console-cq-num');

    consoleOutput.textContent = 'Buscando dados na ontologia...';
    consoleBadge.classList.remove('hidden');
    consoleBadge.textContent = `CQ${cqNum}`;

    // Adiciona classe de destaque visual ao card clicado
    document.querySelectorAll('.cq-card').forEach(card => card.classList.remove('active-cq'));
    document.getElementById(`cq-card-${cqNum}`).classList.add('active-cq');

    try {
        const response = await fetch('/api/run_cq', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cq_num: cqNum })
        });
        const data = await response.json();

        if (response.ok) {
            // Exibir a query SPARQL formatada
            consoleQuery.textContent = data.query;

            // Renderizar resultados
            if (data.results.length === 0) {
                consoleOutput.innerHTML = '<span style="color: var(--text-muted);">Nenhum resultado retornado.</span>';
                return;
            }

            // Construir tabela dinâmica com base nos resultados
            let tableHtml = '<table class="output-table"><thead><tr>';
            
            // Determinar nomes das colunas de acordo com a CQ
            let headers = [];
            if (cqNum === 1) headers = ['Estudante', 'Dias Ausentes'];
            else if (cqNum === 2) headers = ['Subclasse Excludente', 'Descrição em Português'];
            else if (cqNum === 3) headers = ['Papel Administrativo', 'Descrição em Português'];
            else if (cqNum === 4) headers = ['Documento', 'Descrição em Português'];
            else if (cqNum === 5) headers = ['Sessão Alternativa', 'Estudante', 'Instalação Externa'];
            else if (cqNum === 6) headers = ['Classe de Evento', 'Descrição em Português'];

            headers.forEach(h => {
                tableHtml += `<th>${h}</th>`;
            });
            tableHtml += '</tr></thead><tbody>';

            data.results.forEach(row => {
                tableHtml += 'tr';
                let rowHtml = '<tr>';
                row.forEach(cell => {
                    rowHtml += `<td>${cell !== 'None' ? cell : '<span style="color: rgba(255,255,255,0.25);">None</span>'}</td>`;
                });
                rowHtml += '</tr>';
                tableHtml += rowHtml;
            });
            tableHtml += '</tbody></table>';
            
            consoleOutput.innerHTML = tableHtml;
        } else {
            consoleOutput.textContent = `Erro na execução: ${data.error}`;
        }
    } catch (error) {
        consoleOutput.textContent = `Erro de conexão: ${error.message}`;
    }
}

// Controle de arquivo selecionado
let selectedFile = null;

function handleFileSelect(event) {
    const files = event.target.files;
    const fileMsg = document.getElementById('file-msg');
    const submitBtn = document.getElementById('btn-submit-upload');
    
    if (files.length > 0) {
        selectedFile = files[0];
        fileMsg.textContent = `Arquivo selecionado: ${selectedFile.name}`;
        submitBtn.disabled = false;
    } else {
        selectedFile = null;
        fileMsg.textContent = 'ou arraste e solte o PDF aqui';
        submitBtn.disabled = true;
    }
}

// Submeter upload de PDF
async function submitUpload(event) {
    if (!selectedFile) return;
    
    const btn = document.getElementById('btn-submit-upload');
    const fileMsg = document.getElementById('file-msg');
    
    btn.disabled = true;
    btn.textContent = 'Enviando e Povoando...';
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/api/upload_pdf', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(result.success);
            
            // Exibir preview
            const previewBox = document.getElementById('upload-preview');
            const dataList = document.getElementById('preview-data-list');
            
            previewBox.classList.remove('hidden');
            dataList.innerHTML = '';
            
            const fieldLabels = {
                "student_name": "Estudante",
                "gender": "Gênero",
                "school_name": "Escola",
                "grade": "Série/Ano",
                "class_name": "Turma",
                "homeroom_teacher": "Prof. Regente",
                "administrator": "Administrador",
                "absent_days": "Dias de Ausência",
                "support_facility": "Local de Apoio",
                "facility_type": "Tipo de Apoio"
            };
            
            for (const [key, value] of Object.entries(result.data)) {
                const li = document.createElement('li');
                li.innerHTML = `<span class="label">${fieldLabels[key] || key}:</span> <span class="value">${value}</span>`;
                dataList.appendChild(li);
            }
            
            // Resetar
            selectedFile = null;
            document.getElementById('pdf-file').value = '';
            fileMsg.textContent = 'ou arraste e solte o PDF aqui';
            
            // Recarregar os estudantes e opções na tela
            await loadOptions();
        } else {
            alert(`Erro: ${result.error}`);
        }
    } catch (error) {
        alert(`Falha na comunicação: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Confirmar & Popular Ontologia';
    }
}

// Configurar eventos de Drag & Drop quando o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('file-drop-area');
    if (dropArea) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.classList.remove('dragover');
            }, false);
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                const fileInput = document.getElementById('pdf-file');
                fileInput.files = files;
                handleFileSelect({ target: { files: files } });
            }
        }, false);
    }
});

