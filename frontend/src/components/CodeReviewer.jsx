import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import '../styles/CodeReviewer.css';

export default function CodeReviewer() {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!code.trim()) {
      setError('Please paste some code to review.');
      return;
    }

    setIsLoading(true);
    setError('');
    setReview(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/review', {
        code: code
      });
      setReview(response.data.review || 'No review content returned.');
    } catch (err) {
      setError('Failed to generate review. Please try again.');
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
          {isLoading ? 'Reviewing code...' : 'Get Code Review'}
        </button>
      </form>

      {isLoading && <div className="loading-message">Reviewing code...</div>}

      {error && <div className="error-message">{error}</div>}

      {review && (
        <div className="review-result">
          <h2>AI Review</h2>
          <div className="review-markdown">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');

                  if (!inline && match) {
                    return (
                      <SyntaxHighlighter
                        style={oneLight}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    );
                  }

                  return (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {review}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
