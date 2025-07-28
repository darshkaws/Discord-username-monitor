# Account Configuration

This directory contains your Discord account tokens for monitoring.

## Setup Instructions

1. Copy `tokens.txt.example` to `tokens.txt`
2. Add your Discord account credentials to `tokens.txt`
3. The tool supports multiple formats - see examples below

## Supported Formats

### Format 1: Email:Password:Token (Recommended)
```
user@example.com:mypassword:your_discord_token_here
```

### Format 2: Email:Token
```
user@example.com:your_discord_token_here
```

### Format 3: Token Only
```
your_discord_token_here
```

## Security Notes

- **Never share your tokens publicly**
- Tokens provide full access to your Discord account
- Use separate accounts for monitoring (recommended)
- Keep this file secure and never commit it to version control

## Getting Your Discord Token

1. Open Discord in your browser
2. Press F12 to open Developer Tools
3. Go to Network tab
4. Refresh the page
5. Look for requests to `discord.com/api`
6. Check request headers for `Authorization` field
7. Copy the token (without "Bearer " prefix)

## Password Requirements

- Password is required for auto-claiming features
- Used for username change requests
- Can be omitted for notification-only mode

## Account Validation

The tool can validate tokens before use:
- Checks if tokens are active and valid
- Removes invalid accounts automatically
- Provides validation report during startup

