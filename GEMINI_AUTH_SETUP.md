# Gemini Authentication Setup Guide

This guide will help you set up Google Account authentication for the Gemini Bridge tool.

## Overview

The Gemini Bridge now uses **Application Default Credentials (ADC)** exclusively, which means you sign in with your Google account instead of using API keys. This is more secure and easier to manage.

## Prerequisites

1. **Google Cloud SDK (gcloud CLI)** - Required for authentication
2. **Python packages** - `google-auth` and `google-generativeai`

## Step-by-Step Setup

### 1. Install Google Cloud SDK

If you don't have gcloud installed:

**Windows:**
- Download from: https://cloud.google.com/sdk/docs/install
- Run the installer
- Restart your terminal after installation

**Linux/Mac:**
```bash
# Quick install script
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Verify installation:**
```bash
gcloud --version
```

### 2. Install Required Python Packages

```bash
pip install google-auth google-auth-oauthlib google-generativeai
```

### 3. Authenticate with Your Google Account

This is the key step that replaces API keys:

```bash
gcloud auth application-default login
```

**What happens:**
1. A browser window will open
2. Sign in with your Google account
3. Grant the necessary permissions
4. The credentials are saved locally on your computer

**Important Notes:**
- You only need to do this once
- Your credentials are stored securely in:
  - **Windows:** `%APPDATA%\gcloud\application_default_credentials.json`
  - **Linux/Mac:** `~/.config/gcloud/application_default_credentials.json`
- No API keys needed!

### 4. Test Your Setup

```bash
# Quick test
python tools/gemini_bridge.py "Hello, are you working?"

# Or use the --setup flag for help
python tools/gemini_bridge.py --setup
```

## Troubleshooting

### Problem: "Failed to load Application Default Credentials"

**Solution:** You need to authenticate first:
```bash
gcloud auth application-default login
```

### Problem: Persistent authentication errors

**Solution:** Revoke and re-authenticate:
```bash
# Step 1: Revoke existing credentials
gcloud auth application-default revoke

# Step 2: Re-authenticate
gcloud auth application-default login
```

### Problem: "google-auth library is required"

**Solution:** Install the required package:
```bash
pip install google-auth google-auth-oauthlib
```

### Problem: Multiple Google accounts

If you have multiple Google accounts and want to switch:

```bash
# Revoke current auth
gcloud auth application-default revoke

# Login with different account
gcloud auth application-default login
```

### Problem: Check current authentication status

```bash
# Check if you're authenticated
gcloud auth application-default print-access-token

# If this prints a token, you're authenticated
# If it fails, you need to run: gcloud auth application-default login
```

## Advanced Usage

### Use a Different Model

```bash
python tools/gemini_bridge.py --model gemini-1.5-pro "Your prompt here"
```

### Get Setup Help

```bash
python tools/gemini_bridge.py --setup
```

## Security Notes

- **No API keys stored in code or config files** ✓
- **Credentials stored securely by Google Cloud SDK** ✓
- **Uses OAuth 2.0 for authentication** ✓
- **Easy to revoke access if needed** ✓

## Migration from API Keys

If you were previously using API keys:

1. **Remove API keys** from environment variables:
   - Delete `GOOGLE_API_KEY` from your environment
   - Remove API keys from `.env` files

2. **Authenticate with your account:**
   ```bash
   gcloud auth application-default login
   ```

3. **That's it!** The tool will now use your Google account credentials

## FAQ

**Q: Do I need a Google Cloud project?**
A: Yes, but it can be any project. The authentication is tied to your Google account.

**Q: Will this cost me money?**
A: Gemini API usage may have costs depending on your usage tier. Check Google AI Studio for pricing.

**Q: Can I use this on multiple computers?**
A: Yes, just run `gcloud auth application-default login` on each computer.

**Q: How do I know if I'm authenticated?**
A: Run: `gcloud auth application-default print-access-token`
If it prints a token, you're authenticated.

**Q: Does this expire?**
A: Yes, credentials expire periodically. If you get auth errors, just re-run:
```bash
gcloud auth application-default login
```

## Getting Help

If you encounter issues:

1. Check authentication status:
   ```bash
   gcloud auth application-default print-access-token
   ```

2. View detailed setup instructions:
   ```bash
   python tools/gemini_bridge.py --setup
   ```

3. Try re-authenticating:
   ```bash
   gcloud auth application-default revoke
   gcloud auth application-default login
   ```

## Summary

✓ **No more API keys to manage**  
✓ **Secure OAuth 2.0 authentication**  
✓ **Easy to set up and revoke**  
✓ **One command: `gcloud auth application-default login`**  

You're now ready to use the Gemini Bridge with your Google account!
