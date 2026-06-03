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
  const [projectPath, setProjectPath] = useState('.');
  const [projectScan, setProjectScan] = useState(null);
  const [projectReview, setProjectReview] = useState(null);
  const [projectReviewRaw, setProjectReviewRaw] = useState('');
  const [isProjectLoading, setIsProjectLoading] = useState(false);
  const [projectError, setProjectError] = useState('');
  const [projectHistory, setProjectHistory] = useState([]);
  const [isProjectHistoryLoading, setIsProjectHistoryLoading] = useState(false);
  const [projectHistoryError, setProjectHistoryError] = useState('');

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

  const loadProjectHistory = async () => {
    setIsProjectHistoryLoading(true);
    setProjectHistoryError('');

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/projects');
      setProjectHistory(response.data || []);
    } catch (err) {
      setProjectHistoryError('Failed to load project analysis history.');
      console.error(err);
    } finally {
      setIsProjectHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
    loadProjectHistory();
  }, []);

  const parseProjectReview = (raw) => {
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw);
    } catch (parseError) {
      return null;
    }
  };

  const formatConfidence = (value) => {
    if (typeof value !== 'number') {
      return '';
    }

    return `${Math.round(value * 100)}%`;
  };

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

  const handleProjectScan = async (e) => {
    e.preventDefault();

    if (!projectPath.trim()) {
      setProjectError('Please provide a project path to scan.');
      return;
    }

    setIsProjectLoading(true);
    setProjectError('');
    setProjectScan(null);
    setProjectReview(null);
    setProjectReviewRaw('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/projects/scan', {
        root_path: projectPath.trim()
      });
      const projectMap = response.data?.project_map || null;
      const reviewText = response.data?.review || '';
      setProjectScan(projectMap);
      setProjectReviewRaw(reviewText);
      setProjectReview(parseProjectReview(reviewText));
      await loadProjectHistory();
    } catch (scanError) {
      setProjectError('Failed to scan the project. Please try again.');
      console.error(scanError);
    } finally {
      setIsProjectLoading(false);
    }
  };

  const handleProjectHistorySelect = async (analysisId) => {
    if (!analysisId) {
      return;
    }

    setIsProjectLoading(true);
    setProjectError('');

    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/projects/${analysisId}`);
      const projectMap = response.data?.project_map || null;
      const reviewText = response.data?.review || '';
      setProjectScan(projectMap);
      setProjectReviewRaw(reviewText);
      setProjectReview(parseProjectReview(reviewText));
      if (response.data?.project_path) {
        setProjectPath(response.data.project_path);
      }
    } catch (historyError) {
      setProjectError('Failed to load the project analysis.');
      console.error(historyError);
    } finally {
      setIsProjectLoading(false);
    }
  };

  const renderReviewSection = (title, items) => {
    if (!items || items.length === 0) {
      return null;
    }

    return (
      <div className="project-review-section">
        <h4>{title}</h4>
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>
              <p>{item.statement}</p>
              {item.evidence && item.evidence.length > 0 && (
                <div className="evidence">Evidence: {item.evidence.join(', ')}</div>
              )}
            </li>
          ))}
        </ul>
      </div>
    );
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

          <section className="project-panel">
            <div className="panel-header">
              <div>
                <h2>Project Analysis</h2>
                <p>Scan a local project folder to generate a project map and grounded review.</p>
                <div className="project-examples">
                  <span>Examples: .</span>
                  <span>backend</span>
                  <span>frontend</span>
                  <span className="note">Local paths only (no ZIP or GitHub URLs yet).</span>
                </div>
              </div>
            </div>

            <form className="project-form" onSubmit={handleProjectScan}>
              <label htmlFor="projectPath">Project path</label>
              <div className="project-input-row">
                <input
                  id="projectPath"
                  type="text"
                  value={projectPath}
                  onChange={(e) => setProjectPath(e.target.value)}
                  placeholder="."
                  disabled={isProjectLoading}
                />
                <button type="submit" disabled={isProjectLoading}>
                  {isProjectLoading ? 'Scanning...' : 'Scan Project'}
                </button>
              </div>
            </form>

            {projectError && <div className="error-message">{projectError}</div>}
            {isProjectLoading && <div className="loading-message">Scanning project...</div>}

            {projectScan && (
              <div className="project-results">
                <div className="project-grid">
                  <div className="project-card">
                    <h3>Project Name</h3>
                    <p>{projectScan.project_name}</p>
                  </div>
                  <div className="project-card">
                    <h3>Frameworks</h3>
                    <ul>
                      {projectScan.framework_confidence?.map((framework) => (
                        <li key={framework.name}>
                          <span>{framework.name}</span>
                          <span className="badge">{formatConfidence(framework.confidence)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="project-card">
                    <h3>Languages</h3>
                    <ul>
                      {projectScan.languages?.map((language) => (
                        <li key={language}>{language}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="project-card">
                    <h3>Package Managers</h3>
                    <ul>
                      {projectScan.package_managers?.map((manager) => (
                        <li key={manager}>{manager}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="project-card">
                    <h3>Important Files</h3>
                    <ul>
                      {projectScan.important_files?.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="project-card">
                    <h3>Entry Points</h3>
                    <ul>
                      {projectScan.entry_points?.map((entry) => (
                        <li key={entry}>{entry}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="project-card">
                    <h3>Database Signals</h3>
                    <ul>
                      {projectScan.database_signals?.map((signal) => (
                        <li key={signal.name}>
                          <span>{signal.name}</span>
                          <span className="badge">{signal.evidence?.length || 0} files</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="project-review">
                  <h3>Grounded Project Review</h3>
                  {projectReview ? (
                    <>
                      {renderReviewSection('Overview', projectReview.overview)}
                      {renderReviewSection('Architecture Notes', projectReview.architecture_notes)}
                      {renderReviewSection('Risks', projectReview.risks)}
                      {renderReviewSection('Opportunities', projectReview.opportunities)}
                    </>
                  ) : (
                    <pre>{projectReviewRaw || 'No review content returned.'}</pre>
                  )}
                </div>
              </div>
            )}
          </section>
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

          <div className="analysis-history">
            <div className="history-header">
              <h2>Project Analysis History</h2>
            </div>
            {isProjectHistoryLoading && <div className="loading-message">Loading analyses...</div>}
            {projectHistoryError && <div className="error-message">{projectHistoryError}</div>}
            {!isProjectHistoryLoading && !projectHistoryError && projectHistory.length === 0 && (
              <div className="history-empty">No project analyses yet.</div>
            )}
            {!isProjectHistoryLoading && projectHistory.length > 0 && (
              <ul className="history-list">
                {projectHistory.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      className="history-item"
                      onClick={() => handleProjectHistorySelect(item.id)}
                    >
                      <div className="history-item-header">
                        <span className="history-item-title">{item.project_name}</span>
                      </div>
                      <div className="history-item-meta">{formatTimestamp(item.created_at)}</div>
                      <div className="history-item-snippet">
                        {item.project_path}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
