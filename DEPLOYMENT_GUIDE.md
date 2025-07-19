# 🚀 Code of Law AI - Streamlit Deployment Guide

Complete guide for deploying the Code of Law AI Streamlit chatbot to your website.

## 📋 Overview

The Code of Law AI is now available as an interactive Streamlit chatbot that can be deployed to various hosting platforms and integrated into your website at sunnykotwal.com.

### ✨ Features
- 💬 **Interactive Chat Interface** - Real-time conversation with AI legal advisor
- 🎯 **Complexity Routing** - Automatic question complexity detection and routing
- 📊 **Session Statistics** - Track conversation stats and question complexity
- 💡 **Example Questions** - Pre-built examples for each complexity tier
- 🎨 **Custom Styling** - Professional legal theme with responsive design
- 📱 **Mobile Friendly** - Works seamlessly on desktop, tablet, and mobile

## 🏗️ Deployment Options

### Option 1: Railway (Recommended)
Railway provides easy deployment with automatic HTTPS and custom domains.

#### Steps:
1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your GitHub account
3. **Create New Project**: 
   - Click "Deploy from GitHub repo"
   - Select your Law-Ai-Advisor repository
4. **Configure Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=law-ai-advisor-production
   ```
5. **Deploy**: Railway will automatically build and deploy
6. **Custom Domain**: Add `legal.sunnykotwal.com` in Railway dashboard

### Option 2: Streamlit Cloud (Free)
Streamlit's official hosting platform with GitHub integration.

#### Steps:
1. **Create Account**: Go to [share.streamlit.io](https://share.streamlit.io)
2. **Connect GitHub**: Link your repository
3. **Deploy App**:
   - Repository: `kotsun32/Law-Ai-Advisor-`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. **Add Secrets**: In Streamlit Cloud dashboard, add:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   LANGCHAIN_API_KEY = "your_langchain_api_key_here"
   TAVILY_API_KEY = "your_tavily_api_key_here"
   ```

### Option 3: Heroku
Popular platform with good Python support.

#### Steps:
1. **Install Heroku CLI**: `npm install -g heroku`
2. **Login**: `heroku login`
3. **Create App**: `heroku create law-ai-advisor-sunny`
4. **Set Environment Variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key_here
   heroku config:set LANGCHAIN_API_KEY=your_key_here
   heroku config:set TAVILY_API_KEY=your_key_here
   ```
5. **Create Procfile**:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
6. **Deploy**: `git push heroku main`

### Option 4: Docker Deployment
For custom hosting or VPS deployment.

#### Steps:
1. **Build Image**:
   ```bash
   docker build -f Dockerfile.streamlit -t law-ai-advisor .
   ```
2. **Run Container**:
   ```bash
   docker run -p 8501:8501 \
     -e OPENAI_API_KEY=your_key_here \
     -e LANGCHAIN_API_KEY=your_key_here \
     -e TAVILY_API_KEY=your_key_here \
     law-ai-advisor
   ```
3. **Or use Docker Compose**:
   ```bash
   docker-compose -f docker-compose.streamlit.yml up
   ```

## 🌐 Integration with sunnykotwal.com

### Method 1: Subdomain (Recommended)
Create a subdomain that points to your deployed Streamlit app.

1. **DNS Configuration**:
   - Add CNAME record: `legal.sunnykotwal.com` → `your-app.railway.app`
   - Or A record pointing to your server IP

2. **Update Website**:
   Add a prominent link on sunnykotwal.com:
   ```html
   <a href="https://legal.sunnykotwal.com" class="btn btn-primary">
     ⚖️ Try Law AI Advisor
   </a>
   ```

### Method 2: Iframe Embed
Embed the Streamlit app directly in your website.

```html
<!-- Add to your website -->
<div style="height: 800px; width: 100%;">
  <iframe 
    src="https://your-app.railway.app/?embed=true" 
    width="100%" 
    height="100%" 
    frameborder="0">
  </iframe>
</div>
```

### Method 3: Redirect from Existing Page
Update your website to redirect to the chatbot.

```html
<!-- Add to your projects section -->
<div class="project-card">
  <h3>Law AI Advisor</h3>
  <p>Interactive AI chatbot for legal advice with adaptive complexity routing.</p>
  <div class="project-links">
    <a href="https://legal.sunnykotwal.com" class="project-link">Try the Chatbot</a>
    <a href="https://github.com/kotsun32/Law-Ai-Advisor-" class="project-link">View Code</a>
  </div>
