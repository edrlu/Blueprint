import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import './SimilarityView.css';

function SimilarityView() {
  const navigate = useNavigate();
  const [devpostUrl, setDevpostUrl] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState('');
  const [projects, setProjects] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [sourceProgress, setSourceProgress] = useState({ github: 0, devpost: 0 });

  useEffect(() => {
    document.title = 'Blueprint - Similarity Checker';
  }, []);

  // Only show analysis after result is complete (not during processing)
  const showAnalysisSummary = result !== null;

  // Sort projects by AI similarity (highest first)
  const sortedProjects = useMemo(() => {
    return [...projects].sort((a, b) => {
      const simA = a.ai_similarity !== undefined ? a.ai_similarity : -1;
      const simB = b.ai_similarity !== undefined ? b.ai_similarity : -1;
      return simB - simA;
    });
  }, [projects]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!devpostUrl.trim()) {
      setError('Please enter a Devpost URL');
      return;
    }

    // Clean URL - remove query parameters
    let cleanUrl = devpostUrl.trim();
    if (cleanUrl.includes('?')) {
      cleanUrl = cleanUrl.split('?')[0];
    }

    setIsChecking(true);
    setError('');
    setProjects([]);
    setResult(null);
    setStatus('Starting similarity check...');
    setProgress('');
    setSourceProgress({ github: 0, devpost: 0 });

    try {
      const response = await fetch('http://localhost:8000/similarity-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ devpost_url: cleanUrl }),
      });

      if (!response.ok) throw new Error('Failed to check similarity');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.status) setStatus(data.status);
            if (data.progress) setProgress(data.progress);

            // Handle source progress (GitHub: 5, Devpost: 10, etc.)
            if (data.source_progress) {
              const [source, count] = data.source_progress.split(': ');
              setSourceProgress(prev => ({
                ...prev,
                [source.toLowerCase()]: parseInt(count)
              }));
            }

            // Handle new project
            if (data.project) {
              setProjects(prev => [...prev, data.project]);
            }

            // Handle project update with similarity score (live reordering)
            if (data.project_update) {
              setProjects(prev => {
                const index = prev.findIndex(p => p.url === data.project_update.url);
                if (index >= 0) {
                  // Update existing project
                  const updated = [...prev];
                  updated[index] = data.project_update;
                  return updated;
                } else {
                  // Add new project if not found
                  return [...prev, data.project_update];
                }
              });
            }

            if (data.result) {
              setResult(data.result);
              setStatus('Analysis complete!');
            }
            if (data.error) {
              setError(data.error);
              setStatus('Error occurred');
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setStatus('Failed to check similarity');
    } finally {
      setIsChecking(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'HIGH': return 'var(--error)';
      case 'MEDIUM': return '#FF8C00';
      case 'LOW': return '#00AA00';
      case 'ANALYZING': return 'var(--gray-600)';
      default: return 'var(--gray-600)';
    }
  };

  const getSimilarityColor = (score) => {
    if (score >= 90) return 'var(--error)';
    if (score >= 70) return '#FF8C00';
    if (score >= 50) return '#FFA500';
    return 'var(--gray-600)';
  };

  return (
    <div className="similarity-view">
      <header className="similarity-header">
        <div className="container">
          <div className="similarity-header-inner">
            <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <span className="logo-icon"></span>
              <span>Blueprint</span>
            </div>
          </div>
        </div>
      </header>

      <main className="similarity-main">
        <div className="container">
          <div className="similarity-top">
            <button onClick={() => navigate('/')} className="btn">← Back to Home</button>
            <h1 className="similarity-title">Similarity Checker</h1>
            <p className="similarity-subtitle">Check if a Devpost project is similar to existing projects</p>
          </div>

          <section className="similarity-form-section">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <input
                  type="url"
                  value={devpostUrl}
                  onChange={(e) => setDevpostUrl(e.target.value)}
                  placeholder="Enter Devpost project URL (e.g., https://devpost.com/software/project-name)"
                  className="form-input"
                  disabled={isChecking}
                  required
                />
                <button type="submit" className="btn btn-primary btn-large" disabled={isChecking}>
                  {isChecking ? (
                    <>
                      <span className="loading-spinner"></span>
                      Checking...
                    </>
                  ) : (
                    'Check Similarity'
                  )}
                </button>
              </div>
              {error && <div className="form-error">{error}</div>}
            </form>
          </section>

          {status && (
            <section className="status-card fade-in">
              <div className="status-content">
                {isChecking && <span className="loading-spinner"></span>}
                <div style={{ flex: 1 }}>
                  <div className="status-text">{status}</div>
                  {progress && <div className="status-progress">{progress}</div>}
                  {(sourceProgress.github > 0 || sourceProgress.devpost > 0) && (
                    <div className="status-progress" style={{ marginTop: 'var(--space-2)', display: 'flex', gap: 'var(--space-4)' }}>
                      <span>GitHub: <strong>{sourceProgress.github}</strong></span>
                      <span>Devpost: <strong>{sourceProgress.devpost}</strong></span>
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {result && (
            <section className="result-summary fade-in">
              <h2>Analysis Summary</h2>
              {result.project_name && (
                <div style={{ marginBottom: 'var(--space-4)', paddingBottom: 'var(--space-4)', borderBottom: '1px solid var(--gray-200)' }}>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: 'var(--black)', marginBottom: 'var(--space-1)' }}>
                    {result.project_name}
                  </div>
                  {result.submission_date && (
                    <div style={{ fontSize: '14px', color: 'var(--gray-600)' }}>
                      Submitted: {result.submission_date}
                    </div>
                  )}
                </div>
              )}
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Fraud Risk</span>
                  <span className="summary-value" style={{ color: getRiskColor(result.fraud_risk) }}>
                    {result.fraud_risk}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Originality Score</span>
                  <span className="summary-value">{result.originality_score}/100</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Similar Projects</span>
                  <span className="summary-value">{result.total_projects}</span>
                </div>
              </div>
            </section>
          )}

          {sortedProjects.length > 0 ? (
            <section className="projects-section">
              <h2 className="projects-title">Similar Projects Found ({sortedProjects.length})</h2>
              <div className="projects-list">
                {sortedProjects.map((project, index) => (
                  <div key={index} className="project-card fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
                    <div className="project-header">
                      <div>
                        <h3 className="project-name">{project.name}</h3>
                        <span className="project-platform">{project.platform}</span>
                      </div>
                      {project.ai_similarity !== undefined && (
                        <div className="similarity-badge" style={{ backgroundColor: getSimilarityColor(project.ai_similarity) }}>
                          {project.ai_similarity}% similar
                        </div>
                      )}
                    </div>

                    <p className="project-description">{project.description}</p>

                    {project.ai_reasoning && (
                      <div className="project-reasoning">
                        <strong>Analysis:</strong> {project.ai_reasoning}
                      </div>
                    )}

                    <div className="project-meta">
                      {project.platform === 'GitHub' ? (
                        <>
                          <span>{project.stars} stars</span>
                          <span>{project.language}</span>
                          {project.created_at && (
                            <span>{new Date(project.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                          )}
                        </>
                      ) : (
                        <>
                          <span>{project.likes} likes</span>
                          {project.is_winner && <span className="winner-badge">Winner</span>}
                          {project.submission_date && <span>{project.submission_date}</span>}
                          {project.comments !== undefined && <span>{project.comments} comments</span>}
                        </>
                      )}
                    </div>

                    <a href={project.url} target="_blank" rel="noopener noreferrer" className="project-link">
                      View Project →
                    </a>
                  </div>
                ))}
              </div>
            </section>
          ) : result && result.total_projects === 0 && (
            <section className="projects-section">
              <div className="no-results-card fade-in">
                <div style={{ fontSize: '48px', fontWeight: '700', color: 'var(--raycast-purple)', marginBottom: 'var(--space-4)' }}>✓</div>
                <h3 style={{ marginBottom: 'var(--space-2)', color: 'var(--gray-900)' }}>No Similar Projects Found</h3>
                <p style={{ color: 'var(--gray-600)', lineHeight: '1.6' }}>
                  Great news! Your project appears to be highly original. We couldn't find any similar projects on GitHub or Devpost.
                </p>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default SimilarityView;
