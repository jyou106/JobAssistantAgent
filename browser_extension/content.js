// AI Career Assistant - Content Script
// Integrates with your FastAPI backend to provide real-time resume matching

class AICareerAssistant {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:8000';
        this.currentJobUrl = window.location.href;
        this.resumeText = '';
        this.userId = 'user_' + Date.now();
        this.matchData = null;
        
        this.init();
    }

    async init() {
        console.log('🤖 AI Career Assistant activated!');
        
        // Load saved resume
        await this.loadSavedResume();
        
        // Create the match score UI
        this.createMatchScoreUI();
        
        // Auto-analyze if resume is available
        if (this.resumeText) {
            await this.analyzeCurrentJob();
        }
        
        // Listen for URL changes (SPAs)
        this.observeUrlChanges();
    }

    async loadSavedResume() {
        try {
            const result = await chrome.storage.local.get(['savedResume']);
            if (result.savedResume) {
                this.resumeText = result.savedResume;
                console.log('✅ Resume loaded from storage');
            }
        } catch (error) {
            console.error('Error loading resume:', error);
        }
    }

    createMatchScoreUI() {
        // Remove existing UI if present
        const existing = document.getElementById('ai-career-assistant');
        if (existing) existing.remove();

        // Create floating widget
        const widget = document.createElement('div');
        widget.id = 'ai-career-assistant';
        widget.className = 'ai-assistant-widget';
        
        widget.innerHTML = `
            <div class="ai-widget-header">
                <div class="ai-logo">🤖</div>
                <span class="ai-title">AI Career Assistant</span>
                <button class="ai-minimize" id="ai-minimize">−</button>
            </div>
            <div class="ai-widget-content" id="ai-content">
                <div class="ai-match-score" id="ai-match-score">
                    <div class="score-circle" id="score-circle">
                        <span id="score-text">?</span>
                    </div>
                    <div class="score-label">Resume Match</div>
                </div>
                
                <div class="ai-insights" id="ai-insights">
                    <div class="insight-item" id="loading-state">
                        <span class="loading-spinner">⏳</span>
                        <span>Analyzing job posting...</span>
                    </div>
                </div>
                
                <div class="ai-actions">
                    <button class="ai-btn primary" id="analyze-btn">Analyze Job</button>
                    <button class="ai-btn secondary" id="upload-resume-btn">Upload Resume</button>
                    <button class="ai-btn secondary" id="detailed-view-btn">View Details</button>
                </div>
                
                <div class="ai-status" id="ai-status">
                    Ready to analyze
                </div>
            </div>
        `;

        document.body.appendChild(widget);
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Minimize/expand widget
        document.getElementById('ai-minimize').addEventListener('click', () => {
            const content = document.getElementById('ai-content');
            const isHidden = content.style.display === 'none';
            content.style.display = isHidden ? 'block' : 'none';
            document.getElementById('ai-minimize').textContent = isHidden ? '−' : '+';
        });

        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.analyzeCurrentJob();
        });

        // Upload resume button
        document.getElementById('upload-resume-btn').addEventListener('click', () => {
            this.openResumeUpload();
        });

        // Detailed view button
        document.getElementById('detailed-view-btn').addEventListener('click', () => {
            this.openDetailedView();
        });
    }

    async analyzeCurrentJob() {
        if (!this.resumeText) {
            this.updateStatus('Please upload your resume first', 'warning');
            return;
        }

        this.updateStatus('Analyzing job posting...', 'loading');
        this.showLoadingState();

        try {
            // Use your autonomous workflow endpoint for comprehensive analysis
            const response = await fetch(`${this.apiBaseUrl}/autonomous-workflow`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    resume_text: this.resumeText,
                    job_url: this.currentJobUrl,
                    questions: [
                        "Why are you interested in this position?",
                        "What makes you a good fit for this role?",
                        "What is your greatest strength for this position?"
                    ]
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.matchData = data;
            
            if (data.success) {
                this.displayResults(data);
                this.updateStatus('Analysis complete!', 'success');
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.updateStatus('Analysis failed. Check if backend is running.', 'error');
            this.showErrorState(error.message);
        }
    }

    displayResults(data) {
        // Extract match score from resume scoring results
        const resumeMatchingData = data.execution_results?.resume_and_job_matching;
        const matchScore = resumeMatchingData?.job_matching?.match_score || 0;
        
        // Update score circle
        this.updateScoreCircle(Math.round(matchScore * 100));

        // Display insights
        this.displayInsights(data);
    }

    updateScoreCircle(score) {
        const scoreElement = document.getElementById('score-text');
        const circleElement = document.getElementById('score-circle');
        
        scoreElement.textContent = `${score}%`;
        
        // Color based on score
        let color = '#dc3545'; // red
        if (score >= 70) color = '#28a745'; // green
        else if (score >= 50) color = '#ffc107'; // yellow
        
        circleElement.style.borderColor = color;
        scoreElement.style.color = color;
    }

    displayInsights(data) {
        const insightsContainer = document.getElementById('ai-insights');
        const resumeData = data.execution_results?.resume_and_job_matching;
        
        let insights = [];

        // Resume analysis insights
        if (resumeData?.resume_analysis) {
            const analysis = resumeData.resume_analysis;
            
            if (analysis.skill_gaps && analysis.skill_gaps.length > 0) {
                insights.push({
                    type: 'skill-gap',
                    icon: '📚',
                    text: `Missing skills: ${analysis.skill_gaps.slice(0, 3).join(', ')}`
                });
            }

            if (analysis.opportunities && analysis.opportunities.length > 0) {
                insights.push({
                    type: 'opportunity',
                    icon: '🎯',
                    text: `Opportunities: ${analysis.opportunities.slice(0, 2).join(', ')}`
                });
            }

            if (analysis.recommended_focus) {
                insights.push({
                    type: 'focus',
                    icon: '💡',
                    text: `Focus area: ${analysis.recommended_focus.replace('_', ' ')}`
                });
            }
        }

        // Agent goals
        if (data.agent_goals && data.agent_goals.length > 0) {
            insights.push({
                type: 'goal',
                icon: '🎯',
                text: `AI recommends: ${data.agent_goals[0].replace('_', ' ')}`
            });
        }

        // Job matching insights
        if (resumeData?.job_matching?.insights) {
            resumeData.job_matching.insights.slice(0, 2).forEach(insight => {
                insights.push({
                    type: 'insight',
                    icon: '💼',
                    text: insight
                });
            });
        }

        // Render insights
        if (insights.length > 0) {
            insightsContainer.innerHTML = insights.map(insight => `
                <div class="insight-item ${insight.type}">
                    <span class="insight-icon">${insight.icon}</span>
                    <span class="insight-text">${insight.text}</span>
                </div>
            `).join('');
        } else {
            insightsContainer.innerHTML = `
                <div class="insight-item">
                    <span class="insight-icon">✅</span>
                    <span class="insight-text">Analysis complete - check detailed view</span>
                </div>
            `;
        }
    }

    showLoadingState() {
        const insightsContainer = document.getElementById('ai-insights');
        insightsContainer.innerHTML = `
            <div class="insight-item loading">
                <span class="loading-spinner">⏳</span>
                <span>AI agent analyzing job posting...</span>
            </div>
        `;
    }

    showErrorState(error) {
        const insightsContainer = document.getElementById('ai-insights');
        insightsContainer.innerHTML = `
            <div class="insight-item error">
                <span class="insight-icon">❌</span>
                <span class="insight-text">Analysis failed: ${error}</span>
            </div>
        `;
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('ai-status');
        statusElement.textContent = message;
        statusElement.className = `ai-status ${type}`;
    }

    openResumeUpload() {
        // Create a file input for resume upload
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.txt,.pdf,.doc,.docx';
        input.style.display = 'none';
        
        input.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                this.handleResumeUpload(file);
            }
        });
        
        document.body.appendChild(input);
        input.click();
        document.body.removeChild(input);
    }

    async handleResumeUpload(file) {
        try {
            this.updateStatus('Processing resume...', 'loading');
            
            // For now, handle text files only
            if (file.type === 'text/plain') {
                const text = await file.text();
                this.resumeText = text;
                
                // Save to storage
                await chrome.storage.local.set({ savedResume: text });
                
                this.updateStatus('Resume uploaded successfully!', 'success');
                
                // Auto-analyze after upload
                setTimeout(() => this.analyzeCurrentJob(), 1000);
            } else {
                this.updateStatus('Please upload a .txt file for now', 'warning');
            }
        } catch (error) {
            console.error('Resume upload error:', error);
            this.updateStatus('Resume upload failed', 'error');
        }
    }

    openDetailedView() {
        if (!this.matchData) {
            this.updateStatus('No analysis data available', 'warning');
            return;
        }

        // Open popup with detailed view
        chrome.runtime.sendMessage({
            action: 'openDetailedView',
            data: this.matchData
        });
    }

    observeUrlChanges() {
        let lastUrl = location.href;
        
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                this.currentJobUrl = url;
                
                // Reset and re-analyze for new job posting
                setTimeout(() => {
                    if (this.resumeText) {
                        this.analyzeCurrentJob();
                    }
                }, 2000);
            }
        }).observe(document, { subtree: true, childList: true });
    }
}

