# 🔐 Private Repository Deployment Guide for Streamlit Cloud

## Current Repository: datavineo/ElectraLens (Private)

### Step 1: Deploy on Streamlit Community Cloud

1. **Visit**: https://share.streamlit.io/
2. **Sign in** with your GitHub account (`datavineo`)
3. **Grant Repository Access**:
   - Click "New app"
   - If `ElectraLens` doesn't appear in the dropdown:
     - Click "Add repository" or "Configure repository access"
     - Grant Streamlit access to `datavineo/ElectraLens`
     - Refresh the page

4. **Configure App Settings**:
   ```
   Repository: datavineo/ElectraLens
   Branch: main
   Main file path: streamlit_app.py
   App URL: electralens-dashboard (or choose your preferred subdomain)
   ```

### Step 2: Configure Environment Variables

In the "Advanced settings" section, add these environment variables:

```toml
# Required Environment Variables
API_BASE = "https://your-actual-vercel-url.vercel.app"

# Optional (if you have authentication setup)
SECRET_KEY = "your-secret-key-here"
```

**🔥 IMPORTANT**: Replace `https://your-actual-vercel-url.vercel.app` with your actual Vercel deployment URL.

### Step 3: Find Your Vercel URL

To find your actual Vercel deployment URL:

1. **Option A**: Check Vercel Dashboard
   - Go to https://vercel.com/dashboard
   - Look for your `ElectraLens` or API project
   - Copy the deployment URL

2. **Option B**: Test API endpoints
   - Your API should be accessible at: `https://[project-name].vercel.app`
   - Common patterns:
     - `https://electra-lens.vercel.app`
     - `https://electralens.vercel.app`
     - `https://electra-lens-[hash].vercel.app`

### Step 4: Test Your API Connection

Once you have the URL, test it:

```bash
# Test if your API is working
curl https://your-vercel-url.vercel.app/health
curl https://your-vercel-url.vercel.app/voters/summary
```

### Step 5: Update Streamlit App (if needed)

If you need to change the default API URL, update line 16 in `streamlit_app.py`:

```python
API_BASE = os.getenv('API_BASE', 'https://your-actual-vercel-url.vercel.app')
```

### Step 6: Deploy

1. Click "Deploy!" in Streamlit Cloud
2. Wait for the build to complete (usually 3-5 minutes)
3. Your app will be available at: `https://your-app-name.streamlit.app`

---

## Troubleshooting Private Repository Issues

### Issue: Repository Not Visible
**Solution**: 
- Ensure you're signed into GitHub with the `datavineo` account
- Grant Streamlit access to private repositories in GitHub settings
- Go to GitHub → Settings → Applications → Streamlit → Configure

### Issue: Build Fails
**Solution**:
- Check the build logs in Streamlit Cloud
- Verify `requirements-streamlit.txt` has all dependencies
- Ensure no syntax errors in `streamlit_app.py`

### Issue: API Connection Failed
**Solution**:
- Verify your Vercel API is working by visiting the URL directly
- Check the `API_BASE` environment variable in Streamlit Cloud
- Ensure CORS is properly configured in your FastAPI backend

---

## Alternative: Manual Repository Access

If Streamlit Cloud can't access your private repo automatically:

1. **Fork to Public** (temporary):
   - Create a public fork of your private repo
   - Deploy from the public fork
   - Delete the public fork after deployment

2. **Use GitHub Deploy Keys**:
   - Generate an SSH deploy key
   - Add it to your repository settings
   - Configure in Streamlit Cloud advanced settings

---

## Next Steps After Deployment

1. **Test all features**:
   - ✅ Login functionality
   - ✅ PDF upload
   - ✅ Voter management
   - ✅ Charts and analytics

2. **Monitor performance**:
   - Check app performance in Streamlit Cloud dashboard
   - Monitor API response times

3. **Share your app**:
   - Your Streamlit app URL: `https://[your-app-name].streamlit.app`
   - Share with team members or stakeholders

---

## Support

If you encounter issues:
- Check Streamlit Community Forum: https://discuss.streamlit.io/
- Review build logs in Streamlit Cloud dashboard
- Verify GitHub repository permissions