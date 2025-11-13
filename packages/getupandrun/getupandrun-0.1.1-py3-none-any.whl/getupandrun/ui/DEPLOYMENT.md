# Vercel Deployment Guide

This guide explains how to set up automatic deployments to Vercel when pushing to the `main` branch.

## Automatic Deployment Setup

Vercel automatically deploys when you connect a Git repository. Here's how to set it up:

### Step 1: Connect Your Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. Select your repository (GitHub, GitLab, or Bitbucket)
5. Authorize Vercel to access your repository if prompted

### Step 2: Configure Project Settings

**IMPORTANT**: Set the following in the project configuration:

- **Root Directory**: Set to `ui/` (not the repo root!)
  - Click "Edit" next to Root Directory
  - Enter: `ui`
  - This tells Vercel where your Next.js app is located

- **Framework Preset**: Next.js (should auto-detect)

- **Build Command**: `npm run build` (already in `vercel.json`)

- **Output Directory**: `.next` (default for Next.js)

### Step 3: Set Environment Variables

Go to **Project Settings** → **Environment Variables** and add:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
  - Add for: Production, Preview, and Development
  - Mark as sensitive

- `PYTHON_PATH`: Optional, defaults to `python3`
  - Only needed if you want to override the Python path

- `GETUPANDRUN_CLI_PATH`: Optional, defaults to `python3 -m getupandrun.cli.main`
  - Only needed if you want to override the CLI command

### Step 4: Deploy

Click **"Deploy"** and Vercel will:
1. Install Node.js dependencies
2. Run the Python installation script
3. Build the Next.js application
4. Deploy to production

## Automatic Deployments

Once connected, Vercel will **automatically deploy**:

- **Production**: Every push to `main` branch
- **Preview**: Every push to other branches (creates preview deployments)
- **Pull Requests**: Creates preview deployments for PRs

### Deployment Triggers

- ✅ Push to `main` → Production deployment
- ✅ Push to other branches → Preview deployment
- ✅ Open/update Pull Request → Preview deployment
- ✅ Merge PR to `main` → Production deployment

## Manual Deployment

You can also deploy manually:

1. **Via Vercel Dashboard**: Click "Redeploy" on any deployment
2. **Via Vercel CLI**:
   ```bash
   cd ui
   vercel --prod
   ```

## Configuration Files

### `vercel.json`

The `vercel.json` file in the `ui/` directory configures:
- Build and install commands
- Function runtime settings
- Git deployment settings

### Root Directory Setting

**CRITICAL**: The Root Directory must be set to `ui/` in Vercel Dashboard:
- Go to Project Settings → General
- Under "Root Directory", set it to `ui`
- This ensures Vercel looks in the correct directory for your Next.js app

## Troubleshooting

### Build Fails

1. **Check Root Directory**: Must be set to `ui/`
2. **Check Build Logs**: View detailed logs in Vercel Dashboard
3. **Python Installation**: The build script may fail if Python isn't available
   - Check build logs for Python installation errors
   - Python may not be available in Vercel's build environment

### Runtime Errors

1. **Check Function Logs**: View logs in Vercel Dashboard → Functions
2. **Check Environment Variables**: Ensure `OPENAI_API_KEY` is set
3. **Python Not Available**: If Python isn't available at runtime, you may need:
   - A different deployment strategy
   - A separate API service with Python
   - Vercel's Python runtime (if available)

### Settings Not Saving

- On Vercel, settings are stored in browser `localStorage`
- This is expected behavior - the deployed version cannot access your local filesystem

## Monitoring Deployments

- **Dashboard**: View all deployments at `vercel.com/dashboard`
- **Status**: Each deployment shows build status, logs, and URL
- **Notifications**: Get notified of deployment status via email/Slack

## Next Steps

After deployment:
1. Your app will be available at `https://your-project.vercel.app`
2. Check the deployment logs to ensure Python installation succeeded
3. Test project creation to verify everything works
4. Monitor function logs for any runtime errors

