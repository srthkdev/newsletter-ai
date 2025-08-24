"""
Newsletter Detail View - Beautiful Newsletter Display Page
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import time
import re
try:
    import html2text
except ImportError:
    html2text = None

# Page configuration
st.set_page_config(
    page_title="Newsletter Detail - Newsletter AI", 
    page_icon="📄", 
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for beautiful newsletter display
st.markdown(
    """
<style>
    .newsletter-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        color: #1a202c;
    }
    .newsletter-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .newsletter-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    .newsletter-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    .newsletter-meta {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1rem;
    }
    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #6b7280;
        font-size: 0.95rem;
    }
    .newsletter-summary {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #0ea5e9;
        margin: 2rem 0;
        color: #1e40af;
    }
    .newsletter-content {
        line-height: 1.8;
        font-size: 1.1rem;
        color: #2d3748;
    }
    .section-divider {
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        margin: 3rem auto;
        border-radius: 2px;
    }
    .content-section {
        margin: 2.5rem 0;
        padding: 1.5rem;
        background: #f8fafc;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a202c !important;
        margin-bottom: 1rem;
    }
    .article-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 3px solid #10b981;
    }
    .article-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a202c !important;
        margin-bottom: 0.75rem;
    }
    /* Ensure all headings are dark regardless of theme */
    h1, h2, h3, h4, h5, h6 {
        color: #1a202c !important;
    }
    /* Newsletter content text styling */
    .newsletter-container h1,
    .newsletter-container h2,
    .newsletter-container h3,
    .newsletter-container h4,
    .newsletter-container h5,
    .newsletter-container h6 {
        color: #1a202c !important;
    }
    /* Topic and section headings */
    .content-section h3,
    .content-section h4,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #1a202c !important;
    }
    .article-content {
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .article-url {
        color: #0ea5e9;
        text-decoration: none;
        font-weight: 500;
    }
    .article-url:hover {
        text-decoration: underline;
    }
    .sources-section {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 5px solid #22c55e;
    }
    .source-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        border-left: 3px solid #22c55e;
    }
    .source-title {
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    .source-summary {
        color: #6b7280;
        font-size: 0.95rem;
    }
    .action-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 3rem 0 2rem 0;
        flex-wrap: wrap;
    }
    .rating-section {
        background: linear-gradient(135deg, #fef7ff 0%, #f3e8ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #a855f7;
        margin: 2rem 0;
        text-align: center;
    }
    .mindmap-section {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #16a34a;
        margin: 2rem 0;
    }
    .mindmap-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        min-height: 400px;
        position: relative;
    }
    .mindmap-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .mindmap-title {
        color: #16a34a;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    .mindmap-controls {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        flex-wrap: wrap;
    }
    .mindmap-btn {
        background: #16a34a;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    .mindmap-btn:hover {
        background: #15803d;
        transform: translateY(-1px);
    }
    .mindmap-btn:active {
        transform: translateY(0);
    }
    .zoom-controls {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        background: #f8fafc;
        border-radius: 6px;
        padding: 0.25rem;
    }
    .zoom-btn {
        background: #64748b;
        color: white;
        border: none;
        width: 28px;
        height: 28px;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .zoom-btn:hover {
        background: #475569;
    }
    .zoom-level {
        font-size: 0.8rem;
        color: #64748b;
        min-width: 40px;
        text-align: center;
    }
    .mindmap-viewer {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
        background: #f8fafc;
        cursor: grab;
    }
    .mindmap-viewer:active {
        cursor: grabbing;
    }
    .mindmap-content {
        transition: transform 0.3s ease;
        transform-origin: center center;
    }
    .mindmap-fallback {
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        color: #64748b;
    }
    .star-rating {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        font-size: 2rem;
        margin: 1rem 0;
    }
    .navigation-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 10px;
    }
    .back-button {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .back-button:hover {
        background: #5a67d8;
        transform: translateY(-1px);
    }
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-sent {
        background: #d1fae5;
        color: #065f46;
    }
    .status-draft {
        background: #fef3c7;
        color: #92400e;
    }
    .status-ready {
        background: #dbeafe;
        color: #1e40af;
    }
    @media (max-width: 768px) {
        .newsletter-container {
            padding: 1rem;
        }
        .newsletter-title {
            font-size: 2rem;
        }
        .newsletter-meta {
            flex-direction: column;
            gap: 1rem;
        }
        .action-buttons {
            flex-direction: column;
            align-items: center;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_auth_headers():
    """Get authentication headers for API requests"""
    session_token = st.session_state.get("session_token")
    if session_token:
        return {"Authorization": f"Bearer {session_token}"}
    return {}


def get_newsletter_detail(newsletter_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed newsletter information"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            st.error("Please log in to view newsletters")
            return None
            
        response = requests.get(
            f"{API_BASE_URL}/newsletters/{newsletter_id}",
            headers=auth_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error("Newsletter not found")
            return None
        elif response.status_code == 401:
            st.error("Your session has expired. Please log in again.")
            st.switch_page("streamlit_app.py")
            return None
        else:
            st.error(f"Failed to fetch newsletter: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Please make sure the API is running.")
        return None
    except Exception as e:
        st.error(f"Error fetching newsletter: {str(e)}")
        return None


def format_content_sections(content_sections: list) -> str:
    """Format content sections for display without raw markdown syntax"""
    if not content_sections:
        return ""
    
    formatted_html = ""
    
    for section in content_sections:
        if isinstance(section, dict):
            section_title = section.get("title", "")
            articles = section.get("articles", [])
            
            if section_title:
                formatted_html += f'<div class="content-section">'
                formatted_html += f'<h3 class="section-title">{section_title}</h3>'
            
            for article in articles:
                if isinstance(article, dict):
                    formatted_html += '<div class="article-item">'
                    
                    if article.get("title"):
                        formatted_html += f'<h4 class="article-title">{article["title"]}</h4>'
                    
                    if article.get("content"):
                        content = article["content"]
                        # Clean and format the content
                        content = clean_markdown_content(content)
                        if len(content) > 500:
                            content = content[:500] + "..."
                        formatted_html += f'<div class="article-content">{content}</div>'
                    
                    if article.get("url"):
                        formatted_html += f'<a href="{article["url"]}" class="article-url" target="_blank">Read full article →</a>'
                    
                    formatted_html += '</div>'
                    
                elif isinstance(article, str):
                    # Handle string articles (already formatted content) - clean markdown
                    cleaned_content = clean_markdown_content(article)
                    formatted_html += f'<div class="article-item">'
                    formatted_html += f'<div class="article-content">{cleaned_content}</div>'
                    formatted_html += '</div>'
            
            if section_title:
                formatted_html += '</div>'
    
    return formatted_html


def clean_markdown_content(content: str) -> str:
    """Clean markdown content for HTML display"""
    if not content:
        return ""
    
    # Remove common markdown syntax but preserve basic formatting
    cleaned = content
    
    # Convert markdown links [text](url) to HTML links
    cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', cleaned)
    
    # Convert **bold** to <strong>
    cleaned = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', cleaned)
    
    # Convert *italic* to <em>
    cleaned = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', cleaned)
    
    # Convert headers to appropriate HTML tags
    cleaned = re.sub(r'^### (.+)$', r'<h4>\1</h4>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^## (.+)$', r'<h3>\1</h3>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^# (.+)$', r'<h2>\1</h2>', cleaned, flags=re.MULTILINE)
    
    # Convert line breaks to HTML
    cleaned = cleaned.replace('\n\n', '<br><br>')
    cleaned = cleaned.replace('\n', '<br>')
    
    # Remove any remaining markdown syntax artifacts
    cleaned = re.sub(r'\*{1,2}', '', cleaned)  # Remove stray asterisks
    cleaned = re.sub(r'#{1,6}\s*', '', cleaned)  # Remove stray headers
    
    return cleaned


def convert_html_to_text(html_content: str) -> str:
    """Convert HTML content to readable text"""
    if not html_content:
        return ""
    
    if html2text:
        try:
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            return h.handle(html_content)
        except:
            pass
    
    # Fallback: simple HTML tag removal
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_content)


def display_newsletter_rating(newsletter_id: str, current_rating: int = 0) -> Optional[int]:
    """Display newsletter rating interface"""
    st.markdown('<div class="rating-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #a855f7; margin-bottom: 1rem;">Rate this Newsletter</h3>', unsafe_allow_html=True)
    
    # Star rating display
    col1, col2, col3, col4, col5 = st.columns(5)
    rating = None
    
    with col1:
        if st.button("⭐" if current_rating >= 1 else "☆", key=f"star1_{newsletter_id}", help="1 star"):
            rating = 1
    with col2:
        if st.button("⭐" if current_rating >= 2 else "☆", key=f"star2_{newsletter_id}", help="2 stars"):
            rating = 2
    with col3:
        if st.button("⭐" if current_rating >= 3 else "☆", key=f"star3_{newsletter_id}", help="3 stars"):
            rating = 3
    with col4:
        if st.button("⭐" if current_rating >= 4 else "☆", key=f"star4_{newsletter_id}", help="4 stars"):
            rating = 4
    with col5:
        if st.button("⭐" if current_rating >= 5 else "☆", key=f"star5_{newsletter_id}", help="5 stars"):
            rating = 5
    
    # Feedback input
    feedback = st.text_area(
        "Optional feedback:", 
        placeholder="What did you think about this newsletter?",
        key=f"feedback_{newsletter_id}"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return rating, feedback


def rate_newsletter(newsletter_id: str, rating: int, feedback: str = None) -> tuple[bool, str]:
    """Rate a newsletter"""
    try:
        user_id = st.session_state.get("user_id", 1)
        
        response = requests.post(
            f"{API_BASE_URL}/newsletters/rate",
            params={
                "user_id": user_id,
                "newsletter_id": newsletter_id,
                "rating": rating,
                "feedback": feedback
            },
            timeout=10,
        )
        
        if response.status_code == 200:
            return True, "Newsletter rated successfully!"
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to rate newsletter")
            
    except Exception as e:
        return False, f"Error rating newsletter: {str(e)}"


def display_newsletter_mindmap(newsletter: Dict[str, Any]) -> None:
    """Display newsletter mindmap with zoom controls and download options"""
    mindmap_markdown = newsletter.get('mindmap_markdown')
    mindmap_svg = newsletter.get('mindmap_svg', '')
    
    if not mindmap_markdown:
        # Check if we can generate a mindmap
        st.markdown(
            '''
            <div class="mindmap-section">
                <div class="mindmap-header">
                    <h3 class="mindmap-title">🎨 Newsletter Mindmap</h3>
                </div>
                <div class="mindmap-fallback">
                    <h4>🗺️ No Mindmap Available</h4>
                    <p>This newsletter doesn't have a mindmap yet. Mindmaps provide visual keyword overviews of newsletter content.</p>
                    <p><strong>Note:</strong> Mindmaps are automatically generated for new newsletters with keyword analysis.</p>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        return
    
    # Display mindmap section with enhanced controls
    st.markdown(
        '''
        <div class="mindmap-section">
            <div class="mindmap-header">
                <h3 class="mindmap-title">🎨 Newsletter Keywords Mindmap</h3>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    # Create control panel
    control_col1, control_col2, control_col3 = st.columns([2, 2, 2])
    
    with control_col1:
        if st.button("🔍 Reset View", key="reset_mindmap"):
            st.rerun()
    
    with control_col2:
        if st.button("📱 Fullscreen", key="fullscreen_mindmap"):
            st.info("Click the expand button in the mindmap viewer for fullscreen mode")
    
    with control_col3:
        # SVG Download button
        if mindmap_svg:
            st.download_button(
                label="💾 Download SVG",
                data=mindmap_svg,
                file_name=f"mindmap_{newsletter.get('title', 'newsletter').replace(' ', '_')}.svg",
                mime="image/svg+xml",
                key="download_mindmap_svg"
            )
        else:
            st.button("💾 SVG Unavailable", disabled=True, key="no_svg")
    
    # Create tabs for different views
    mindmap_tab1, mindmap_tab2, mindmap_tab3 = st.columns([3, 1, 1])
    
    with mindmap_tab1:
        st.markdown("**🗺️ Interactive Keywords Mindmap**")
        
        # Enhanced mindmap rendering with zoom controls
        try:
            # Check if it's Mermaid format
            if mindmap_markdown.strip().startswith('mindmap'):
                # Enhanced Mermaid component with zoom and pan controls
                mindmap_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
                    <style>
                        body {{ 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            margin: 0; 
                            padding: 20px; 
                            background: white;
                            overflow: hidden;
                        }}
                        .mindmap-viewer {{
                            display: flex;
                            flex-direction: column;
                            height: 500px;
                            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                            border-radius: 12px;
                            padding: 10px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            position: relative;
                        }}
                        .mindmap-controls {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 10px;
                            background: rgba(255, 255, 255, 0.9);
                            border-radius: 8px;
                            margin-bottom: 10px;
                            backdrop-filter: blur(5px);
                        }}
                        .zoom-controls {{
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        }}
                        .zoom-btn {{
                            background: #16a34a;
                            color: white;
                            border: none;
                            width: 32px;
                            height: 32px;
                            border-radius: 6px;
                            font-size: 16px;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: all 0.2s ease;
                        }}
                        .zoom-btn:hover {{
                            background: #15803d;
                            transform: scale(1.05);
                        }}
                        .zoom-level {{
                            background: #f1f5f9;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 0.85rem;
                            color: #64748b;
                            min-width: 50px;
                            text-align: center;
                        }}
                        .control-btn {{
                            background: #6366f1;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 6px;
                            font-size: 0.85rem;
                            cursor: pointer;
                            transition: all 0.2s ease;
                        }}
                        .control-btn:hover {{
                            background: #4f46e5;
                        }}
                        .mindmap-container {{
                            flex: 1;
                            overflow: hidden;
                            border-radius: 8px;
                            position: relative;
                            cursor: grab;
                        }}
                        .mindmap-container:active {{
                            cursor: grabbing;
                        }}
                        .mermaid {{
                            width: 100%;
                            height: 100%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: transform 0.3s ease;
                            transform-origin: center center;
                        }}
                        .error-message {{
                            color: #dc2626;
                            background: #fef2f2;
                            padding: 16px;
                            border-radius: 8px;
                            border: 1px solid #fecaca;
                            text-align: center;
                        }}
                    </style>
                </head>
                <body>
                    <div class="mindmap-viewer">
                        <div class="mindmap-controls">
                            <div class="zoom-controls">
                                <button class="zoom-btn" onclick="zoomOut()" title="Zoom Out">−</button>
                                <div class="zoom-level" id="zoomLevel">100%</div>
                                <button class="zoom-btn" onclick="zoomIn()" title="Zoom In">+</button>
                            </div>
                            <div>
                                <button class="control-btn" onclick="resetView()" title="Reset View">🔄 Reset</button>
                                <button class="control-btn" onclick="downloadSVG()" title="Download SVG">💾 SVG</button>
                            </div>
                        </div>
                        <div class="mindmap-container" id="mindmapContainer">
                            <div class="mermaid" id="mindmap">
                                {mindmap_markdown}
                            </div>
                        </div>
                    </div>
                    
                    <script>
                        let currentZoom = 1;
                        let isDragging = false;
                        let startX, startY, currentX = 0, currentY = 0;
                        
                        // Initialize Mermaid
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            mindmap: {{
                                padding: 10,
                                maxNodeTextLength: 50,
                                curve: 'basis'
                            }},
                            flowchart: {{
                                htmlLabels: true,
                                curve: 'basis'
                            }}
                        }});
                        
                        // Zoom functions
                        function zoomIn() {{
                            currentZoom = Math.min(currentZoom * 1.2, 3);
                            updateTransform();
                        }}
                        
                        function zoomOut() {{
                            currentZoom = Math.max(currentZoom / 1.2, 0.3);
                            updateTransform();
                        }}
                        
                        function resetView() {{
                            currentZoom = 1;
                            currentX = 0;
                            currentY = 0;
                            updateTransform();
                        }}
                        
                        function updateTransform() {{
                            const mindmap = document.getElementById('mindmap');
                            mindmap.style.transform = `translate(${{currentX}}px, ${{currentY}}px) scale(${{currentZoom}})`;
                            document.getElementById('zoomLevel').textContent = Math.round(currentZoom * 100) + '%';
                        }}
                        
                        // Pan functionality
                        const container = document.getElementById('mindmapContainer');
                        
                        container.addEventListener('mousedown', (e) => {{
                            isDragging = true;
                            startX = e.clientX - currentX;
                            startY = e.clientY - currentY;
                            container.style.cursor = 'grabbing';
                        }});
                        
                        container.addEventListener('mousemove', (e) => {{
                            if (!isDragging) return;
                            currentX = e.clientX - startX;
                            currentY = e.clientY - startY;
                            updateTransform();
                        }});
                        
                        container.addEventListener('mouseup', () => {{
                            isDragging = false;
                            container.style.cursor = 'grab';
                        }});
                        
                        // Wheel zoom
                        container.addEventListener('wheel', (e) => {{
                            e.preventDefault();
                            if (e.deltaY < 0) {{
                                zoomIn();
                            }} else {{
                                zoomOut();
                            }}
                        }});
                        
                        // Download SVG function
                        function downloadSVG() {{
                            try {{
                                const svg = document.querySelector('#mindmap svg');
                                if (svg) {{
                                    const svgData = new XMLSerializer().serializeToString(svg);
                                    const blob = new Blob([svgData], {{type: 'image/svg+xml'}});
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = 'mindmap.svg';
                                    a.click();
                                    URL.revokeObjectURL(url);
                                }} else {{
                                    alert('SVG not available for download');
                                }}
                            }} catch (error) {{
                                console.error('Download error:', error);
                                alert('Error downloading SVG');
                            }}
                        }}
                        
                        // Error handling
                        mermaid.parseError = function(err, hash) {{
                            console.error('Mermaid parsing error:', err);
                            document.getElementById('mindmap').innerHTML = 
                                '<div class="error-message">❌ Error rendering mindmap. Please check the source format.</div>';
                        }};
                        
                        // Render the mindmap
                        try {{
                            mermaid.init(undefined, document.getElementById('mindmap'));
                        }} catch (error) {{
                            console.error('Mermaid render error:', error);
                            document.getElementById('mindmap').innerHTML = 
                                '<div class="error-message">⚠️ Mindmap rendering failed. Showing source content.</div>';
                        }}
                    </script>
                </body>
                </html>
                """
                
                # Display the enhanced interactive Mermaid mindmap
                st.components.v1.html(mindmap_html, height=600, scrolling=False)
                
            else:
                # Legacy markdown format - convert to visual tree
                st.markdown("**📋 Mindmap Structure**")
                
                # Process markdown mindmap into visual format
                lines = mindmap_markdown.split('\n')
                processed_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Count indentation level
                    indent_level = (len(line) - len(line.lstrip())) // 2
                    content = line.lstrip('- #').strip()
                    
                    if content:
                        # Create visual tree structure
                        prefix = "  " * indent_level
                        if indent_level == 0:
                            emoji = "🎯"
                        elif indent_level == 1:
                            emoji = "📂"
                        elif indent_level == 2:
                            emoji = "📄"
                        else:
                            emoji = "🔹"
                        
                        processed_lines.append(f"{prefix}{emoji} **{content}**")
                
                # Display as formatted markdown
                mindmap_display = "\n".join(processed_lines)
                st.markdown(mindmap_display)
            
        except Exception as e:
            # Fallback to plain markdown display
            st.error(f"Error rendering mindmap: {str(e)}")
            st.markdown("**Mindmap Preview:**")
            with st.expander("🗺️ View Mindmap Content", expanded=True):
                # Clean and display the mindmap content
                cleaned_content = clean_markdown_content(mindmap_markdown)
                st.markdown(cleaned_content, unsafe_allow_html=True)
    
    with mindmap_tab2:
        st.markdown("**📄 Mindmap Source**")
        
        # Show mindmap metadata
        mindmap_data = newsletter.get('mindmap_agent_data', {})
        if mindmap_data:
            st.markdown("**Generation Info:**")
            metadata = mindmap_data.get('metadata', {})
            if metadata:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Topics", metadata.get('topics_count', 0))
                with col2:
                    st.metric("Articles", metadata.get('articles_count', 0))
        
        # Download options
        st.markdown("**💾 Export Options:**")
        
        # Markdown download
        st.download_button(
            label="📄 Download Markdown",
            data=mindmap_markdown,
            file_name=f"mindmap_{newsletter.get('title', 'newsletter').replace(' ', '_')}.md",
            mime="text/markdown"
        )
        
        # Text preview
        with st.expander("🔍 Preview Source"):
            st.code(mindmap_markdown[:500] + "..." if len(mindmap_markdown) > 500 else mindmap_markdown, language="markdown")


def get_newsletter_rating(newsletter_id: str) -> Optional[Dict[str, Any]]:
    """Get existing rating for a newsletter"""
    try:
        user_id = st.session_state.get("user_id", 1)
        
        response = requests.get(
            f"{API_BASE_URL}/newsletters/rating/{user_id}/{newsletter_id}",
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("rating")
        return None
        
    except Exception:
        return None
    """Get existing rating for a newsletter"""
    try:
        user_id = st.session_state.get("user_id", 1)
        
        response = requests.get(
            f"{API_BASE_URL}/newsletters/rating/{user_id}/{newsletter_id}",
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("rating")
        return None
        
    except Exception:
        return None


def main():
    """Main newsletter detail page"""
    # Check authentication
    session_token = st.session_state.get("session_token")
    if not session_token:
        st.error("🔒 Please log in to view newsletters")
        if st.button("Go to Login", type="primary"):
            st.switch_page("streamlit_app.py")
        return

    # Get newsletter ID from session state
    newsletter_id = st.session_state.get("newsletter_id")
    
    if not newsletter_id:
        st.error("No newsletter specified")
        if st.button("← Back to Dashboard"):
            st.switch_page("pages/1_📊_Dashboard.py")
        return

    # Navigation header
    st.markdown(
        """
        <div class="navigation-header">
            <div style="display: flex; align-items: center; gap: 1rem; width: 100%;">
                <div style="flex: 1;">
                    <h2 style="margin: 0; color: #1a202c;">📄 Newsletter Detail</h2>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Back button
    if st.button("← Back to Dashboard", key="back_to_dashboard"):
        st.switch_page("pages/1_📊_Dashboard.py")

    # Fetch newsletter data
    with st.spinner("Loading newsletter..."):
        newsletter = get_newsletter_detail(newsletter_id)
    
    if not newsletter:
        st.error("Failed to load newsletter")
        return
    
    # Newsletter container
    st.markdown('<div class="newsletter-container">', unsafe_allow_html=True)
    
    # Newsletter header
    st.markdown(
        f"""
        <div class="newsletter-header">
            <h1 class="newsletter-title">{newsletter.get('title', 'Untitled Newsletter')}</h1>
            <div class="newsletter-meta">
                <div class="meta-item">
                    <span>📅</span>
                    <span>{datetime.fromisoformat(newsletter.get('created_at', '').replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p') if newsletter.get('created_at') else 'Unknown date'}</span>
                </div>
                <div class="meta-item">
                    <span>📊</span>
                    <span class="status-badge status-{newsletter.get('status', 'draft')}">{newsletter.get('status', 'Unknown').upper()}</span>
                </div>
                <div class="meta-item">
                    <span>📖</span>
                    <span>{len(newsletter.get('content_sections', []))} sections</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Newsletter summary
    if newsletter.get('summary'):
        st.markdown(
            f"""
            <div class="newsletter-summary">
                <h3 style="color: #1e40af; margin-bottom: 1rem;">📋 Summary</h3>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6;">{newsletter.get('summary')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Main content
    st.markdown('<div class="newsletter-content">', unsafe_allow_html=True)
    
    # Display content sections if available
    content_sections = newsletter.get('content_sections', [])
    if content_sections:
        sections_html = format_content_sections(content_sections)
        if sections_html:
            st.markdown(sections_html, unsafe_allow_html=True)
    
    # Display main content if no sections
    main_content = newsletter.get('content') or newsletter.get('main_content')
    if main_content and not content_sections:
        st.markdown(
            f"""
            <div class="content-section">
                <div class="article-content">{main_content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Display HTML content as fallback
    html_content = newsletter.get('html_content')
    if html_content and not main_content and not content_sections:
        text_content = convert_html_to_text(html_content)
        st.markdown(
            f"""
            <div class="content-section">
                <div class="article-content">{text_content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Display mindmap if available
    display_newsletter_mindmap(newsletter)
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Sources section
    sources = newsletter.get('sources_used', [])
    if sources:
        st.markdown(
            """
            <div class="sources-section">
                <h3 style="color: #22c55e; margin-bottom: 1.5rem;">📚 Sources</h3>
            """,
            unsafe_allow_html=True
        )
        
        for source in sources[:5]:  # Limit to 5 sources
            if isinstance(source, dict):
                st.markdown(
                    f"""
                    <div class="source-item">
                        <div class="source-title">{source.get('title', 'Unknown Source')}</div>
                        <div class="source-summary">{source.get('summary', 'No summary available')}</div>
                        {f'<a href="{source.get("url", "")}" target="_blank" style="color: #22c55e; font-weight: 500;">Visit source →</a>' if source.get('url') else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Rating section
    existing_rating = get_newsletter_rating(newsletter_id)
    current_rating = existing_rating.get("overall_rating", 0) if existing_rating else 0
    
    rating, feedback = display_newsletter_rating(newsletter_id, current_rating)
    
    # Process rating if changed
    if rating and rating != current_rating:
        with st.spinner("Saving your rating..."):
            success, message = rate_newsletter(newsletter_id, rating, feedback)
        
        if success:
            st.success(f"✅ Rated {rating} stars!")
            st.rerun()
        else:
            st.error(f"❌ {message}")
    
    # Action buttons
    st.markdown(
        """
        <div class="action-buttons">
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📧 Resend Email", use_container_width=True):
            st.info("🚧 Resend functionality coming soon!")
    
    with col2:
        if st.button("🔄 Create Similar", use_container_width=True):
            st.info("🚧 Create similar newsletter coming soon!")
    
    with col3:
        if st.button("🎨 Regenerate Mindmap", use_container_width=True):
            with st.spinner("Regenerating mindmap..."):
                try:
                    auth_headers = get_auth_headers()
                    response = requests.post(
                        f"{API_BASE_URL}/newsletters/mindmap/{newsletter_id}",
                        headers=auth_headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Mindmap regenerated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to regenerate mindmap")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/📈_Analytics.py")
    
    with col5:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close newsletter container
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()