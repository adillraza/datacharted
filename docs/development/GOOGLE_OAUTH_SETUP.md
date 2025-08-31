# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for your DataCharted application.

## 🚀 What We've Implemented

✅ **Google OAuth Integration** - Users can sign up and login with Google  
✅ **Automatic Account Creation** - New Google users get accounts created automatically  
✅ **Account Linking** - Existing users can link their accounts to Google  
✅ **Seamless Authentication** - No password required for Google users  

## 🔧 Setup Steps

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** and **Google OAuth2 API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Web application** as the application type
6. Add these authorized redirect URIs:
   - `http://localhost:5000/login/google/callback` (for local development)
   - `https://app.datacharted.com/login/google/callback` (for production)
7. Copy your **Client ID** and **Client Secret**

### 2. Environment Configuration

Create a `.env` file in your project root with:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Other required settings
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 3. Database Migration

The database has been updated with new fields:
- `google_id` - Unique Google user identifier
- `google_picture` - User's Google profile picture
- `auth_provider` - Authentication method ('local' or 'google')

## 🎯 How It Works

### Sign Up Flow
1. User clicks "Sign up with Google"
2. Redirected to Google OAuth consent screen
3. User authorizes the application
4. Google returns user data (email, name, picture)
5. System creates new account or links existing one
6. User is automatically logged in

### Login Flow
1. User clicks "Continue with Google"
2. Redirected to Google OAuth consent screen
3. User authorizes the application
4. System finds existing account by Google ID or email
5. User is automatically logged in

### Account Linking
- If a user signs up with Google using an email that already exists in the system, the accounts are automatically linked
- Users can still use their password to login, or Google OAuth

## 🔒 Security Features

✅ **OAuth 2.0 Protocol** - Industry standard authentication  
✅ **Secure Token Exchange** - No passwords stored for Google users  
✅ **Account Verification** - Google users are automatically verified  
✅ **Unique Constraints** - Google IDs are unique across the system  

## 🧪 Testing

### Local Development
1. Set up your `.env` file with Google credentials
2. Run the Flask development server
3. Visit `http://localhost:5000/auth/login`
4. Click "Continue with Google"
5. Complete Google OAuth flow

### Production
1. Update your production environment variables
2. Deploy the updated code
3. Test on `https://app.datacharted.com/auth/login`

## 🐛 Troubleshooting

### Common Issues

**"Google authentication failed"**
- Check your Google OAuth credentials
- Verify redirect URIs are correct
- Ensure Google+ API is enabled

**"Invalid redirect URI"**
- Make sure your redirect URI exactly matches what's configured in Google Console
- Check for trailing slashes or protocol mismatches

**Database errors**
- Run `flask db upgrade` to apply migrations
- Check that all new columns exist in your database

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=1` in your environment.

## 📱 User Experience

### For New Users
- One-click signup with Google
- No password creation required
- Automatic account verification
- Profile picture imported from Google

### For Existing Users
- Can link their account to Google
- Maintain access to existing data
- Choose between password and Google login

### For All Users
- Seamless authentication experience
- No need to remember another password
- Quick access to the application

## 🚀 Next Steps

After setting up Google OAuth, consider:

1. **Email Verification** - Implement email verification for local accounts
2. **Profile Management** - Allow users to update their Google-linked profiles
3. **Account Unlinking** - Option to remove Google association
4. **Additional Providers** - Add Facebook, GitHub, or other OAuth providers

## 📚 Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Flask-OAuthlib Documentation](https://flask-oauthlib.readthedocs.io/)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**Need Help?** Check the application logs or create an issue in the repository.
