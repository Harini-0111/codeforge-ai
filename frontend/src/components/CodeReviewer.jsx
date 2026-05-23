import { useState } from 'react';
import axios from 'axios';
import '../styles/CodeReviewer.css';

export default function CodeReviewer() {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!code.trim()) {
      setError('Please paste some code');
      return;
    }

    setIsLoading(true);
    setError('');
    setReview(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/review', {
        code: code
      });
      setReview(response.data);
    } catch (err) {
      setError('Error connecting to backend: ' + (err.message || 'Unknown error'));
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="code-reviewer">
      <h1>CodeForge AI - Code Review</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="codeInput">Paste your code here:</label>
          <textarea
            id="codeInput"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your Python/JavaScript code here..."
            rows="15"
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Get Code Review'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {review && (
        <div className="review-result">
          <div className="score-section">
            <h2>Code Quality Score: <span className={`score score-${review.score}`}>{review.score}/100</span></h2>
          </div>

          {review.issues.length > 0 && (
            <div className="issues-section">
              <h3>Issues Found:</h3>
              <ul>
                {review.issues.map((issue, idx) => (
                  <li key={idx} className="issue">{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {review.suggestions.length > 0 && (
            <div className="suggestions-section">
              <h3>Suggestions:</h3>
              <ul>
                {review.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="suggestion">{suggestion}</li>
                ))}
              </ul>
            </div>
          )}

          {review.issues.length === 0 && review.suggestions.length === 0 && (
            <div className="success-message">Great code! No issues found.</div>
          )}
        </div>
      )}
    </div>
  );
}
