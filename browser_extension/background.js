// AI Career Assistant - Background Service Worker

class CareerAssistantBackground {
    constructor() {
        this.init();
    }

    init() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            if (details.reason === 'install') {
                this.onInstall();
            } else if (details.reason === 'update') {
                this.onUpdate();
            }
        });

        // Handle messages from content scripts and popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep message channel open for async responses
        });

        // Handle tab updates to refresh analysis on new job pages
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && this.isJobPostingUrl(tab.url)) {
                this.notifyTabUpdate(tabId, tab);
            }
        });
    }

    onInstall() {
        console.log('🤖 AI Career Assistant installed!');
        
        // Set default settings
        chrome.storage.local.set({
            settings: {
                autoAnalyze: true,
                apiEndpoint: 'http://127.0.0.1:8000',
                notifications: true
            },
            firstRun: true
        });

        // Show welcome notification
        this.showNotification(
            'AI Career Assistant Installed!',
            'Navigate to any job posting to get AI-powered resume matching and career insights.'
        );
    }

    onUpdate() {
        console.log('🔄 AI Career Assistant updated!');
        
        this.showNotification(
            'AI Career Assistant Updated!',
            'New features available. Visit any job posting to see the improvements.'
        );
    }

    handleMessage(message, sender, sendResponse) {
        switch (message.action) {
            case 'openDetailedView':
                this.openDetailedView(message.data);
                sendResponse({ success: true });
                break;

            case 'saveAnalysisData':
                this.saveAnalysisData(message.data);
                sendResponse({ success: true });
                break;

            case 'getSettings':
                this.getSettings().then(sendResponse);
                break;

            case 'updateSettings':
                this.updateSettings(message.settings).then(sendResponse);
                break;

            case 'showNotification':
                this.showNotification(message.title, message.body, message.icon);
                sendResponse({ success: true });
                break;

            case 'checkBackendStatus':
                this.checkBackendStatus().then(sendResponse);
                break;

            default:
                sendResponse({ error: 'Unknown action' });
        }
    }

    async openDetailedView(data) {
        try {
            // Create a new tab with detailed analysis
            const tab = await chrome.tabs.create({
                url: chrome.runtime.getURL('detailed.html'),
                active: true
            });

            // Wait for tab to load and send data
            setTimeout(() => {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'displayDetailedData',
                    data: data
                });
            }, 500);

        } catch (error) {
            console.error('Error opening detailed view:', error);
        }
    }

    async saveAnalysisData(data) {
        try {
            await chrome.storage.local.set({
                lastAnalysis: data,
                lastAnalysisTime: Date.now()
            });
            console.log('Analysis data saved');
        } catch (error) {
            console.error('Error saving analysis data:', error);
        }
    }

    async getSettings() {
        try {
            const result = await chrome.storage.local.get(['settings']);
            return result.settings || {
                autoAnalyze: true,
                apiEndpoint: 'http://127.0.0.1:8000',
                notifications: true
            };
        } catch (error) {
            console.error('Error getting settings:', error);
            return { error: error.message };
        }
    }

    async updateSettings(newSettings) {
        try {
            const currentSettings = await this.getSettings();
            const updatedSettings = { ...currentSettings, ...newSettings };
            
            await chrome.storage.local.set({ settings: updatedSettings });
            return { success: true, settings: updatedSettings };
        } catch (error) {
            console.error('Error updating settings:', error);
            return { error: error.message };
        }
    }

    async checkBackendStatus() {
        try {
            const settings = await this.getSettings();
            const apiUrl = settings.apiEndpoint || 'http://127.0.0.1:8000';
            
            const response = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });

            if (response.ok) {
                const data = await response.json();
                return { 
                    status: 'online', 
                    service: data.service,
                    timestamp: data.timestamp 
                };
            } else {
                return { status: 'error', message: 'Backend responded with error' };
            }

        } catch (error) {
            return { 
                status: 'offline', 
                message: 'Backend not reachable. Make sure your FastAPI server is running.' 
            };
        }
    }

    notifyTabUpdate(tabId, tab) {
        // Send message to content script that tab updated
        setTimeout(() => {
            chrome.tabs.sendMessage(tabId, {
                action: 'tabUpdated',
                url: tab.url
            }).catch(() => {
                // Content script might not be loaded yet
            });
        }, 1000);
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

    showNotification(title, body, icon = null) {
        const notificationOptions = {
            type: 'basic',
            title: title,
            message: body,
            priority: 1
        };
        
        if (icon) {
            notificationOptions.iconUrl = icon;
        }
        
        chrome.notifications.create(notificationOptions);
    }

    // Periodic cleanup of old data
    async cleanupOldData() {
        try {
            const result = await chrome.storage.local.get(['lastAnalysisTime']);
            const lastTime = result.lastAnalysisTime;
            const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);

            if (lastTime && lastTime < oneDayAgo) {
                await chrome.storage.local.remove(['lastAnalysis']);
                console.log('Cleaned up old analysis data');
            }
        } catch (error) {
            console.error('Error during cleanup:', error);
        }
    }
}

// Initialize background service
new CareerAssistantBackground();

// Run cleanup every hour
setInterval(() => {
    new CareerAssistantBackground().cleanupOldData();
}, 60 * 60 * 1000);
