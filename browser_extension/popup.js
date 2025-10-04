// AI Career Assistant - Popup Script
class CareerAssistantPopup {
    constructor() {
        this.currentData = null;
        this.apiBaseUrl = 'http://127.0.0.1:8000';
        this.init();
    }

    async init() {
        // Load any stored analysis data
        await this.loadStoredData();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Check if we have current tab data
        await this.getCurrentTabData();
    }

    async loadStoredData() {
        try {
            const result = await chrome.storage.local.get(['lastAnalysis']);
            if (result.lastAnalysis) {
                this.currentData = result.lastAnalysis;
                this.displayData();
            } else {
                this.showNoDataState();
            }
        } catch (error) {
            console.error('Error loading stored data:', error);
            this.showNoDataState();
        }
    }

    async getCurrentTabData() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Try to get analysis data from content script
            const response = await chrome.tabs.sendMessage(tab.id, { 
                action: 'getAnalysisData' 
            });
            
            if (response && response.data) {
                this.currentData = response.data;
                this.displayData();
            }
        } catch (error) {
            // Content script might not be loaded or no data available
            console.log('No current analysis data available');
        }
    }

    attachEventListeners() {
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.triggerAnalysis();
        });

        document.getElementById('uploadResumeBtn').addEventListener('click', () => {
            this.openResumeUpload();
        });

        document.getElementById('viewOnPageBtn').addEventListener('click', () => {
            this.focusOnPageWidget();
        });
    }

    displayData() {
        if (!this.currentData) {
            this.showNoDataState();
            return;
        }

        const data = this.currentData;
        
        // Hide loading state
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';

        // Display match score
        this.displayMatchScore(data);
        
        // Display insights
        this.displayInsights(data);
        
        // Display agent goals
        this.displayAgentGoals(data);
        
        // Display tailored answers if available
        this.displayTailoredAnswers(data);

        this.updateStatus('Analysis data loaded', 'success');
    }

    displayMatchScore(data) {
        const resumeMatchingData = data.execution_results?.resume_and_job_matching;
        const matchScore = resumeMatchingData?.job_matching?.match_score || 0;
        
        const scoreElement = document.getElementById('matchScore');
        const score = Math.round(matchScore * 100);
        
        scoreElement.textContent = `${score}%`;
        
        // Style based on score
        if (score >= 70) {
            scoreElement.style.color = '#28a745';
        } else if (score >= 50) {
            scoreElement.style.color = '#ffc107';
        } else {
            scoreElement.style.color = '#dc3545';
        }
    }

    displayInsights(data) {
        const insightsList = document.getElementById('insightsList');
        const resumeData = data.execution_results?.resume_and_job_matching;
        
        let insights = [];

        // Resume analysis insights
        if (resumeData?.resume_analysis) {
            const analysis = resumeData.resume_analysis;
            
            if (analysis.skill_gaps && analysis.skill_gaps.length > 0) {
                insights.push({
                    icon: '📚',
                    text: `Skills to develop: ${analysis.skill_gaps.slice(0, 4).join(', ')}`
                });
            }

            if (analysis.opportunities && analysis.opportunities.length > 0) {
                insights.push({
                    icon: '🎯',
                    text: `Your strengths: ${analysis.opportunities.slice(0, 3).join(', ')}`
                });
            }

            if (analysis.recommended_focus) {
                insights.push({
                    icon: '💡',
                    text: `Recommended focus: ${analysis.recommended_focus.replace('_', ' ')}`
                });
            }
        }

        // Job matching insights
        if (resumeData?.job_matching?.insights) {
            resumeData.job_matching.insights.slice(0, 3).forEach(insight => {
                insights.push({
                    icon: '💼',
                    text: insight
                });
            });
        }

        // Career development insights
        const careerData = data.execution_results?.career_development;
        if (careerData?.progress) {
            const progress = careerData.progress;
            if (progress.next_milestone) {
                insights.push({
                    icon: '🎖️',
                    text: `Next milestone: ${progress.next_milestone.replace('_', ' ')}`
                });
            }
        }

        // Render insights
        if (insights.length > 0) {
            insightsList.innerHTML = insights.map(insight => `
                <li class="insight">
                    <span class="icon">${insight.icon}</span>
                    <span>${insight.text}</span>
                </li>
            `).join('');
        } else {
            insightsList.innerHTML = `
                <li class="insight">
                    <span class="icon">✅</span>
                    <span>No specific insights available</span>
                </li>
            `;
        }
    }

    displayAgentGoals(data) {
        const goalsList = document.getElementById('goalsList');
        const goals = data.agent_goals || [];
        const obstacles = data.identified_obstacles || [];

        let goalItems = [];

        // Display agent goals
        goals.forEach(goal => {
            goalItems.push({
                icon: '🎯',
                text: `Focus on: ${goal.replace('_', ' ')}`
            });
        });

        // Display key obstacles
        if (obstacles.length > 0) {
            goalItems.push({
                icon: '⚠️',
                text: `Obstacles to address: ${obstacles.slice(0, 2).join(', ').replace(/_/g, ' ')}`
            });
        }

        // Agent actions
        if (data.agent_actions && data.agent_actions.length > 0) {
            goalItems.push({
                icon: '🔧',
                text: `AI actions taken: ${data.agent_actions.length} analysis steps completed`
            });
        }

        if (goalItems.length > 0) {
            goalsList.innerHTML = goalItems.map(item => `
                <li class="insight">
                    <span class="icon">${item.icon}</span>
                    <span>${item.text}</span>
                </li>
            `).join('');
        } else {
            document.getElementById('goalsSection').style.display = 'none';
        }
    }

    displayTailoredAnswers(data) {
        const answersSection = document.getElementById('answersSection');
        const answersContainer = document.getElementById('tailoredAnswers');
        
        const tailoredData = data.execution_results?.resume_and_job_matching?.tailored_answers;
        
        if (tailoredData && tailoredData.answers && tailoredData.answers.length > 0) {
            answersSection.style.display = 'block';
            
            answersContainer.innerHTML = tailoredData.answers.map((answer, index) => `
                <div class="answer-item">
                    <div class="question">Q${index + 1}: ${answer.question || `Question ${index + 1}`}</div>
                    <div class="answer">${answer.answer || answer}</div>
                </div>
            `).join('');
        } else {
            answersSection.style.display = 'none';
        }
    }

    showNoDataState() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('mainContent').innerHTML = `
            <div style="text-align: center; padding: 40px; opacity: 0.8;">
                <div style="font-size: 48px; margin-bottom: 16px;">🤖</div>
                <div style="font-size: 14px; margin-bottom: 8px;">No analysis data available</div>
                <div style="font-size: 12px; opacity: 0.7;">Navigate to a job posting and click "Analyze Job" to get started</div>
            </div>
        `;
        document.getElementById('mainContent').style.display = 'block';
    }

    async triggerAnalysis() {
        try {
            this.updateStatus('Triggering analysis...', 'loading');
            
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            console.log('🤖 Popup: Sending analysis request to tab:', tab.url);
            
            // Check if this is a supported job site
            if (!this.isJobPostingUrl(tab.url)) {
                this.updateStatus('Please navigate to a job posting on a supported site', 'warning');
                return;
            }
            
            // Send message to content script to trigger analysis
            const response = await chrome.tabs.sendMessage(tab.id, { 
                action: 'triggerAnalysis' 
            });
            
            console.log('🤖 Popup: Response from content script:', response);
            
            if (response && response.success) {
                this.updateStatus('Analysis started on page', 'success');
                // Close popup to let user see the analysis
                setTimeout(() => window.close(), 1000);
            } else {
                this.updateStatus(response?.error || 'Failed to start analysis', 'error');
            }
            
        } catch (error) {
            console.error('Error triggering analysis:', error);
            
            // More specific error messages
            if (error.message.includes('Could not establish connection')) {
                this.updateStatus('Content script not loaded. Try refreshing the page.', 'error');
            } else if (error.message.includes('No tab with id')) {
                this.updateStatus('Tab not accessible. Please try again.', 'error');
            } else {
                this.updateStatus('Error: Make sure you\'re on a job posting page and refresh if needed', 'error');
            }
        }
    }

    isJobPostingUrl(url) {
        if (!url) return false;
        
        const jobSites = [
            'workday.com',
            'myworkdayjobs.com',
            'indeed.com',
            'linkedin.com/jobs',
            'glassdoor.com',
            'lever.co',
            'greenhouse.io'
        ];

        return jobSites.some(site => url.includes(site));
    }

    openResumeUpload() {
        // Create file input
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.txt,.pdf,.doc,.docx';
        input.style.display = 'none';
        
        input.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                await this.handleResumeUpload(file);
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
                
                // Save to storage
                await chrome.storage.local.set({ savedResume: text });
                
                this.updateStatus('Resume uploaded successfully!', 'success');
                
                // Notify content script about new resume
                try {
                    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                    await chrome.tabs.sendMessage(tab.id, { 
                        action: 'resumeUpdated',
                        resumeText: text
                    });
                } catch (error) {
                    // Content script might not be loaded
                }
            } else {
                this.updateStatus('Please upload a .txt file for now', 'warning');
            }
        } catch (error) {
            console.error('Resume upload error:', error);
            this.updateStatus('Resume upload failed', 'error');
        }
    }

    async focusOnPageWidget() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Focus the browser tab
            await chrome.tabs.update(tab.id, { active: true });
            
            // Send message to content script to highlight widget
            await chrome.tabs.sendMessage(tab.id, { 
                action: 'focusWidget' 
            });
            
            // Close popup
            window.close();
            
        } catch (error) {
            console.error('Error focusing widget:', error);
            this.updateStatus('Unable to focus widget on page', 'error');
        }
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusText');
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
    }
}

// Initialize popup when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    new CareerAssistantPopup();
});
