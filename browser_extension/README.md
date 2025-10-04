# 🤖 AI Career Assistant - Browser Extension

Transform your job search with AI-powered resume matching and career insights, powered by your FastAPI backend!

## ✨ Features

### 🎯 **Smart Resume Matching**
- Real-time compatibility scoring against job postings
- AI-powered analysis using your autonomous career agent
- Much more than keyword matching - semantic understanding

### 🧠 **AI Career Insights**
- Autonomous goal identification and strategy recommendations
- Skill gap analysis and improvement suggestions
- Career trajectory tracking and milestone planning
- Personalized networking and development recommendations

### ✍️ **Tailored Answer Generation**
- AI-generated responses to common application questions
- Contextual answers based on your resume and the specific job
- Professional, personalized content that stands out

### 🔄 **Seamless Integration**
- Works on major job sites (Workday, Indeed, LinkedIn, Glassdoor, etc.)
- Connects directly to your FastAPI backend
- Persistent resume storage and analysis history

## 🚀 Installation

### Prerequisites
1. **Your FastAPI backend must be running**
   ```bash
   cd JobAssistantAgent
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Chrome Browser** (Firefox support coming soon)

### Install the Extension

#### Method 1: Developer Mode (Recommended)
1. **Open Chrome Extensions**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (top right toggle)

2. **Load Extension**
   - Click "Load unpacked"
   - Select the `browser_extension` folder
   - The AI Career Assistant icon should appear in your toolbar

#### Method 2: Package and Install
```bash
# Zip the extension folder
cd browser_extension
zip -r ai-career-assistant.zip .
# Then load the zip file in Chrome extensions
```

## 🎮 How to Use

### 1. **First Setup**
- Click the extension icon in your toolbar
- Upload your resume (currently supports .txt files)
- Your resume is stored locally and securely

### 2. **Job Analysis**
- Navigate to any job posting on supported sites
- The AI widget automatically appears on the right side
- Click "Analyze Job" for instant AI insights

### 3. **View Results**
- **Match Score**: See your compatibility percentage
- **AI Insights**: Get skill gaps, opportunities, and focus areas
- **Smart Recommendations**: Autonomous AI suggestions for career growth
- **Tailored Answers**: Pre-written responses to common questions

### 4. **Detailed Analysis**
- Click "View Details" for comprehensive insights
- Access the full autonomous agent analysis
- See career development recommendations and progress tracking

## 🔧 Configuration

### Backend Connection
The extension connects to your FastAPI backend at `http://127.0.0.1:8000` by default.

**To change the backend URL:**
1. Open extension popup
2. Go to settings (gear icon)
3. Update the API endpoint
4. Save changes

### Supported Job Sites
- ✅ Workday (workday.com, myworkdayjobs.com)
- ✅ Indeed (indeed.com)
- ✅ LinkedIn Jobs (linkedin.com/jobs)
- ✅ Glassdoor (glassdoor.com)
- ✅ Lever (lever.co)
- ✅ Greenhouse (greenhouse.io)

## 🧩 Extension Components

### Content Script (`content.js`)
- Injected into job posting pages
- Creates the floating AI widget
- Handles real-time analysis and UI updates

### Popup Interface (`popup.html`)
- Detailed view of analysis results
- Resume upload and management
- Settings and configuration

### Background Service (`background.js`)
- Manages data storage and sync
- Handles cross-tab communication
- Background analysis and notifications

## 🎨 What Makes This Different

### vs. Traditional Keyword Matchers
- **Semantic Understanding**: AI analyzes meaning, not just keywords
- **Autonomous Decision Making**: Agent identifies goals and strategies
- **Continuous Learning**: Improves recommendations over time
- **Comprehensive Analysis**: Resume, career trajectory, and market fit

### vs. Basic Resume Checkers
- **Real-time Integration**: Works directly on job posting pages
- **AI-Powered Insights**: Uses advanced LLMs for deep analysis
- **Career Guidance**: Beyond resume - full career development
- **Tailored Content**: Generates specific application materials

## 🔒 Privacy & Security

- **Local Storage**: Your resume is stored locally in your browser
- **Secure Communication**: HTTPS connections to your backend
- **No Data Sharing**: Analysis happens on your own infrastructure
- **Transparent Processing**: Open source - see exactly how it works

## 🛠 Development

### File Structure
```
browser_extension/
├── manifest.json          # Extension configuration
├── content.js             # Main widget logic
├── popup.html/popup.js    # Extension popup
├── background.js          # Service worker
├── styles.css             # Widget styling
└── icons/                 # Extension icons
```

### API Integration
The extension uses these endpoints from your FastAPI backend:

- `POST /autonomous-workflow` - Main AI analysis
- `POST /score` - Resume scoring
- `POST /tailored-answers` - Answer generation
- `GET /health` - Backend status check

### Customization
- **Styling**: Edit `styles.css` for custom appearance
- **Job Sites**: Add new sites in `manifest.json` and `content.js`
- **Features**: Extend functionality by modifying the content script

## 🐛 Troubleshooting

### Common Issues

**Extension not appearing on job pages:**
- Check if the site is in the supported list
- Refresh the page after installing
- Ensure developer mode is enabled

**"Analysis failed" errors:**
- Verify FastAPI backend is running on port 8000
- Check browser console for network errors
- Confirm backend endpoints are accessible

**Resume upload not working:**
- Currently only .txt files are supported
- Ensure file is plain text format
- Check browser permissions for file access

**No analysis data in popup:**
- Make sure you've run analysis on a job page first
- Check if data is stored (browser developer tools > Application > Storage)

### Debug Mode
1. Open Chrome Developer Tools
2. Go to Console tab
3. Look for messages starting with "🤖"
4. Check Network tab for API call status

## 🔄 Updates & Roadmap

### Current Version: 1.0.0
- ✅ Real-time job analysis
- ✅ AI-powered insights
- ✅ Resume scoring
- ✅ Tailored answer generation

### Coming Soon
- 📄 PDF resume support
- 🔔 Analysis notifications
- 📊 Career progress tracking
- 🌐 More job site support
- 📱 Mobile browser support

## 🤝 Contributing

Want to improve the extension?

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Areas for Contribution
- Additional job site support
- UI/UX improvements
- Performance optimizations
- New AI features
- Bug fixes and testing

## 📞 Support

**Issues with the extension?**
1. Check this README for troubleshooting
2. Review browser console for errors
3. Verify backend connectivity
4. Open an issue with details

**Need help with the FastAPI backend?**
- Refer to the main project documentation
- Check API endpoint documentation at `/docs`
- Ensure all dependencies are installed

---

**🚀 Transform your job search with AI-powered insights!**

Your autonomous career agent is now available wherever you browse for jobs. Get instant, intelligent feedback on every opportunity and accelerate your career growth with personalized AI guidance.

