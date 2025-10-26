import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

function App() {
  const navigate = useNavigate();
  const [hackathonUrl, setHackathonUrl] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    document.title = 'Blueprint - AI Hackathon Idea Generator';
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!hackathonUrl.trim()) {
      setError('Please enter a hackathon URL');
      return;
    }

    setIsGenerating(true);
    setError('');
    setProgress([]);
    setResult(null);
    setStatus('Starting idea generation...');

    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hackathon_url: hackathonUrl }),
      });

      if (!response.ok) throw new Error('Failed to generate ideas');

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
            if (data.progress) setProgress(prev => [...prev, data.progress]);
            if (data.result) {
              setResult(data.result);
              setStatus('Ideas generated successfully!');
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
      setStatus('Failed to generate ideas');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <span className="logo-icon"></span>
              <span>Blueprint</span>
            </div>
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container">
            <h1 className="hero-title">Generate Winning Hackathon Ideas</h1>
            <p className="hero-subtitle">
              AI-powered idea generation that learns from past hackathon winners to create tailored project concepts for your next competition
            </p>
          </div>
        </section>

        <section className="form-section">
          <div className="container">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <input
                  type="url"
                  value={hackathonUrl}
                  onChange={(e) => setHackathonUrl(e.target.value)}
                  placeholder="Enter hackathon URL (e.g., https://cal-hacks-12-0.devpost.com)"
                  className="form-input"
                  disabled={isGenerating}
                  required
                />
                <button type="submit" className="btn btn-primary btn-large" disabled={isGenerating}>
                  {isGenerating ? (
                    <>
                      <span className="loading-spinner"></span>
                      Generating...
                    </>
                  ) : (
                    'Generate Ideas'
                  )}
                </button>
              </div>
              {error && <div className="form-error">{error}</div>}
            </form>
          </div>
        </section>

        {status && (
          <section className="status-card fade-in">
            <div className="status-content">
              {isGenerating && <span className="loading-spinner"></span>}
              <span className="status-text">{status}</span>
            </div>
          </section>
        )}

        {progress.length > 0 && (
          <section className="progress-card fade-in">
            <h3 className="progress-title">Progress</h3>
            <div className="progress-list">
              {progress.map((item, index) => (
                <div key={index} className="progress-item">
                  <span className="progress-dot"></span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {result && (
          <section className="result-card fade-in">
            <h2 className="result-title">Ideas Generated Successfully</h2>
            <p className="result-subtitle">7 tailored project ideas ready for you</p>
            <div className="result-details">
              <div className="result-detail-item">
                <span className="result-detail-label">Output Directory</span>
                <code className="result-detail-value">{result.output_dir}</code>
              </div>
              <div className="result-detail-item">
                <span className="result-detail-label">Ideas File</span>
                <code className="result-detail-value">{result.ideas_file}</code>
              </div>
            </div>
            <button
              onClick={() => navigate('/ideas', { state: { ideas_file: result.ideas_file } })}
              className="btn btn-primary btn-large"
              style={{ width: '100%' }}
            >
              View Your Ideas
            </button>
          </section>
        )}

        {!isGenerating && !result && (
          <>
            <section className="features">
              <div className="container">
                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon">🎯</div>
                    <h3 className="feature-title">Smart Analysis</h3>
                    <p className="feature-description">
                      Analyze rules and requirements from your target hackathon
                    </p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">🏆</div>
                    <h3 className="feature-title">Learn from Winners</h3>
                    <p className="feature-description">
                      Study patterns from past hackathon winning projects
                    </p>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">🤖</div>
                    <h3 className="feature-title">AI-Powered</h3>
                    <p className="feature-description">
                      Claude AI generates 7 tailored ideas with implementation plans
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <section className="similarity-section">
              <div className="container">
                <div className="similarity-cta">
                  <h2 className="similarity-cta-title">Check Project Similarity</h2>
                  <p className="similarity-cta-text">
                    Analyze your Devpost project to find similar existing projects and assess originality
                  </p>
                  <button
                    onClick={() => navigate('/similarity')}
                    className="btn btn-primary btn-large"
                  >
                    Check Similarity
                  </button>
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <div className="container">
          <p className="footer-text">Built for hackathon enthusiasts</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
