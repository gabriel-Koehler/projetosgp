export function shuffle(list) {
  const clone = [...list];
  for (let i = clone.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [clone[i], clone[j]] = [clone[j], clone[i]];
  }
  return clone;
}

function normalizeAnswer(question) {
  const answer = question.answer ?? question.correctAnswer;
  if (typeof answer === 'string' && /^[A-Da-d]$/.test(answer)) {
    const idx = answer.toUpperCase().charCodeAt(0) - 65;
    return question.options[idx] ?? answer;
  }
  return answer;
}

export function buildVersions({
  questions,
  versionCount = 1,
  naming = 'A,B,C',
  sameSet = true,
  shuffleQuestions = false,
  shuffleAlternatives = false
}) {
  const names = (naming || 'A,B,C')
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean);

  const versionNames = names.length >= versionCount
    ? names.slice(0, versionCount)
    : Array.from({ length: versionCount }, (_, idx) => `Versão ${idx + 1}`);

  const versions = [];

  for (let idx = 0; idx < versionCount; idx += 1) {
    const baseQuestions = sameSet ? questions : questions; 
    const reorderedQuestions = shuffleQuestions ? shuffle(baseQuestions) : [...baseQuestions];

    const versionQuestions = reorderedQuestions.map((question) => {
      const correctAnswer = normalizeAnswer(question);
      const shuffledOptions = shuffleAlternatives ? shuffle(question.options) : [...question.options];
      const answer = correctAnswer;

      return {
        ...question,
        id: question.id,
        versionName: versionNames[idx],
        originalQuestionId: question.id,
        options: shuffledOptions,
        answer,
        correctAnswer: answer,
        answerLetter: String.fromCharCode(65 + shuffledOptions.indexOf(answer))
      };
    });

    versions.push({
      name: versionNames[idx],
      questions: versionQuestions,
      answerKey: versionQuestions.map((question, position) => ({
        questionId: question.originalQuestionId,
        position,
        correct: question.correctAnswer
      }))
    });
  }

  return versions;
}

export function buildStudentView({ versionName, questions, studentAnswers, showOnlyCorrect = true }) {
  return {
    title: versionName,
    items: questions.map((question, idx) => ({
      id: question.id,
      statement: question.statement,
      options: [...question.options],
      correctAnswer: showOnlyCorrect ? question.correctAnswer ?? question.answer : undefined,
      selectedAnswer: showOnlyCorrect ? undefined : studentAnswers[idx],
      studentAnswer: showOnlyCorrect ? undefined : studentAnswers[idx]
    }))
  };
}