// Global instance for message handling
let careerAssistant = null;

// Message listener for popup communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('🤖 Content script received message:', request);
    
    switch (request.action) {
        case 'getAnalysisData':
            sendResponse({ 
                data: careerAssistant?.matchData || null,
                hasResume: !!careerAssistant?.resumeText,
                currentUrl: window.location.href
            });
            break;
            
        case 'triggerAnalysis':
            if (careerAssistant) {
                careerAssistant.analyzeCurrentJob();
                sendResponse({ success: true });
            } else {
                sendResponse({ error: 'Career assistant not initialized' });
            }
            break;
            
        case 'resumeUpdated':
            if (careerAssistant) {
                careerAssistant.resumeText = request.resumeText;
                sendResponse({ success: true });
            }
            break;
            
        case 'focusWidget':
            const widget = document.getElementById('ai-career-assistant');
            if (widget) {
                widget.scrollIntoView({ behavior: 'smooth', block: 'center' });
                widget.style.animation = 'pulse 1s ease-in-out 3';
                sendResponse({ success: true });
            } else {
                sendResponse({ error: 'Widget not found' });
            }
            break;
            
        default:
            sendResponse({ error: 'Unknown action' });
    }
    
    return true; // Keep message channel open
});

// Initialize when page loads
function initializeAssistant() {
    console.log('🤖 Initializing AI Career Assistant on:', window.location.href);
    careerAssistant = new AICareerAssistant();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAssistant);
} else {
    initializeAssistant();
}
