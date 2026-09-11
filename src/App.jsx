import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Plus, CheckCircle, FileText, QrCode, Camera, BarChart2, 
  Settings, Users, Upload, RefreshCw, Trash2, Edit, AlertTriangle, 
  Check, X, Download, Printer, LogOut, ArrowRight, ShieldCheck, Eye, Layers
} from 'lucide-react';

// ============================================================================
// BANCO DE DADOS EM MEMÓRIA (MOCK INICIAL)
// ============================================================================
const initialSemesters = [
  { id: 'sem_1', name: '2026.1', active: true },
  { id: 'sem_2', name: '2026.2', active: false },
];

const initialClasses = [
  { id: 'turma_1', name: 'Engenharia de Software - T1', semesterId: 'sem_1' },
  { id: 'turma_2', name: 'Ciências Contábeis - T2', semesterId: 'sem_1' },
];

const initialStudents = [
  { id: 'aluno_1', name: 'Carlos Eduardo', classId: 'turma_1', code: '2026101' },
  { id: 'aluno_2', name: 'Ana Maria Silva', classId: 'turma_1', code: '2026102' },
  { id: 'aluno_3', name: 'Beatriz Costa', classId: 'turma_2', code: '2026201' },
];

const initialQuestions = [
  {
    id: 'q1',
    statement: 'Qual das seguintes opções descreve corretamente o padrão de projeto Singleton?',
    options: {
      A: 'Garante que uma classe tenha apenas uma instância e fornece um ponto global de acesso a ela.',
      B: 'Converte a interface de uma classe em outra interface esperada pelos clientes.',
      C: 'Define uma dependência um-para-muitos entre objetos para que quando um mude, todos sejam notificados.',
      D: 'Permite separar a abstração da sua implementação para que ambas possam variar independentemente.'
    },
    correctAnswer: 'A',
    subject: 'Engenharia de Software',
    difficulty: 'Média'
  },
  {
    id: 'q2',
    statement: 'No ciclo de vida de desenvolvimento de software, qual fase envolve a identificação das necessidades dos stakeholders?',
    options: {
      A: 'Testes de Integração',
      B: 'Levantamento de Requisitos',
      C: 'Refatoração de Código',
      D: 'Implantação em Produção'
    },
    correctAnswer: 'B',
    subject: 'Engenharia de Software',
    difficulty: 'Fácil'
  },
  {
    id: 'q3',
    statement: 'Qual protocolo é utilizado primariamente para a comunicação segura e criptografada na Web?',
    options: {
      A: 'HTTP',
      B: 'FTP',
      C: 'HTTPS',
      D: 'SMTP'
    },
    correctAnswer: 'C',
    subject: 'Redes de Computadores',
    difficulty: 'Fácil'
  },
  {
    id: 'q4',
    statement: 'Em bancos de dados relacionais, o que garante a unicidade e identificação de um registro na tabela?',
    options: {
      A: 'Chave Estrangeira (FK)',
      B: 'Índice Secundário',
      C: 'Chave Primária (PK)',
      D: 'Triggers'
    },
    correctAnswer: 'C',
    subject: 'Banco de Dados',
    difficulty: 'Média'
  }
];

