---
layout: default
title: Home
---

<style>
  .hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
    margin: -2rem -2rem 3rem -2rem;
    border-radius: 0 0 20px 20px;
  }
  
  .hero-title {
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-bottom: 2rem;
  }
  
  .search-container {
    max-width: 600px;
    margin: 0 auto 3rem auto;
    position: relative;
  }
  
  .search-input {
    width: 100%;
    padding: 1rem 1.5rem;
    font-size: 1.1rem;
    border: 2px solid #e1e5e9;
    border-radius: 50px;
    outline: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  
  .search-input:focus {
    border-color: #667eea;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    transform: translateY(-2px);
  }
  
  .search-results {
    margin-top: 2rem;
    max-height: 600px;
    overflow-y: auto;
  }
  
  .search-result {
    background: white;
    border: 1px solid #e1e5e9;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }
  
  .search-result:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }
  
  .result-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    display: block;
    margin-bottom: 0.5rem;
  }
  
  .result-title:hover {
    color: #667eea;
  }
  
  .result-meta {
    color: #7f8c8d;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }
  
  .result-snippet {
    color: #34495e;
    line-height: 1.6;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
  }
  
  .stat-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
  }
  
  .stat-card:hover {
    transform: translateY(-4px);
  }
  
  .stat-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #667eea;
    display: block;
  }
  
  .stat-label {
    color: #7f8c8d;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  
  .recent-videos {
    margin-top: 3rem;
  }
  
  .section-title {
    font-size: 2rem;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 2rem;
    text-align: center;
  }
  
  .video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }
  
  .video-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }
  
  .video-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
  }
  
  .video-thumbnail {
    width: 100%;
    height: 180px;
    background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 3rem;
  }
  
  .video-info {
    padding: 1.5rem;
  }
  
  .video-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 0.5rem;
    text-decoration: none;
  }
  
  .video-title:hover {
    color: #667eea;
  }
  
  .video-meta {
    color: #7f8c8d;
    font-size: 0.9rem;
  }
  
  .loading {
    text-align: center;
    color: #7f8c8d;
    font-style: italic;
  }
  
  .no-results {
    text-align: center;
    color: #7f8c8d;
    font-style: italic;
    padding: 2rem;
  }
  
  @media (max-width: 768px) {
    .hero-title {
      font-size: 2rem;
    }
    
    .hero-section {
      padding: 2rem 1rem;
      margin: -1rem -1rem 2rem -1rem;
    }
    
    .search-container {
      margin: 0 auto 2rem auto;
    }
  }
</style>

<div class="hero-section">
  <h1 class="hero-title">🛸 UAPGerb Video Wiki</h1>
  <p class="hero-subtitle">Automatically maintained archive with searchable transcripts from the @UAPGerb YouTube channel</p>
</div>

<div class="search-container">
  <input 
    type="text" 
    id="search-input" 
    class="search-input"
    placeholder="🔍 Search videos and transcripts..." 
    autocomplete="off"
  >
  <div id="search-results" class="search-results"></div>
</div>

<div class="stats-grid" id="stats-grid">
  <div class="stat-card">
    <span class="stat-number" id="total-videos">-</span>
    <span class="stat-label">Total Videos</span>
  </div>
  <div class="stat-card">
    <span class="stat-number" id="total-transcripts">-</span>
    <span class="stat-label">With Transcripts</span>
  </div>
  <div class="stat-card">
    <span class="stat-number" id="last-updated">-</span>
    <span class="stat-label">Last Updated</span>
  </div>
</div>

<div class="recent-videos">
  <h2 class="section-title">📺 Recent Videos</h2>
  <div id="recent-videos-grid" class="video-grid">
    <div class="loading">Loading recent videos...</div>
  </div>
</div>

<script src="https://unpkg.com/lunr/lunr.js"></script>
<script>
let searchIndex;
let documents = [];
let recentVideos = [];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
  loadSearchData();
  loadRecentVideos();
});

