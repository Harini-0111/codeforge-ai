import { useEffect, useState } from 'react';
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
  const [history, setHistory] = useState([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [error, setError] = useState('');
  const [historyError, setHistoryError] = useState('');

  const buildSnippet = (text, maxLength = 70) => {
    if (!text) {
      return '';
    }

    const trimmed = text.replace(/\s+/g, ' ').trim();
    if (trimmed.length <= maxLength) {
      return trimmed;
    }

    return `${trimmed.slice(0, maxLength - 3)}...`;
  };

  const formatTimestamp = (value) => {
    if (!value) {
      return '';
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
  };

  const loadHistory = async () => {
    setIsHistoryLoading(true);
    setHistoryError('');

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/reviews');
      setHistory(response.data || []);
    } catch (err) {
      setHistoryError('Failed to load review history.');
      console.error(err);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

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
      setReview(response.data);
      await loadHistory();
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
      <div className="review-layout">
        <div className="review-main">
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
              <div className="review-header">
                <h2>AI Review</h2>
                <div className="review-meta">
                  <span className="language-badge">{review.language}</span>
                  <span className="review-timestamp">{formatTimestamp(review.created_at)}</span>
                </div>
              </div>
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
                  {review.review || 'No review content returned.'}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        <aside className="history-panel">
          <div className="history-header">
            <h2>Review History</h2>
          </div>
          {isHistoryLoading && <div className="loading-message">Loading history...</div>}
          {historyError && <div className="error-message">{historyError}</div>}
          {!isHistoryLoading && !historyError && history.length === 0 && (
            <div className="history-empty">No reviews yet.</div>
          )}
          {!isHistoryLoading && history.length > 0 && (
            <ul className="history-list">
              {history.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className="history-item"
                    onClick={() => {
                      setReview(item);
                      setCode(item.code);
                    }}
                  >
                    <div className="history-item-header">
                      <span className="history-item-title">Review #{item.id}</span>
                      <span className="language-badge">{item.language}</span>
                    </div>
                    <div className="history-item-meta">{formatTimestamp(item.created_at)}</div>
                    <div className="history-item-snippet">
                      {buildSnippet(item.code)}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>
    </div>
  );
}
