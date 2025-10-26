import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import './IdeaBreakdown.css';

function IdeaBreakdown() {
  const navigate = useNavigate();
  const location = useLocation();
  const [breakdown, setBreakdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [idea, setIdea] = useState(null);

  useEffect(() => {
    const ideaData = location.state?.idea;
    const hackathonFolder = location.state?.hackathon_folder;
    if (!ideaData) {
      navigate('/ideas');
      return;
    }
    setIdea(ideaData);
    document.title = `Blueprint - ${ideaData.title}`;
    generateBreakdown(ideaData, hackathonFolder);
  }, [location, navigate]);

  const generateBreakdown = async (ideaData, hackathonFolder) => {
    try {
      const controller = new AbortController();
      // Increased timeout to 2 minutes (120 seconds) to match backend
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch('http://localhost:8000/breakdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: ideaData, hackathon_folder: hackathonFolder }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate breakdown');
      }

      const data = await response.json();
      setBreakdown(data.breakdown);
      setLoading(false);
    } catch (error) {
      console.error('Error generating breakdown:', error);

      // If there's already content rendered, just stop loading and keep it
      // Don't show error message if we have content
      if (breakdown && breakdown.length > 0) {
        console.log('Content already rendered, ignoring error');
        setLoading(false);
        return;
      }

      // Only show error if no content was rendered
      if (error.name === 'AbortError') {
        setBreakdown('The request took too long. Please try again.');
      } else {
        setBreakdown(`Failed to generate implementation guide: ${error.message}`);
      }
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="breakdown-view">
        <header className="breakdown-header">
          <div className="container">
            <div className="breakdown-header-inner">
            <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <span className="logo-icon"></span>
              <span>Blueprint</span>
            </div>
            </div>
          </div>
        </header>
        <main className="breakdown-main">
          <div className="container">
            <div className="loading-breakdown">
              <span className="loading-spinner"></span>
              <div>
                <p className="loading-text">Generating implementation guide...</p>
                <p className="loading-subtext">Analyzing hackathon schedule and optimizing timeline</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="breakdown-view">
      <header className="breakdown-header">
        <div className="container">
          <div className="breakdown-header-inner">
            <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <span className="logo-icon"></span>
              <span>Blueprint</span>
            </div>
          </div>
        </div>
      </header>

      <main className="breakdown-main">
        <div className="container">
          <div className="breakdown-top">
            <button onClick={() => navigate('/ideas')} className="btn">← Back to Ideas</button>
            <h1 className="breakdown-title">{idea?.title}</h1>
            <p className="breakdown-subtitle">Step-by-Step Implementation Guide</p>
          </div>

          <div className="breakdown-content">
            <div className="summary-card">
              <div className="summary-grid">
                <div className="summary-item">
                  <h4>Problem Statement</h4>
                  <p>{idea?.problem}</p>
                </div>
                <div className="summary-item">
                  <h4>Solution Overview</h4>
                  <p>{idea?.solution}</p>
                </div>
                <div className="summary-item">
                  <h4>Key Technologies</h4>
                  <div className="tech-tags">
                    {idea?.technologies?.map((tech, idx) => (
                      <span key={idx} className="tech-tag">{tech}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="guide-card">
              <div className="markdown-content">
                <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                  {breakdown}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default IdeaBreakdown;
