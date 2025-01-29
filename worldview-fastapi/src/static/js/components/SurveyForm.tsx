import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';

interface Response {
  id: string;
  text: string;
  scores: [number, number, number];
}

interface Question {
  text: string;
  responses: Response[];
}

interface Questions {
  [key: string]: Question;
}

interface FormResponses {
  [key: string]: number;
}

const SurveyForm = () => {
  const [questions, setQuestions] = useState<Questions | null>(null);
  const [responses, setResponses] = useState<FormResponses>({});

  useEffect(() => {
    fetch('/api/questions')
      .then(res => res.json())
      .then(data => setQuestions(data.questions));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...responses,
        browser: navigator.userAgent,
        source: 'web'
      })
    });
    const data = await result.json();
    console.log(data);
  };

  if (!questions) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <form onSubmit={handleSubmit}>
        {Object.entries(questions).map(([id, question]) => (
          <Card key={id} className="mb-6 p-6">
            <h3 className="text-lg font-semibold mb-4">{question.text}</h3>
            <div className="space-y-2">
              {question.responses.map((response, idx) => (
                <div key={response.id} className="flex items-center">
                  <input
                    type="radio"
                    name={id}
                    value={idx + 1}
                    id={response.id}
                    className="mr-2"
                    onChange={(e) => setResponses({
                      ...responses,
                      [`${id.toLowerCase()}_response`]: parseInt(e.target.value)
                    })}
                  />
                  <label htmlFor={response.id}>{response.text}</label>
                </div>
              ))}
            </div>
          </Card>
        ))}
        <button 
          type="submit" 
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default SurveyForm;