export default function App() {
  // Controle de Navegação e Estado Global
  const [currentUser, setCurrentUser] = useState(null); // null = não logado, 'teacher' = professor
  const [studentViewQR, setStudentViewQR] = useState(null); // Se preenchido, exibe a visão do aluno para a versão
  const [activeTab, setActiveTab] = useState('questions'); // Módulos do Professor

  // Estados dos Dados
  const [semesters, setSemesters] = useState(initialSemesters);
  const [classes, setClasses] = useState(initialClasses);
  const [students, setStudents] = useState(initialStudents);
  const [questions, setQuestions] = useState(initialQuestions);
  const [evaluations, setEvaluations] = useState([]);
  const [results, setResults] = useState([]);

  // Estados Temporários / Modais
  const [selectedSemester, setSelectedSemester] = useState('sem_1');
  const [csvPreview, setCsvPreview] = useState(null);
  const [filterSubject, setFilterSubject] = useState('');

  // Checar parâmetros de URL para consulta do aluno via QR Code
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const evalId = params.get('eval');
    const versionId = params.get('version');
    if (evalId && versionId) {
      setStudentViewQR({ evalId, versionId });
    }
  }, []);

  // Handler de login simulado
  const handleLogin = (e) => {
    e.preventDefault();
    setCurrentUser({ name: 'Prof. Anderson Silva', email: 'prof.anderson@instituicao.edu.br' });
  };

  // Logout
  const handleLogout = () => {
    setCurrentUser(null);
  };

  // ============================================================================
  // TELA DO ALUNO (ACESSO EXCLUSIVO VIA QR CODE - RF29, RF30, RN02-RN05)
  // ============================================================================
  if (studentViewQR) {
    const evaluation = evaluations.find(e => e.id === studentViewQR.evalId);
    const version = evaluation?.versions.find(v => v.id === studentViewQR.versionId);

    return (
      <div className="min-h-screen bg-slate-100 p-4 flex flex-col items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b">
            <div>
              <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Consulta de Gabarito</span>
              <h2 className="text-xl font-bold text-slate-800">{evaluation ? evaluation.title : 'Avaliação'}</h2>
            </div>
            <div className="bg-blue-100 text-blue-800 font-bold px-3 py-1 rounded-full text-sm">
              Versão: {version ? version.name : 'A'}
            </div>
          </div>

          <div className="bg-amber-50 border-l-4 border-amber-400 p-3 mb-6 rounded text-xs text-amber-800">
            <strong>Aviso:</strong> Esta consulta exibe apenas os gabaritos oficiais das alternativas corretas. Nenhuma resposta marcada ou nota individual é exibida por motivos de segurança.
          </div>

          {!version ? (
            <div className="text-center py-8 text-slate-500">
              <AlertTriangle className="mx-auto mb-2 text-amber-500" size={32} />
              Gabarito ou versão não localizada. Por favor, verifique se a avaliação já foi disponibilizada pelo professor.
            </div>
          ) : (
            <div className="space-y-3">
              <h3 className="font-semibold text-slate-700 mb-2">Gabarito Oficial:</h3>
              <div className="grid grid-cols-2 gap-2">
                {version.answerKey.map((item, index) => (
                  <div key={index} className="flex items-center justify-between bg-slate-50 border rounded p-2 text-sm">
                    <span className="font-medium text-slate-600">Questão {index + 1}</span>
                    <span className="font-bold bg-green-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
                      {item.correctAnswer}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button 
            onClick={() => { setStudentViewQR(null); window.history.replaceState({}, '', window.location.pathname); }}
            className="w-full mt-6 bg-slate-200 hover:bg-slate-300 text-slate-700 py-2 rounded-lg font-medium text-sm transition"
          >
            Voltar ao Inicio
          </button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // TELA DE LOGIN DO PROFESSOR (RF01, RN01)
  // ============================================================================
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="bg-blue-600 p-6 text-white text-center">
            <BookOpen size={48} className="mx-auto mb-2" />
            <h1 className="text-2xl font-bold">Portal do Professor</h1>
            <p className="text-blue-100 text-sm mt-1">Sistema de Automação e Correção de Avaliações</p>
          </div>

          <form onSubmit={handleLogin} className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">E-mail Institucional</label>
              <input 
                type="email" 
                required 
                defaultValue="prof.anderson@instituicao.edu.br"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-slate-800"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Senha de Acesso</label>
              <input 
                type="password" 
                required 
                defaultValue="123456"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-slate-800"
              />
            </div>
            <button 
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg transition duration-200 shadow"
            >
              Entrar no Sistema
            </button>
            <p className="text-xs text-center text-slate-500 mt-4">
              Acesso exclusivo para professores autenticados. Alunos devem utilizar a câmera para ler o QR Code da avaliação.
            </p>
          </form>
        </div>
      </div>
    );
  }

  // ============================================================================
  // PAINEL ADMINISTRATIVO DO PROFESSOR
  // ============================================================================
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* CABEÇALHO */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <BookOpen size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight">AvaliaMax</h1>
              <span className="text-xs text-slate-400">Geração & Correção Automática</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold">{currentUser.name}</p>
              <p className="text-xs text-slate-400">{currentUser.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
              title="Sair"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      {/* BARRA DE NAVEGAÇÃO PRINCIPAL */}
      <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 flex space-x-1 overflow-x-auto">
          {[
            { id: 'questions', label: 'Banco de Questões', icon: BookOpen },
            { id: 'evaluations', label: 'Avaliações & Provas', icon: FileText },
            { id: 'correction', label: 'Corrigir Provas (OMR)', icon: Camera },
            { id: 'results', label: 'Resultados & Relatórios', icon: BarChart2 },
            { id: 'academic', label: 'Semestres / Turmas', icon: Users }
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition ${
                  active 
                    ? 'border-blue-600 text-blue-600 bg-blue-50/50' 
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* CONTEÚDO PRINCIPAL */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6">
        {activeTab === 'questions' && (
          <QuestionsModule 
            questions={questions} 
            setQuestions={setQuestions}
            filterSubject={filterSubject}
            setFilterSubject={setFilterSubject}
          />
        )}

        {activeTab === 'evaluations' && (
          <EvaluationsModule 
            questions={questions} 
            evaluations={evaluations} 
            setEvaluations={setEvaluations}
            semesters={semesters}
            classes={classes}
            setStudentViewQR={setStudentViewQR}
          />
        )}

        {activeTab === 'correction' && (
          <CorrectionModule 
            evaluations={evaluations}
            students={students}
            results={results}
            setResults={setResults}
          />
        )}

        {activeTab === 'results' && (
          <ResultsModule 
            results={results}
            evaluations={evaluations}
            students={students}
            classes={classes}
          />
        )}

        {activeTab === 'academic' && (
          <AcademicManagementModule 
            semesters={semesters} setSemesters={setSemesters}
            classes={classes} setClasses={setClasses}
            students={students} setStudents={setStudents}
          />
        )}
      </main>
    </div>
  );
}

// ============================================================================
// MÓDULO 1: BANCO DE QUESTÕES (RF06 - RF13)
// ============================================================================
function QuestionsModule({ questions, setQuestions, filterSubject, setFilterSubject }) {
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // Form de questão manual
  const [formData, setFormData] = useState({
    statement: '',
    optionA: '', optionB: '', optionC: '', optionD: '',
    correctAnswer: 'A',
    subject: 'Geral',
    difficulty: 'Média'
  });

  const handleSaveQuestion = (e) => {
    e.preventDefault();
    if (editingQuestion) {
      setQuestions(questions.map(q => q.id === editingQuestion.id ? {
        ...q,
        statement: formData.statement,
        options: { A: formData.optionA, B: formData.optionB, C: formData.optionC, D: formData.optionD },
        correctAnswer: formData.correctAnswer,
        subject: formData.subject,
        difficulty: formData.difficulty
      } : q));
    } else {
      const newQ = {
        id: 'q_' + Date.now(),
        statement: formData.statement,
        options: { A: formData.optionA, B: formData.optionB, C: formData.optionC, D: formData.optionD },
        correctAnswer: formData.correctAnswer,
        subject: formData.subject,
        difficulty: formData.difficulty
      };
      setQuestions([...questions, newQ]);
    }
    setShowAddModal(false);
    resetForm();
  };

  const resetForm = () => {
    setFormData({ statement: '', optionA: '', optionB: '', optionC: '', optionD: '', correctAnswer: 'A', subject: 'Geral', difficulty: 'Média' });
    setEditingQuestion(null);
  };

  const handleEdit = (q) => {
    setEditingQuestion(q);
    setFormData({
      statement: q.statement,
      optionA: q.options.A, optionB: q.options.B, optionC: q.options.C, optionD: q.options.D,
      correctAnswer: q.correctAnswer,
      subject: q.subject || 'Geral',
      difficulty: q.difficulty || 'Média'
    });
    setShowAddModal(true);
  };

  const handleDelete = (id) => {
    if (confirm('Deseja realmente remover esta questão do banco?')) {
      setQuestions(questions.filter(q => q.id !== id));
    }
  };

  // Simulação de Importação CSV/Excel (RF10, RF11, RF12, RF13)
  const handleSimulateCSVImport = () => {
    const mockImported = [
      {
        statement: 'Qual o principal objetivo da validação de software?',
        optionA: 'Garantir que o software atenda às necessidades do cliente',
        optionB: 'Reduzir o custo de hardware',
        optionC: 'Acelerar a velocidade de navegação na web',
        optionD: 'Substituir a documentação',
        correctAnswer: 'A',
        subject: 'Engenharia de Software',
        difficulty: 'Fácil'
      },
      {
        statement: 'No MySQL, qual comando é utilizado para listar registros em uma tabela?',
        optionA: 'FETCH ALL',
        optionB: 'SELECT',
        optionC: 'GET DATA',
        optionD: 'SHOW RECORDS',
        correctAnswer: 'B',
        subject: 'Banco de Dados',
        difficulty: 'Fácil'
      }
    ];

    const newQuestions = mockImported.map((q, idx) => ({
      id: 'imp_' + Date.now() + '_' + idx,
      statement: q.statement,
      options: { A: q.optionA, B: q.optionB, C: q.optionC, D: q.optionD },
      correctAnswer: q.correctAnswer,
      subject: q.subject,
      difficulty: q.difficulty
    }));

    setQuestions([...questions, ...newQuestions]);
    setShowImportModal(false);
    alert('Importação concluída com sucesso! 2 questões adicionadas.');
  };

  const filteredQuestions = filterSubject 
    ? questions.filter(q => q.subject.toLowerCase().includes(filterSubject.toLowerCase()))
    : questions;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Banco de Questões</h2>
          <p className="text-sm text-slate-500">Cadastre, edite e importe questões de múltipla escolha.</p>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setShowImportModal(true)}
            className="flex items-center space-x-2 bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg font-medium text-sm transition"
          >
            <Upload size={16} />
            <span>Importar CSV/Excel</span>
          </button>
          <button 
            onClick={() => { resetForm(); setShowAddModal(true); }}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition"
          >
            <Plus size={16} />
            <span>Nova Questão</span>
          </button>
        </div>
      </div>

      {/* Filtro */}
      <div className="bg-white p-4 rounded-xl border border-slate-200">
        <input 
          type="text"
          placeholder="Filtrar por disciplina/categoria..."
          value={filterSubject}
          onChange={e => setFilterSubject(e.target.value)}
          className="w-full max-w-md border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Lista de Questões */}
      <div className="space-y-4">
        {filteredQuestions.map((q, index) => (
          <div key={q.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow transition">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-800">#{index + 1}</span>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full font-medium">{q.subject}</span>
                <span className="bg-slate-100 text-slate-600 text-xs px-2 py-0.5 rounded-full">{q.difficulty}</span>
              </div>
              <div className="flex items-center space-x-2">
                <button onClick={() => handleEdit(q)} className="p-1 text-slate-400 hover:text-blue-600 rounded">
                  <Edit size={16} />
                </button>
                <button onClick={() => handleDelete(q.id)} className="p-1 text-slate-400 hover:text-red-600 rounded">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            <p className="text-slate-800 font-medium mb-4">{q.statement}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              {['A', 'B', 'C', 'D'].map(letter => {
                const isCorrect = q.correctAnswer === letter;
                return (
                  <div 
                    key={letter}
                    className={`p-2.5 rounded-lg border flex items-center justify-between ${
                      isCorrect 
                        ? 'bg-green-50 border-green-300 text-green-900 font-medium' 
                        : 'bg-slate-50 border-slate-200 text-slate-700'
                    }`}
                  >
                    <span><strong>{letter})</strong> {q.options[letter]}</span>
                    {isCorrect && <Check size={16} className="text-green-600 ml-2 flex-shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* MODAL CADASTRO / EDIÇÃO */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-800">
              {editingQuestion ? 'Editar Questão' : 'Cadastrar Nova Questão'}
            </h3>
            
            <form onSubmit={handleSaveQuestion} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Enunciado</label>
                <textarea 
                  required
                  rows={3}
                  value={formData.statement}
                  onChange={e => setFormData({ ...formData, statement: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Escreva a pergunta..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {['A', 'B', 'C', 'D'].map(letter => (
                  <div key={letter}>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Alternativa {letter}</label>
                    <input 
                      type="text" 
                      required
                      value={formData[`option${letter}`]}
                      onChange={e => setFormData({ ...formData, [`option${letter}`]: e.target.value })}
                      className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Resposta Correta</label>
                  <select 
                    value={formData.correctAnswer}
                    onChange={e => setFormData({ ...formData, correctAnswer: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm bg-white"
                  >
                    <option value="A">Alternativa A</option>
                    <option value="B">Alternativa B</option>
                    <option value="C">Alternativa C</option>
                    <option value="D">Alternativa D</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Disciplina/Categoria</label>
                  <input 
                    type="text" 
                    value={formData.subject}
                    onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Dificuldade</label>
                  <select 
                    value={formData.difficulty}
                    onChange={e => setFormData({ ...formData, difficulty: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm bg-white"
                  >
                    <option value="Fácil">Fácil</option>
                    <option value="Média">Média</option>
                    <option value="Difícil">Difícil</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t">
                <button 
                  type="button" 
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 rounded-lg text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium"
                >
                  Salvar Questão
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL IMPORTAÇÃO (RF10-RF13) */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-800">Importar Banco via CSV / Excel</h3>
            <p className="text-sm text-slate-600">
              Faça upload do seu arquivo contendo colunas obrigatorias: Enunciado, A, B, C, D e Gabarito.
            </p>

            <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:bg-slate-50 transition cursor-pointer">
              <Upload className="mx-auto text-slate-400 mb-2" size={32} />
              <p className="text-xs text-slate-500">Clique para selecionar o arquivo .xlsx ou .csv</p>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg text-xs space-y-1">
              <p className="font-semibold text-slate-700">Modelo de Importação Standard:</p>
              <a href="#download" onClick={e => {e.preventDefault(); alert('Modelo CSV baixado!');}} className="text-blue-600 underline">Baixar Modelo Excel (.xlsx)</a>
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t">
              <button 
                onClick={() => setShowImportModal(false)}
                className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100"
              >
                Cancelar
              </button>
              <button 
                onClick={handleSimulateCSVImport}
                className="px-4 py-2 rounded-lg text-sm bg-green-600 hover:bg-green-700 text-white font-medium"
              >
                Simular Carregamento
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MÓDULO 2: CRIAÇÃO DE AVALIAÇÕES E VERSÕES (RF14 - RF28, RN06 - RN11)
// ============================================================================
function EvaluationsModule({ questions, evaluations, setEvaluations, semesters, classes, setStudentViewQR }) {
  const [showWizard, setShowWizard] = useState(false);
  const [selectedEvalForPrint, setSelectedEvalForPrint] = useState(null);

  // Form de Configuração da Avaliação
  const [evalConfig, setEvalConfig] = useState({
    title: '',
    semesterId: semesters[0]?.id || '',
    classId: classes[0]?.id || '',
    selectedQuestionIds: [],
    numVersions: 2,
    versionNaming: 'A/B/C', // 'A/B/C', '1/2/3', 'Cores'
    shuffleQuestions: true,
    shuffleOptions: true,
  });

  const toggleQuestionSelection = (id) => {
    setEvalConfig(prev => ({
      ...prev,
      selectedQuestionIds: prev.selectedQuestionIds.includes(id)
        ? prev.selectedQuestionIds.filter(qId => qId !== id)
        : [...prev.selectedQuestionIds, id]
    }));
  };

  // Algoritmo para Gerar as Versões mantendo a integridade do gabarito (RN06, RN07, RF23-RF25)
  const handleGenerateEvaluation = (e) => {
    e.preventDefault();
    if (evalConfig.selectedQuestionIds.length === 0) {
      alert('Selecione ao menos 1 questão para a avaliação!');
      return;
    }

    const baseQuestions = questions.filter(q => evalConfig.selectedQuestionIds.includes(q.id));
    const generatedVersions = [];

    // Gerador de Nomes
    const getNamingScheme = (idx) => {
      if (evalConfig.versionNaming === 'A/B/C') return String.fromCharCode(65 + idx);
      if (evalConfig.versionNaming === '1/2/3') return (idx + 1).toString();
      const colors = ['Azul', 'Verde', 'Amarela', 'Vermelha'];
      return colors[idx % colors.length];
    };

    const evalId = 'eval_' + Date.now();

    for (let v = 0; v < evalConfig.numVersions; v++) {
      const versionLetter = getNamingScheme(v);
      let vQuestions = [...baseQuestions];

      // Embaralha Ordem das Questões se habilitado (RN09)
      if (evalConfig.shuffleQuestions) {
        vQuestions = [...vQuestions].sort(() => Math.random() - 0.5);
      }

      // Processa cada questão e embaralha alternativas se configurado (RN07, RN10)
      const versionQuestionsData = [];
      const answerKey = [];

      vQuestions.forEach((origQ, qIndex) => {
        let keys = ['A', 'B', 'C', 'D'];
        let optionsMap = { ...origQ.options };
        let correctLetter = origQ.correctAnswer;

        if (evalConfig.shuffleOptions) {
          // Mantém os valores e reordena
          const optionEntries = Object.entries(origQ.options); // [['A', text], ['B', text], ...]
          const shuffledValues = optionEntries.map(e => e[1]).sort(() => Math.random() - 0.5);
          
          // Mapeia de volta para A, B, C, D
          let newOptions = {};
          let newCorrectLetter = 'A';

          keys.forEach((k, idx) => {
            newOptions[k] = shuffledValues[idx];
            // Se o texto original da resposta correta estiver nesta posição, essa passa a ser a nova letra
            if (origQ.options[origQ.correctAnswer] === shuffledValues[idx]) {
              newCorrectLetter = k;
            }
          });

          optionsMap = newOptions;
          correctLetter = newCorrectLetter;
        }

        versionQuestionsData.push({
          id: origQ.id,
          statement: origQ.statement,
          options: optionsMap,
          correctAnswer: correctLetter
        });

        answerKey.push({
          questionIndex: qIndex + 1,
          questionId: origQ.id,
          correctAnswer: correctLetter
        });
      });

      const versionId = `${evalId}_v_${versionLetter}`;

      generatedVersions.push({
        id: versionId,
        name: versionLetter,
        questions: versionQuestionsData,
        answerKey: answerKey,
        qrCodeUrl: `?eval=${evalId}&version=${versionId}`
      });
    }

    const newEvaluation = {
      id: evalId,
      title: evalConfig.title,
      semesterId: evalConfig.semesterId,
      classId: evalConfig.classId,
      createdAt: new Date().toLocaleDateString('pt-BR'),
      versions: generatedVersions
    };

    setEvaluations([...evaluations, newEvaluation]);
    setShowWizard(false);
    alert('Avaliação e Versões geradas com sucesso!');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Avaliações e Provas</h2>
          <p className="text-sm text-slate-500">Crie provas com múltiplas versões, embaralhamento e QR Code automático.</p>
        </div>
        <button 
          onClick={() => setShowWizard(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition"
        >
          <Plus size={16} />
          <span>Criar Nova Avaliação</span>
        </button>
      </div>

      {/* Lista de Avaliações */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {evaluations.map(ev => {
          const className = classes.find(c => c.id === ev.classId)?.name || 'Turma não especificada';
          return (
            <div key={ev.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-slate-800 text-lg">{ev.title}</h3>
                  <p className="text-xs text-slate-500">{className} • Criada em {ev.createdAt}</p>
                </div>
                <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-1 rounded-full">
                  {ev.versions.length} Versões
                </span>
              </div>

              <div className="border-t pt-3 flex flex-wrap gap-2">
                {ev.versions.map(v => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedEvalForPrint({ eval: ev, version: v })}
                    className="flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-200 transition"
                  >
                    <Printer size={12} />
                    <span>Versão {v.name}</span>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* MODAL CRIAR AVALIAÇÃO */}
      {showWizard && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full p-6 space-y-6 my-8">
            <h3 className="text-xl font-bold text-slate-800 border-b pb-3">Configurar Nova Avaliação</h3>

            <form onSubmit={handleGenerateEvaluation} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Título da Prova</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="Ex: Prova N1 - Algoritmos"
                    value={evalConfig.title}
                    onChange={e => setEvalConfig({...evalConfig, title: e.target.value})}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Semestre</label>
                  <select 
                    value={evalConfig.semesterId}
                    onChange={e => setEvalConfig({...evalConfig, semesterId: e.target.value})}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm bg-white"
                  >
                    {semesters.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Turma</label>
                  <select 
                    value={evalConfig.classId}
                    onChange={e => setEvalConfig({...evalConfig, classId: e.target.value})}
                    className="w-full border border-slate-300 rounded-lg p-2 text-sm bg-white"
                  >
                    {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              </div>

              {/* SELEÇÃO DE QUESTÕES */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Selecione as Questões ({evalConfig.selectedQuestionIds.length} selecionadas)
                </label>
                <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-lg divide-y bg-slate-50">
                  {questions.map(q => {
                    const isSelected = evalConfig.selectedQuestionIds.includes(q.id);
                    return (
                      <div 
                        key={q.id}
                        onClick={() => toggleQuestionSelection(q.id)}
                        className={`p-3 flex items-center justify-between cursor-pointer text-sm ${isSelected ? 'bg-blue-50/80 font-medium' : 'hover:bg-slate-100'}`}
                      >
                        <span className="truncate max-w-lg">{q.statement}</span>
                        <input type="checkbox" checked={isSelected} onChange={() => {}} className="h-4 w-4 text-blue-600 rounded" />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* REGRAS DE VERSÃO E EMBARALHAMENTO */}
              <div className="bg-slate-50 p-4 rounded-xl border space-y-4">
                <h4 className="font-semibold text-slate-800 text-sm">Configurações de Versões & Embaralhamento</h4>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Quantidade de Versões</label>
                    <input 
                      type="number" 
                      min="1" 
                      max="10"
                      value={evalConfig.numVersions}
                      onChange={e => setEvalConfig({...evalConfig, numVersions: parseInt(e.target.value) || 1})}
                      className="w-full border border-slate-300 rounded-lg p-2 bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Nomenclatura das Versões</label>
                    <select 
                      value={evalConfig.versionNaming}
                      onChange={e => setEvalConfig({...evalConfig, versionNaming: e.target.value})}
                      className="w-full border border-slate-300 rounded-lg p-2 bg-white"
                    >
                      <option value="A/B/C">Letras (A, B, C...)</option>
                      <option value="1/2/3">Números (1, 2, 3...)</option>
                      <option value="Cores">Cores (Azul, Verde...)</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t">
                  <label className="flex items-center space-x-2 text-sm text-slate-700 cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={evalConfig.shuffleQuestions}
                      onChange={e => setEvalConfig({...evalConfig, shuffleQuestions: e.target.checked})}
                      className="rounded text-blue-600"
                    />
                    <span>Embaralhar a ordem das Questões entre as versões</span>
                  </label>

                  <label className="flex items-center space-x-2 text-sm text-slate-700 cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={evalConfig.shuffleOptions}
                      onChange={e => setEvalConfig({...evalConfig, shuffleOptions: e.target.checked})}
                      className="rounded text-blue-600"
                    />
                    <span>Embaralhar as Alternativas (preservando a resposta correta no gabarito)</span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t">
                <button 
                  type="button" 
                  onClick={() => setShowWizard(false)}
                  className="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-5 py-2 rounded-lg text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium"
                >
                  Gerar Versões e QR Codes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VISUALIZADOR DE IMPRESSÃO DA PROVA E FOLHA DE RESPOSTAS (RF26, RF27, RF28) */}
      {selectedEvalForPrint && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full p-8 my-8 space-y-8">
            <div className="flex justify-between items-center border-b pb-4 print:hidden">
              <div>
                <h3 className="text-xl font-bold text-slate-800">Visualização para Impressão</h3>
                <p className="text-sm text-slate-500">
                  {selectedEvalForPrint.eval.title} — Versão: <strong>{selectedEvalForPrint.version.name}</strong>
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => window.print()}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                >
                  <Printer size={16} />
                  <span>Imprimir / Salvar PDF</span>
                </button>
                <button 
                  onClick={() => setSelectedEvalForPrint(null)}
                  className="p-2 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            {/* DOCUMENTO DA PROVA E FOLHA DE RESPOSTAS */}
            <div className="space-y-12 text-slate-900 font-serif">
              {/* CABEÇALHO PROVA */}
              <div className="border-2 border-slate-900 p-4 rounded text-xs space-y-2">
                <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                  <span className="font-bold text-sm">AVALIAÇÃO INSTITUCIONAL</span>
                  <span className="font-bold text-sm">VERSÃO: {selectedEvalForPrint.version.name}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <p><strong>NOME DO ALUNO:</strong> ________________________________________</p>
                  <p><strong>MATRÍCULA:</strong> _______________</p>
                  <p><strong>DATA:</strong> ____/____/2026</p>
                  <p><strong>TURMA:</strong> Engenharia de Software</p>
                </div>
              </div>

              {/* QUESTÕES */}
              <div className="space-y-6">
                <h4 className="font-sans font-bold text-slate-800 uppercase text-xs tracking-wider border-b pb-1">Caderno de Questões</h4>
                {selectedEvalForPrint.version.questions.map((q, idx) => (
                  <div key={q.id} className="text-sm space-y-2">
                    <p className="font-semibold">{idx + 1}. {q.statement}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 pl-4 font-sans text-xs">
                      <p><strong>A)</strong> {q.options.A}</p>
                      <p><strong>B)</strong> {q.options.B}</p>
                      <p><strong>C)</strong> {q.options.C}</p>
                      <p><strong>D)</strong> {q.options.D}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* FOLHA DE RESPOSTAS / GABARITO AUTOMÁTICO (OMR + QR CODE) */}
              <div className="border-t-4 border-dashed border-slate-400 pt-8 mt-12 page-break-before font-sans">
                <div className="border-4 border-slate-900 p-6 rounded-lg relative">
                  {/* MARCAS DE ALINHAMENTO OMR */}
                  <div className="absolute top-2 left-2 w-4 h-4 bg-black"></div>
                  <div className="absolute top-2 right-2 w-4 h-4 bg-black"></div>
                  <div className="absolute bottom-2 left-2 w-4 h-4 bg-black"></div>
                  <div className="absolute bottom-2 right-2 w-4 h-4 bg-black"></div>

                  <div className="flex justify-between items-start mb-6 border-b-2 border-slate-900 pb-4">
                    <div>
                      <h3 className="font-extrabold text-lg uppercase tracking-tight">Folha de Respostas Oficial</h3>
                      <p className="text-xs text-slate-600">{selectedEvalForPrint.eval.title}</p>
                      <p className="text-xs font-bold mt-1">VERSÃO DA PROVA: {selectedEvalForPrint.version.name}</p>
                    </div>

                    {/* QR CODE GERADO DA VERSÃO (RF28) */}
                    <div className="text-center bg-slate-50 p-2 border rounded">
                      <div className="w-20 h-20 bg-slate-900 text-white flex flex-col items-center justify-center p-1 rounded text-center">
                        <QrCode size={40} className="text-white" />
                        <span className="text-[8px] mt-1 font-mono">{selectedEvalForPrint.version.name}</span>
                      </div>
                      <span className="text-[9px] text-slate-500 block mt-1">Escanear p/ Gabarito</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 mb-4 italic">
                    Instruções: Preencha completamente o círculo da alternativa correspondente. Não rasure.
                  </p>

                  {/* GRADE OMR */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {selectedEvalForPrint.version.questions.map((_, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-slate-50 p-2 rounded border border-slate-300">
                        <span className="font-bold text-xs w-8">{String(idx + 1).padStart(2, '0')}</span>
                        <div className="flex space-x-3">
                          {['A', 'B', 'C', 'D'].map(opt => (
                            <div key={opt} className="flex items-center space-x-1">
                              <div className="w-5 h-5 rounded-full border-2 border-slate-800 flex items-center justify-center text-[10px] font-bold">
                                {opt}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* SIMULADOR DE LINK DO ALUNO VIA QR CODE */}
                  <div className="mt-6 pt-4 border-t text-center text-xs text-blue-600 print:hidden">
                    <button 
                      onClick={() => setStudentViewQR({ evalId: selectedEvalForPrint.eval.id, versionId: selectedEvalForPrint.version.id })}
                      className="hover:underline font-semibold"
                    >
                      [Simular Aluno Escaneando este QR Code]
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MÓDULO 3: CORREÇÃO AUTOMÁTICA OMR/LEITURA (RF31 - RF40, RNF05)
// ============================================================================
function CorrectionModule({ evaluations, students, results, setResults }) {
  const [selectedEvalId, setSelectedEvalId] = useState('');
  const [selectedVersionId, setSelectedVersionId] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState('');
  
  // Respostas simuladas na leitura
  const [scannedAnswers, setScannedAnswers] = useState({});
  const [readQualityWarning, setReadQualityWarning] = useState(false);

  const selectedEval = evaluations.find(e => e.id === selectedEvalId);
  const selectedVersion = selectedEval?.versions.find(v => v.id === selectedVersionId);

  // Simular alteração da leitura de marcações OMR
  const handleOptionSelect = (qIdx, option) => {
    setScannedAnswers(prev => ({
      ...prev,
      [qIdx]: option
    }));
  };

  // Processar Correção
  const handleProcessCorrection = () => {
    if (!selectedEval || !selectedVersion) {
      alert('Selecione a avaliação e a versão da folha lida!');
      return;
    }

    // Regra RNF05 / RF40: Verificação de Leitura
    if (readQualityWarning) {
      alert('Erro de Leitura: Marcações ilegíveis ou duplas detectadas. Por favor, ajuste ou realize uma nova leitura!');
      return;
    }

    let hits = 0;
    let errors = 0;
    const detail = [];

    selectedVersion.answerKey.forEach(item => {
      const studentMarked = scannedAnswers[item.questionIndex];
      const isCorrect = studentMarked === item.correctAnswer;
      if (isCorrect) hits++; else errors++;

      detail.push({
        questionIndex: item.questionIndex,
        questionId: item.questionId,
        marked: studentMarked || 'N/A',
        correctAnswer: item.correctAnswer,
        isCorrect
      });
    });

    const totalQuestions = selectedVersion.answerKey.length;
    const grade = (hits / totalQuestions) * 10;

    const newResult = {
      id: 'res_' + Date.now(),
      evaluationId: selectedEval.id,
      evaluationTitle: selectedEval.title,
      versionId: selectedVersion.id,
      versionName: selectedVersion.name,
      studentId: selectedStudentId || 'aluno_1',
      studentName: students.find(s => s.id === selectedStudentId)?.name || 'Carlos Eduardo',
      hits,
      errors,
      grade: grade.toFixed(1),
      timestamp: new Date().toLocaleString('pt-BR'),
      details: detail
    };

    setResults([newResult, ...results]);
    alert(`Correção realizada com sucesso! Nota obtida: ${grade.toFixed(1)}`);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-xl font-bold text-slate-800">Correção Automática de Provas (OMR)</h2>
        <p className="text-sm text-slate-500">
          Simule a leitura do QR Code da prova e o escaneamento da folha de respostas.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* COLUNA DE CAPTURA / CÂMERA */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-800 border-b pb-2 flex items-center space-x-2">
            <Camera size={18} className="text-blue-600" />
            <span>Scanner / Captura da Folha</span>
          </h3>

          <div className="bg-slate-900 rounded-lg aspect-video flex flex-col items-center justify-center text-slate-400 p-4 text-center relative overflow-hidden border-2 border-dashed border-slate-700">
            <QrCode size={48} className="text-blue-500 animate-pulse mb-2" />
            <p className="text-xs text-slate-300">Posicione a câmera sobre a folha de respostas e o QR Code</p>
            <span className="mt-2 bg-blue-600/30 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded">
              Aguardando Alinhamento OMR
            </span>
          </div>

          {/* Seletores manuais de apoio à leitura OMR */}
          <div className="space-y-3 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Avaliação Identificada</label>
              <select 
                value={selectedEvalId} 
                onChange={e => { setSelectedEvalId(e.target.value); setSelectedVersionId(''); }}
                className="w-full border border-slate-300 rounded p-2 bg-white"
              >
                <option value="">-- Selecione a Avaliação --</option>
                {evaluations.map(e => <option key={e.id} value={e.id}>{e.title}</option>)}
              </select>
            </div>

            {selectedEval && (
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Versão Lida pelo QR Code</label>
                <select 
                  value={selectedVersionId} 
                  onChange={e => setSelectedVersionId(e.target.value)}
                  className="w-full border border-slate-300 rounded p-2 bg-white"
                >
                  <option value="">-- Selecione a Versão --</option>
                  {selectedEval.versions.map(v => <option key={v.id} value={v.id}>Versão {v.name}</option>)}
                </select>
              </div>
            )}

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Aluno Identificado</label>
              <select 
                value={selectedStudentId} 
                onChange={e => setSelectedStudentId(e.target.value)}
                className="w-full border border-slate-300 rounded p-2 bg-white"
              >
                {students.map(s => <option key={s.id} value={s.id}>{s.name} ({s.code})</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* COLUNA DE LEITURA DAS RESPOSTAS E VALIDAÇÃO */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-800 border-b pb-2 flex items-center justify-between">
            <span>Matriz de Marcações Detectadas</span>
            {selectedVersion && (
              <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full font-normal">
                Gabarito Carregado • {selectedVersion.answerKey.length} questões
              </span>
            )}
          </h3>

          {!selectedVersion ? (
            <div className="text-center py-12 text-slate-400">
              Selecione uma avaliação e versão para carregar o gabarito e realizar a leitura.
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-72 overflow-y-auto p-2 border rounded-lg bg-slate-50">
                {selectedVersion.answerKey.map((item) => {
                  const marked = scannedAnswers[item.questionIndex];
                  return (
                    <div key={item.questionIndex} className="bg-white p-3 rounded border flex items-center justify-between shadow-sm">
                      <span className="font-bold text-xs text-slate-700">Questão {item.questionIndex}</span>
                      <div className="flex space-x-1">
                        {['A', 'B', 'C', 'D'].map(opt => (
                          <button
                            key={opt}
                            onClick={() => handleOptionSelect(item.questionIndex, opt)}
                            className={`w-7 h-7 rounded-full text-xs font-bold transition ${
                              marked === opt 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* SIMULADOR DE FALHA DE LEITURA (RNF05) */}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center justify-between text-xs">
                <span className="text-amber-800 font-medium">Simular falha/dúvida de leitura na folha</span>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={readQualityWarning}
                    onChange={e => setReadQualityWarning(e.target.checked)}
                    className="rounded text-amber-600"
                  />
                  <span className="text-amber-900 font-semibold">Marcar como duvidoso</span>
                </label>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleProcessCorrection}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg text-sm shadow transition"
                >
                  Finalizar Correção e Registrar Nota
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MÓDULO 4: RESULTADOS, ESTATÍSTICAS E EXPORTAÇÃO (RF41 - RF48)
// ============================================================================
function ResultsModule({ results, evaluations, students, classes }) {
  const [selectedEvalFilter, setSelectedEvalFilter] = useState('');

  const filteredResults = selectedEvalFilter 
    ? results.filter(r => r.evaluationId === selectedEvalFilter)
    : results;

  // Cálculo de Estatísticas Simplificadas (RF46)
  const totalCorrected = filteredResults.length;
  const avgGrade = totalCorrected > 0 
    ? (filteredResults.reduce((acc, r) => acc + parseFloat(r.grade), 0) / totalCorrected).toFixed(1)
    : '0.0';

  // Exportar Excel/CSV (RF48)
  const handleExportCSV = () => {
    if (results.length === 0) {
      alert('Não há resultados registrados para exportação.');
      return;
    }

    let csvContent = "data:text/csv;charset=utf-8,Aluno,Avaliacao,Versao,Acertos,Erros,Nota,Data\n";
    results.forEach(r => {
      csvContent += `"${r.studentName}","${r.evaluationTitle}","${r.versionName}",${r.hits},${r.errors},${r.grade},"${r.timestamp}"\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "relatorio_avaliacoes.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Resultados & Estatísticas</h2>
          <p className="text-sm text-slate-500">Consulte notas, médias de turmas e exporte relatórios completos em Excel/CSV.</p>
        </div>
        <button 
          onClick={handleExportCSV}
          className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition"
        >
          <Download size={16} />
          <span>Exportar Relatório (CSV)</span>
        </button>
      </div>

      {/* CARDS DE ESTATÍSTICAS RÁPIDAS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Provas Corrigidas</p>
          <p className="text-3xl font-extrabold text-slate-800 mt-1">{totalCorrected}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Média Geral da Turma</p>
          <p className="text-3xl font-extrabold text-blue-600 mt-1">{avgGrade}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Taxa de Sucesso</p>
          <p className="text-3xl font-extrabold text-green-600 mt-1">
            {totalCorrected > 0 ? Math.round((filteredResults.filter(r => parseFloat(r.grade) >= 6).length / totalCorrected) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* TABELA DE RESULTADOS */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b bg-slate-50 flex items-center justify-between">
          <h3 className="font-bold text-slate-800">Histórico de Correções</h3>
        </div>

        {filteredResults.length === 0 ? (
          <div className="p-8 text-center text-slate-500">Nenhuma prova corrigida até o momento.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-100 text-slate-600 uppercase text-xs font-semibold border-b">
                <tr>
                  <th className="p-3">Aluno</th>
                  <th className="p-3">Avaliação</th>
                  <th className="p-3">Versão</th>
                  <th className="p-3">Acertos</th>
                  <th className="p-3">Erros</th>
                  <th className="p-3">Nota</th>
                  <th className="p-3">Data/Hora</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredResults.map(r => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="p-3 font-medium text-slate-900">{r.studentName}</td>
                    <td className="p-3">{r.evaluationTitle}</td>
                    <td className="p-3 font-bold text-blue-600">Versão {r.versionName}</td>
                    <td className="p-3 text-green-600 font-semibold">{r.hits}</td>
                    <td className="p-3 text-red-500 font-semibold">{r.errors}</td>
                    <td className="p-3 font-extrabold text-slate-900">{r.grade}</td>
                    <td className="p-3 text-xs text-slate-500">{r.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// MÓDULO 5: GERENCIAMENTO ACADÊMICO (SEMESTRES, TURMAS, ALUNOS) (RF02 - RF05)
// ============================================================================
function AcademicManagementModule({ semesters, setSemesters, classes, setClasses, students, setStudents }) {
  const [newSemesterName, setNewSemesterName] = useState('');
  const [newClassName, setNewClassName] = useState('');
  const [selectedSemForClass, setSelectedSemForClass] = useState(semesters[0]?.id || '');

  const handleAddSemester = (e) => {
    e.preventDefault();
    if (!newSemesterName) return;
    const newSem = { id: 'sem_' + Date.now(), name: newSemesterName, active: true };
    setSemesters([...semesters, newSem]);
    setNewSemesterName('');
  };

  const handleAddClass = (e) => {
    e.preventDefault();
    if (!newClassName) return;
    const newC = { id: 'turma_' + Date.now(), name: newClassName, semesterId: selectedSemForClass };
    setClasses([...classes, newC]);
    setNewClassName('');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <h2 className="text-xl font-bold text-slate-800">Gerenciamento Acadêmico</h2>
        <p className="text-sm text-slate-500">Cadastre e organize Semestres, Turmas e Alunos para vinculação das avaliações.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* SEMESTRES */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-800 border-b pb-2">Semestres Letivos</h3>
          <form onSubmit={handleAddSemester} className="flex gap-2">
            <input 
              type="text" 
              placeholder="Ex: 2027.1"
              value={newSemesterName}
              onChange={e => setNewSemesterName(e.target.value)}
              className="flex-1 border border-slate-300 rounded-lg p-2 text-sm"
            />
            <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              Adicionar
            </button>
          </form>

          <div className="space-y-2">
            {semesters.map(s => (
              <div key={s.id} className="flex justify-between items-center bg-slate-50 p-2.5 rounded border border-slate-200 text-sm">
                <span className="font-semibold text-slate-700">{s.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${s.active ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'}`}>
                  {s.active ? 'Ativo' : 'Inativo'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* TURMAS */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-800 border-b pb-2">Turmas Cadastradas</h3>
          <form onSubmit={handleAddClass} className="space-y-2">
            <input 
              type="text" 
              placeholder="Nome da Turma (Ex: Engenharia - T3)"
              value={newClassName}
              onChange={e => setNewClassName(e.target.value)}
              className="w-full border border-slate-300 rounded-lg p-2 text-sm"
            />
            <div className="flex gap-2">
              <select 
                value={selectedSemForClass} 
                onChange={e => setSelectedSemForClass(e.target.value)}
                className="flex-1 border border-slate-300 rounded-lg p-2 text-sm bg-white"
              >
                {semesters.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
                Cadastrar Turma
              </button>
            </div>
          </form>

          <div className="space-y-2">
            {classes.map(c => {
              const sem = semesters.find(s => s.id === c.semesterId);
              return (
                <div key={c.id} className="flex justify-between items-center bg-slate-50 p-2.5 rounded border border-slate-200 text-sm">
                  <span className="font-semibold text-slate-700">{c.name}</span>
                  <span className="text-xs text-slate-500">Semestre: {sem?.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}