</div>
```

## 🔧 Local Development & Testing

### Quick Start
```bash
# 1. Navigate to project
cd Law-Ai-Advisor-

# 2. Activate environment
source venv/bin/activate

# 3. Install Streamlit dependencies
pip install -r requirements_streamlit.txt

# 4. Run Streamlit app
streamlit run streamlit_app.py
```

### Local URL
- **Main App**: http://localhost:8501
- **Admin Page**: http://localhost:8501/_stcore/health

### Testing Checklist
- [ ] App loads without errors
- [ ] Chat interface responds to questions
- [ ] Complexity routing works (Simple/Moderate/Complex)
- [ ] Example questions work
- [ ] Statistics update correctly
- [ ] Mobile responsive design

## 📊 Monitoring & Analytics

### Streamlit Analytics
- **Built-in Metrics**: User sessions, page views
- **Custom Tracking**: Question complexity, response times
- **Error Monitoring**: Failed questions, API errors

### LangChain Tracing
Enable LangSmith for detailed AI pipeline monitoring:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=law-ai-advisor-production
```

## 🛡️ Security & Configuration

### Environment Variables
Never commit API keys to Git. Use platform-specific secret management:

- **Railway**: Environment Variables tab
- **Streamlit Cloud**: Secrets management
- **Heroku**: Config Vars
- **Docker**: Environment files

### Rate Limiting
Consider implementing rate limiting for production:
```python
# Add to streamlit_app.py
import streamlit as st
from datetime import datetime, timedelta

def check_rate_limit():
    if 'last_request' not in st.session_state:
        st.session_state.last_request = datetime.now()
        return True
    
    if datetime.now() - st.session_state.last_request < timedelta(seconds=5):
        return False
    
    st.session_state.last_request = datetime.now()
    return True
```

## 🎨 Customization Options

### Branding
Update the app to match your website:

1. **Colors**: Edit `.streamlit/config.toml`
2. **Logo**: Add your logo to the header
3. **Domain**: Use custom domain matching your brand

### Content
- **Legal Disclaimer**: Update for your jurisdiction
- **Example Questions**: Add domain-specific examples
- **Welcome Message**: Customize for your audience

## 🔗 URL Structure

After deployment, your URLs will be:
- **Main Chatbot**: `https://legal.sunnykotwal.com/`
- **Health Check**: `https://legal.sunnykotwal.com/_stcore/health`
- **Embed Mode**: `https://legal.sunnykotwal.com/?embed=true`

## 📈 Performance Optimization

### Caching
Streamlit includes built-in caching for better performance:
```python
@st.cache_data
def load_vector_store():
    return FAISS.load_local("faiss_index", embeddings)
```

### Resource Management
- **Memory**: Monitor vector store memory usage
- **API Calls**: Track OpenAI API usage and costs
- **Response Time**: Optimize for sub-5-second responses

## 🚨 Troubleshooting

### Common Issues

1. **"Pipeline not initialized"**
   - Check API keys are set correctly
   - Verify FAISS index exists
   - Check internet connectivity

2. **Slow responses**
   - Monitor OpenAI API latency
   - Check vector store size
   - Verify server resources

3. **Chat history not working**
   - Clear browser cache
   - Check session state
   - Restart Streamlit app

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support & Maintenance

### Regular Updates
- **Dependencies**: Update LangChain monthly
- **Vector Store**: Refresh legal documents quarterly
- **API Keys**: Rotate keys annually

### Monitoring
- **Uptime**: Use platform monitoring tools
- **Errors**: Set up alerting for failures
- **Usage**: Track user engagement metrics

---

## 🎯 Next Steps

1. **Choose deployment platform** (Railway recommended)
2. **Set up environment variables** with your API keys
3. **Deploy the application**
4. **Configure custom domain** (legal.sunnykotwal.com)
5. **Update your website** with links to the chatbot
6. **Test thoroughly** before going live
7. **Monitor performance** and user feedback

Your Law AI Advisor chatbot will be live and ready to help users with legal questions! 🚀⚖️