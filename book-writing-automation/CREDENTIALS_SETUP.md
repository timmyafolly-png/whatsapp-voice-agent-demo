# Credentials Setup Guide for Make.com Workflow

Before you can run the "Attention is Currency" workflow, you must authenticate all API connections in Make.com. This guide walks you through each one.

## Why This Matters

Think of Make.com as the conductor of an orchestra. The conductor needs written permission from each musician to direct them. Without these credentials authenticated, the workflow will fail as soon as it tries to access any service.

**In plain terms:** Every time a module tries to fetch from Google Sheets, call ChatGPT, or send an email, Make.com checks if it has permission. If not, the workflow stops with an error.

## Credential Checklist

You'll need to gather these before starting:

- [ ] Google Account (for Sheets, Docs, Gmail)
- [ ] OpenAI API Key (for ChatGPT access)
- [ ] Google Gemini API Key (for Gemini access)
- [ ] Anthropic Claude API Key (for Claude access)

## Step-by-Step Setup

### 1. Google Sheets, Google Docs & Gmail Connection

Make.com can use one Google connection for all three services.

**To get Google permission:**

1. In Make.com, click on any Google module and select "Add connection"
2. Choose "Google"
3. You'll be redirected to Google's login
4. Google will ask: "Make.com wants access to your Google Account"
5. Click "Allow" (Make.com is requesting access to manage Sheets, Docs, and Gmail)
6. You'll be redirected back to Make.com
7. Name this connection "Google" or similar
8. **Done** - This one connection now works for all Google services

**What Make.com can do with this:**
- Read/write Google Sheets (trigger and data storage)
- Create and edit Google Docs (publish chapters)
- Send emails via Gmail (completion notifications)

### 2. OpenAI API Key (ChatGPT)

**To get your OpenAI API key:**

1. Go to: https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key (it starts with `sk-`)
4. **Keep this private** - treat it like a password
5. In Make.com, in the ChatGPT (Module 4) connection, paste this key
6. Test the connection

**Cost:** You'll be charged for tokens used. Monitor your usage at openai.com/account/billing

### 3. Google Gemini API Key

**To get your Gemini API key:**

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. If asked, create a new project
4. Copy the API key
5. In Make.com, in the Gemini (Module 5) connection, paste this key
6. Test the connection

**Cost:** Gemini pricing depends on your plan (free tier available for testing)

### 4. Anthropic Claude API Key

**To get your Claude API key:**

1. Go to: https://console.anthropic.com/
2. Log in with your Anthropic account (create one if needed)
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (it starts with `sk-ant-`)
6. In Make.com, in the Claude (Module 7) connection, paste this key
7. Test the connection

**Cost:** You'll be charged for tokens used. Monitor usage in the Anthropic console

## Testing Each Connection

After adding each credential:

1. Click "Test" on the connection
2. If it says ✓ (green checkmark), it's connected
3. If it says ✗ (red), you likely:
   - Copied the key incorrectly
   - Used an expired key
   - Didn't have access to that service

## Credential Security Best Practices

1. **Never share your API keys** - They're like passwords
2. **Rotate keys regularly** - Delete old ones you're not using
3. **Monitor your usage** - Check each service's dashboard for unexpected charges
4. **Use environment variables in Make.com** - If possible, store keys in Make's secure vault
5. **Set spending limits** - Most AI platforms let you set monthly budget caps

### Budget Limits to Consider

Set limits on each platform to avoid surprise charges:

- **OpenAI:** https://platform.openai.com/account/billing/limits (set Usage Limits)
- **Google Gemini:** Set in Google Cloud Console
- **Anthropic Claude:** Set in Anthropic console

## Troubleshooting Connection Errors

### "Connection failed" or "Invalid API key"

**Solution:** 
- Double-check you copied the entire key (no extra spaces)
- Make sure the key isn't expired
- Regenerate the key and try again
- Clear Make.com's cache and reconnect

### "Permission denied" errors in Google connection

**Solution:**
- Make sure you're using the same Google account that owns your spreadsheet
- Check that the Google account has editor access to your Sheet
- Disconnect and reconnect the Google account

### "Rate limit exceeded" errors

**Solution:**
- This means you're hitting API limits (too many requests)
- Wait a few minutes and retry
- Consider upgrading to a paid tier if running high volume
- Increase Module 15's wait interval (currently 1 hour between chapters)

## After Setup

Once all credentials are authenticated:

1. Create your Google Sheet using the template provided in README.md
2. Add your first chapter to the "Chapter Input" sheet
3. Make.com will automatically trigger the workflow
4. Monitor the first run in Make.com's execution history
5. Check the outputs: Google Docs, spreadsheet entries, email notification

## Questions?

If a connection isn't working:
1. Test it individually in Make.com
2. Check that the API key/credentials are correct
3. Verify the service is active and not suspended
4. Review Make.com's logs for specific error messages

---

**Next Steps:**
- [ ] Gather all API keys
- [ ] Connect Google to Make.com
- [ ] Add OpenAI API key
- [ ] Add Gemini API key
- [ ] Add Claude API key
- [ ] Set budget limits on each platform
- [ ] Create Google Sheet template
- [ ] Import workflow JSON into Make.com
- [ ] Add Chapter 1 and run first test
