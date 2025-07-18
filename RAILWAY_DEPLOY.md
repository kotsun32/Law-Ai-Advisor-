# 🚅 Railway Deployment Guide for Law AI Advisor

Quick guide to deploy your Streamlit chatbot to Railway with custom domain.

## 🚀 Step-by-Step Deployment

### 1. Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub account
- Verify your email

### 2. Deploy from GitHub
1. Click **"Deploy from GitHub repo"**
2. Select **`kotsun32/Law-Ai-Advisor-`** repository
3. Railway will automatically detect the project

### 3. Configure Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=law-ai-advisor-production
```

**Note**: Use your actual API keys from your `.env` file, not the placeholders above.

### 4. Configure Build Settings
Railway should auto-detect from `railway.json`, but verify:
- **Build Command**: `pip install -r requirements_streamlit.txt`
- **Start Command**: `./start.sh` (handles PORT environment variable properly)

### 5. Deploy
- Click **"Deploy"**
- Wait for build to complete (~3-5 minutes)
- You'll get a Railway URL like: `law-ai-advisor-production.up.railway.app`

### 6. Custom Domain Setup

#### Option A: Using Railway's Custom Domain
1. In Railway dashboard, go to **Settings** > **Domains**
2. Click **"Custom Domain"**
3. Enter: `legal.sunnykotwal.com`
4. Railway will provide DNS instructions

#### Option B: Manual DNS Configuration
1. Go to your domain registrar (where you bought sunnykotwal.com)
2. Add CNAME record:
   - **Name**: `legal`
   - **Value**: `law-ai-advisor-production.up.railway.app`
   - **TTL**: 300 (5 minutes)

### 7. SSL Certificate
Railway automatically provides SSL certificates for custom domains.

## 🔧 Troubleshooting

### Build Fails
- Check that `requirements_streamlit.txt` exists
- Verify environment variables are set
- Check Railway build logs for specific errors

### App Won't Start
- Ensure `streamlit_app.py` and `start.sh` exist in root directory
- Check that `start.sh` is executable (handled by Dockerfile)
- Verify PORT environment variable is being passed correctly
- Check that OPENAI_API_KEY is valid

### PORT Environment Variable Error
If you see "Invalid value for '--server.port': '$PORT' is not a valid integer":
- Ensure you're using the updated `start.sh` script
- Verify Railway configuration uses `./start.sh` as start command
- Check that `start.sh` is copied and made executable in Dockerfile

### Domain Issues
- DNS changes can take up to 24 hours to propagate
- Use [DNS Checker](https://dnschecker.org/) to verify propagation
- Ensure CNAME points to correct Railway URL

## 📊 Monitoring

### Railway Dashboard
- **Deployments**: View build history and logs
- **Metrics**: CPU, memory, and network usage
- **Logs**: Real-time application logs

### Expected Performance
- **Cold Start**: ~10-15 seconds
- **Response Time**: 3-8 seconds per query
- **Memory Usage**: ~200-500MB
- **Concurrent Users**: 10-50 (free tier)

## 💰 Pricing

### Railway Free Tier
- $5/month in free credits
- Enough for moderate usage
- Automatic scaling

### Upgrading
- If you exceed free credits, Railway will prompt to upgrade
- Pro plan: $20/month for higher limits

## ✅ Verification

Once deployed, test these URLs:
- **Main App**: `https://legal.sunnykotwal.com/`
- **Health Check**: `https://legal.sunnykotwal.com/_stcore/health`

## 🚨 Important Notes

1. **Environment Variables**: Never commit API keys to GitHub
2. **Domain Propagation**: Can take up to 24 hours
3. **SSL**: Automatically handled by Railway
4. **Updates**: Push to GitHub triggers auto-deployment

## 🎯 Next Steps

1. Deploy to Railway using this guide
2. Wait for DNS propagation
3. Test the chatbot at `legal.sunnykotwal.com`
4. Share with users and collect feedback!

Your Law AI Advisor will be live and accessible from your website! 🚀⚖️