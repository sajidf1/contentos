# Google Drive OAuth setup for Content Studio

This app uses **per-visitor Google OAuth 2.0**, not the repository owner's Google Drive. Visitors can create native Google Docs in their own Drive after consent.

## Google Cloud configuration

1. In Google Cloud Console, create/select a project and enable the **Google Drive API**.
2. In **Google Auth Platform**, configure Branding and Audience. Choose External if visitors use arbitrary Google accounts. While in Testing, add your own Google account as a test user; other visitors cannot authorize until the app is published (and any required verification is completed).
3. Under **Data Access**, request only `https://www.googleapis.com/auth/drive.file`.
4. Create an OAuth client of type **Web application**.
5. Add this **Authorized redirect URI**, including trailing slash: `https://content-studio-demo.streamlit.app/`.
6. Copy the Client ID and Client Secret to **Streamlit Community Cloud → app → Settings → Secrets**. Never commit them to GitHub.

Use this TOML template (replace placeholders privately):

```toml
GOOGLE_CLIENT_ID = "YOUR_WEB_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_WEB_CLIENT_SECRET"
GOOGLE_REDIRECT_URI = "https://content-studio-demo.streamlit.app/"
GOOGLE_OAUTH_STATE_SECRET = "LONG_RANDOM_SERVER_SIDE_SECRET"
```

Generate the state secret with a secure random password generator (at least 32 random bytes). It is used to sign OAuth state and must stay private.

## Visitor flow

- Select **Connect my Google Drive** in the sidebar.
- Authorize the Google `drive.file` permission.
- Run the Content Studio workflow after returning to the app.
- Click **Create Google Doc in my Drive** in the Draft section.
- The app creates a native Google Doc using Drive API file import and displays a link.

No refresh token is requested or persisted. The access token is held only in the visitor's Streamlit session and expires. Disconnect clears the session token. No document is created until the visitor explicitly clicks the creation button.

## Important constraints

- Streamlit Cloud app secrets are separate from ChatGPT's connected Google Drive.
- Google may require OAuth verification and an approved privacy policy before public use. Testing mode only works for added test users and may show an unverified-app warning.
- If the OAuth redirect returns to a new Streamlit session, visitors should run the content workflow again after connecting; drafts are not stored server-side.
- This is a demo, not a production security audit. For a public production launch, review the OAuth session/state binding, abuse prevention, privacy notice, token handling and error monitoring.
