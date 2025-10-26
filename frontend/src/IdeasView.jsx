import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './IdeasView.css';

function IdeasView() {
  const navigate = useNavigate();
  const location = useLocation();
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.title = 'Blueprint - Your Ideas';
    const ideasFile = location.state?.ideas_file;
    if (!ideasFile) {
      navigate('/');
      return;
    }
    fetchIdeas(ideasFile);
  }, [location, navigate]);

  const fetchIdeas = async (filePath) => {
    try {
      const response = await fetch(`http://localhost:8000/ideas/${encodeURIComponent(filePath)}`);
      if (!response.ok) throw new Error('Failed to fetch ideas');
      const data = await response.json();
      setIdeas(data.ideas);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching ideas:', error);
      setIdeas(parseMockIdeas());
      setLoading(false);
    }
  };

  const parseMockIdeas = () => {
    return Array.from({ length: 7 }, (_, i) => ({
      number: i + 1,
      title: `Innovative Idea ${i + 1}`,
      problem: 'Sample problem statement describing the issue being addressed.',
      solution: 'Solution overview explaining how the project works.',
      technologies: ['React', 'Python', 'Claude AI', 'FastAPI'],
      whyItWins: ['Aligns with themes', 'Innovative', 'Feasible', 'High impact'],
      inspiredBy: 'Past winning projects',
      roadmap: ['Setup', 'Core features', 'APIs', 'Test', 'Demo']
    }));
  };

  const handleIdeaClick = (idea) => {
    const ideasFile = location.state?.ideas_file || '';
    const hackathonFolder = ideasFile.split('/')[0] || ideasFile.split('\\')[0];
    navigate('/breakdown', { state: { idea, hackathon_folder: hackathonFolder } });
  };

  const renderIdeaCard = (idea) => (
    <div className="idea-card" onClick={() => handleIdeaClick(idea)} key={idea.number}>
      <div className="idea-header">
        <div className="idea-header-left">
          <div className="idea-number">Idea {idea.number}</div>
          <h3 className="idea-title">{idea.title}</h3>
        </div>
        <div className="click-hint">View details →</div>
      </div>

      <div className="idea-content">
        <div className="idea-two-col">
          <div className="idea-section">
            <h4>Problem Statement</h4>
            <p>{idea.problem}</p>
          </div>

          <div className="idea-section">
            <h4>Solution Overview</h4>
            <p>{idea.solution}</p>
          </div>
        </div>

        <div className="idea-section">
          <h4>Key Technologies</h4>
          <div className="tech-tags">
            {idea.technologies.map((tech, idx) => (
              <span key={idx} className="tech-tag">{tech}</span>
            ))}
          </div>
        </div>

        <div className="idea-section">
          <h4>Why It Wins</h4>
          <ul>
            {idea.whyItWins.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>

        <div className="idea-two-col">
          <div className="idea-section">
            <h4>Inspired By</h4>
            <p>{idea.inspiredBy}</p>
          </div>

          <div className="idea-section">
            <h4>Implementation Steps</h4>
            <ul>
              {idea.roadmap.slice(0, 3).map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="ideas-view">
        <header className="ideas-header">
          <div className="container">
            <div className="ideas-header-inner">
              <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
                <span className="logo-icon"></span>
                <span>Blueprint</span>
              </div>
            </div>
          </div>
        </header>
        <main className="ideas-main">
          <div className="container">
            <div className="loading">
              <span className="loading-spinner"></span>
              <span>Loading ideas...</span>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="ideas-view">
      <header className="ideas-header">
        <div className="container">
          <div className="ideas-header-inner">
            <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <span className="logo-icon"></span>
              <span>Blueprint</span>
            </div>
          </div>
        </div>
      </header>

      <main className="ideas-main">
        <div className="container">
          <div className="ideas-top">
            <button onClick={() => navigate('/')} className="btn">← Back to Home</button>
            <h1 className="ideas-title">Your Generated Ideas</h1>
            <p className="ideas-subtitle">7 innovative project ideas tailored to your hackathon</p>
          </div>

          <div className="ideas-list">
            {ideas.map(idea => renderIdeaCard(idea))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default IdeasView;
