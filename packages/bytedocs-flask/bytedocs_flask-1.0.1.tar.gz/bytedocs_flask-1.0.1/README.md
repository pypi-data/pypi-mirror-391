# ByteDocs Flask

Automatic API documentation generator for Flask, inspired by Scramble for Laravel.

ByteDocs Flask automatically generates beautiful, interactive API documentation for your Flask applications using AST (Abstract Syntax Tree) analysis to detect routes, request bodies, and response schemas.

## Features

- 🚀 **Auto-detection**: Automatically detects Flask routes and generates documentation
- 🎨 **Beautiful UI**: Clean, modern interface with multiple themes
- 🔍 **AST Analysis**: Deep code analysis to detect request/response schemas
- 📝 **OpenAPI Compatible**: Generates OpenAPI 3.0 specification
- 🎯 **Try It Out**: Test your API directly from the documentation
- 🌍 **Multi-Environment**: Support for multiple base URLs (dev, staging, prod)
- 🤖 **AI-Powered** (optional): Chat with AI about your API documentation
- 🔐 **Authentication** (optional): Protect your docs with various auth methods

## Installation

```bash
pip install bytedocs-flask
```

## Quick Start

```python
from flask import Flask
from bytedocs_flask import setup_bytedocs

app = Flask(__name__)

# Your routes
@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    return {"users": []}

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Get a specific user by ID"""
    return {"id": id, "name": "John Doe"}

# Setup ByteDocs
setup_bytedocs(app, {
    "title": "My API",
    "version": "1.0.0",
    "description": "My awesome API documentation",
    "base_url": "http://localhost:5000"
})

if __name__ == '__main__':
    app.run(debug=True)
```

Then visit `http://localhost:5000/docs` to see your documentation!

## Configuration

You can configure ByteDocs using a dictionary or environment variables:

### Python Configuration

```python
from bytedocs_flask import setup_bytedocs

setup_bytedocs(app, {
    "title": "My API",
    "version": "1.0.0",
    "description": "My API Documentation",
    "base_urls": [
        {"name": "Development", "url": "http://localhost:5000"},
        {"name": "Production", "url": "https://api.example.com"}
    ],
    "docs_path": "/docs",
    "auto_detect": True,
    "exclude_paths": ["/admin", "/internal"],
    "ui_config": {
        "theme": "green",  # auto, green, blue, purple, red, orange, teal, pink
        "dark_mode": False,
        "show_try_it": True,
        "show_schemas": True
    }
})
```

### Environment Variables

```env
# Basic Config
BYTEDOCS_TITLE=My API
BYTEDOCS_VERSION=1.0.0
BYTEDOCS_DESCRIPTION=My API Documentation
BYTEDOCS_BASE_URL=http://localhost:5000

# Or use multiple environments
BYTEDOCS_LOCAL_URL=http://localhost:5000
BYTEDOCS_PRODUCTION_URL=https://api.example.com

# Paths
BYTEDOCS_DOCS_PATH=/docs
BYTEDOCS_EXCLUDE_PATHS=/admin,/internal

# UI Configuration
BYTEDOCS_UI_THEME=green
BYTEDOCS_UI_DARK_MODE=false
BYTEDOCS_UI_SHOW_TRY_IT=true
BYTEDOCS_UI_SHOW_SCHEMAS=true
```

## AI Features (Optional)

ByteDocs Flask includes AI-powered chat to help users understand your API.

### Installation with AI

```bash
pip install bytedocs-flask[ai]
```

### Enable AI Chat

```python
setup_bytedocs(app, {
    "title": "My API",
    "version": "1.0.0",
    "ai_config": {
        "enabled": True,
        "provider": "openai",  # or "gemini", "anthropic", "openrouter"
        "api_key": "your-api-key",
        "features": {
            "chat_enabled": True,
            "model": "gpt-4o-mini",  # optional
            "temperature": 0.7
        }
    }
})
```

Or using environment variables:

```env
BYTEDOCS_AI_ENABLED=true
BYTEDOCS_AI_PROVIDER=openai
BYTEDOCS_AI_API_KEY=your-api-key
BYTEDOCS_AI_MODEL=gpt-4o-mini
```

### Supported AI Providers

- **OpenAI**: GPT-4, GPT-4o, GPT-3.5-turbo
- **Google Gemini**: gemini-2.0-flash-exp, gemini-pro
- **Anthropic Claude**: claude-3-5-sonnet, claude-3-opus
- **OpenRouter**: Access to multiple models

### Token Optimization

ByteDocs automatically optimizes context to reduce AI costs by 70-80%:
- Minification: Remove whitespace
- Compression: Remove non-essential fields
- Filtering: Focus on relevant endpoints

## Advanced Features

### Request Body Detection

ByteDocs automatically detects request body usage in your handlers:

```python
from flask import request

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    # ByteDocs detects 'name' and 'email' fields from AST analysis
    return {"id": 1, "name": name, "email": email}
```

### Response Schema Detection

ByteDocs analyzes return statements to detect response schemas:

```python
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Get user by ID"""
    return {
        "id": id,
        "name": "John Doe",
        "email": "john@example.com",
        "active": True
    }
    # ByteDocs automatically creates schema from the returned dict
```

### Custom Documentation

You can enhance auto-generated docs with docstrings:

```python
@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user

    This endpoint creates a new user in the system.
    Requires authentication.
    """
    # ... implementation
```

## API Endpoints

Once set up, ByteDocs provides these endpoints:

- `GET /docs` - Interactive documentation UI
- `GET /docs/api-data.json` - Documentation data as JSON
- `GET /docs/openapi.json` - OpenAPI 3.0 specification (JSON)
- `GET /docs/openapi.yaml` - OpenAPI 3.0 specification (YAML)

## Requirements

- Python 3.8+
- Flask 2.0+

## License

MIT License - see LICENSE file for details

## Credits

- Inspired by [Scramble](https://scramble.dedoc.co/) for Laravel
- Based on ByteDocs FastAPI implementation
- Part of the ByteDocs family (Express, FastAPI, Flask)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: https://github.com/aibnuhibban/bytedocs-flask/issues