// Load search data
async function loadSearchData() {
  try {
    const response = await fetch('/_data/search.json');
    const data = await response.json();
    documents = data;
    
    // Update stats
    document.getElementById('total-videos').textContent = data.length;
    document.getElementById('total-transcripts').textContent = 
      data.filter(doc => !doc.body.includes('Error fetching transcript')).length;
    document.getElementById('last-updated').textContent = 'Today';
    
    // Build Lunr index
    searchIndex = lunr(function () {
      this.ref('url');
      this.field('title', { boost: 10 });
      this.field('body');
      
      data.forEach(doc => {
        this.add(doc);
      });
    });
    
    // Enable search
    document.getElementById('search-input').addEventListener('input', performSearch);
    
  } catch (error) {
    console.log('Search index not yet available:', error);
    document.getElementById('total-videos').textContent = '0';
    document.getElementById('total-transcripts').textContent = '0';
  }
}

// Load recent videos
async function loadRecentVideos() {
  try {
    const response = await fetch('/_data/recent.json');
    const data = await response.json();
    recentVideos = data;
    
    displayRecentVideos(data.slice(0, 6)); // Show top 6
    
  } catch (error) {
    console.log('Recent videos not yet available:', error);
    document.getElementById('recent-videos-grid').innerHTML = 
      '<div class="no-results">Recent videos will appear here after the first sync.</div>';
  }
}

// Display recent videos
function displayRecentVideos(videos) {
  const grid = document.getElementById('recent-videos-grid');
  
  if (videos.length === 0) {
    grid.innerHTML = '<div class="no-results">No videos found.</div>';
    return;
  }
  
  const html = videos.map(video => `
    <div class="video-card">
      <div class="video-thumbnail">🎥</div>
      <div class="video-info">
        <a href="${video.url}" class="video-title">${video.title}</a>
        <div class="video-meta">
          ${video.date} • ${video.duration}
        </div>
      </div>
    </div>
  `).join('');
  
  grid.innerHTML = html;
}

// Perform search
function performSearch() {
  const query = document.getElementById('search-input').value.trim();
  const resultsDiv = document.getElementById('search-results');
  
  if (!query) {
    resultsDiv.innerHTML = '';
    return;
  }
  
  if (!searchIndex) {
    resultsDiv.innerHTML = '<div class="no-results">Search index is loading...</div>';
    return;
  }
  
  try {
    const results = searchIndex.search(query);
    
    if (results.length === 0) {
      resultsDiv.innerHTML = '<div class="no-results">No results found for "' + query + '"</div>';
      return;
    }
    
    const html = results.slice(0, 10).map(result => {
      const doc = documents.find(d => d.url === result.ref);
      const snippet = highlightSearchTerms(doc.body.substring(0, 200), query);
      
      return `
        <div class="search-result">
          <a href="${doc.url}" class="result-title">${doc.title}</a>
          <div class="result-meta">${doc.date} • ${doc.duration}</div>
          <div class="result-snippet">${snippet}...</div>
        </div>
      `;
    }).join('');
    
    resultsDiv.innerHTML = html;
    
  } catch (error) {
    resultsDiv.innerHTML = '<div class="no-results">Search error. Please try a different query.</div>';
  }
}

// Highlight search terms in text
function highlightSearchTerms(text, query) {
  const terms = query.toLowerCase().split(' ').filter(term => term.length > 2);
  let highlightedText = text;
  
  terms.forEach(term => {
    const regex = new RegExp(`(${term})`, 'gi');
    highlightedText = highlightedText.replace(regex, '<strong>$1</strong>');
  });
  
  return highlightedText;
}

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
  
  // Add loading animation to search input
  const searchInput = document.getElementById('search-input');
  let searchTimeout;
  
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      // Add subtle loading indicator if needed
    }, 300);
  });
});
</script>

