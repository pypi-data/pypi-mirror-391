# ByteDocs Django

**Beautiful API documentation for Django** - A modern alternative to Swagger and Scramble.

ByteDocs Django automatically generates interactive API documentation from your Django views and Django REST Framework serializers, with optional AI-powered features.

## ✨ Features

- 🚀 **Zero Configuration** - Works out of the box with sensible defaults
- 📝 **Auto-Detection** - Automatically discovers Django views and DRF ViewSets
- 🎨 **Beautiful UI** - Modern, responsive interface with 8 color themes
- 🤖 **AI-Powered** - Optional AI assistant for API queries (OpenAI, Gemini, Claude, OpenRouter)
- 🔧 **Try It Out** - Interactive API testing directly in the documentation
- 📊 **OpenAPI 3.0** - Full OpenAPI specification export (JSON & YAML)
- 🎯 **DRF Support** - First-class Django REST Framework integration
- 🔐 **Authentication** - Built-in auth support (Basic, API Key, Bearer, Session)
- 🌍 **Multi-Environment** - Support for multiple base URLs (dev, staging, prod)
- ⚡ **Lightweight** - No heavy dependencies, fast performance

## 📸 Screenshots

[Screenshots will be added here]

## 🚀 Quick Start

### Installation

```bash
pip install bytedocs-django
```

### Basic Setup

1. **Add to your Django project's `urls.py`**:

```python
from django.urls import path, include
from bytedocs_django import setup_bytedocs

# Setup ByteDocs
bytedocs = setup_bytedocs(config={
    "title": "My API",
    "version": "1.0.0",
    "description": "My awesome API built with Django",
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.urls')),
    path('docs/', include('bytedocs_django.urls')),
]

# Auto-detect routes
bytedocs.detect_routes()
```

2. **That's it!** Visit `http://localhost:8000/docs/` to see your documentation.

## 📚 Documentation

### Configuration

ByteDocs supports both programmatic and environment-based configuration.

#### Programmatic Configuration

```python
from bytedocs_django import setup_bytedocs

bytedocs = setup_bytedocs(config={
    "title": "My API",
    "version": "1.0.0",
    "description": "API Documentation",
    "base_urls": [
        {"name": "Development", "url": "http://localhost:8000"},
        {"name": "Production", "url": "https://api.example.com"},
    ],
    "docs_path": "/docs",
    "ui_config": {
        "theme": "purple",
        "dark_mode": True,
        "show_try_it": True,
        "show_schemas": True,
    },
    "ai_config": {
        "enabled": True,
        "provider": "openai",
        "api_key": "your-api-key",
        "features": {
            "chat_enabled": True,
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        },
    },
})
```

#### Environment Variables

Create a `.env` file:

```env
BYTEDOCS_TITLE=My API
BYTEDOCS_VERSION=1.0.0
BYTEDOCS_DESCRIPTION=API Documentation
BYTEDOCS_BASE_URL=http://localhost:8000

# UI Configuration
BYTEDOCS_UI_THEME=purple
BYTEDOCS_UI_DARK_MODE=true

# AI Configuration
BYTEDOCS_AI_ENABLED=true
BYTEDOCS_AI_PROVIDER=openai
BYTEDOCS_AI_API_KEY=sk-...
```

### Django REST Framework Integration

ByteDocs automatically extracts schema information from DRF serializers:

```python
from rest_framework import viewsets, serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Product serializer with full schema"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.

    list:
    Get all products with pagination.

    create:
    Create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

ByteDocs will automatically:
- ✅ Extract field types and descriptions
- ✅ Detect required fields
- ✅ Parse docstrings for endpoint descriptions
- ✅ Generate request/response schemas
- ✅ Create interactive examples

### Customization

#### Add Tags

```python
class ProductViewSet(viewsets.ModelViewSet):
    bytedocs_tags = ["Products", "E-commerce"]
    # ...
```

#### Custom Schemas

ByteDocs supports:
- Django REST Framework Serializers
- Pydantic models (django-ninja)
- Django model forms
- Dataclasses
- Type hints

### AI Features

Enable AI-powered documentation assistant:

```env
BYTEDOCS_AI_ENABLED=true
BYTEDOCS_AI_PROVIDER=openai
BYTEDOCS_AI_API_KEY=your-key-here
```

Supported providers:
- **OpenAI** (GPT-4, GPT-3.5)
- **Google Gemini** (gemini-2.0-flash, gemini-1.5-pro)
- **Anthropic Claude** (claude-3-5-sonnet, claude-3-opus)
- **OpenRouter** (access to multiple models)

Features:
- 💬 Chat with AI about your API
- 🔍 Context-aware responses
- 📉 70-80% token savings with optimization
- 🎯 Endpoint-specific queries

### Authentication

Protect your documentation with built-in authentication:

```env
BYTEDOCS_AUTH_ENABLED=true
BYTEDOCS_AUTH_TYPE=session
BYTEDOCS_AUTH_PASSWORD=your-secure-password
```

Supported auth types:
- **Session** - Password-protected with sessions
- **Basic** - HTTP Basic authentication
- **API Key** - Custom header authentication
- **Bearer** - Bearer token authentication

### Themes

Choose from 8 beautiful themes:
- `green` (default)
- `blue`
- `purple`
- `red`
- `orange`
- `teal`
- `pink`
- `auto` (system preference)

### OpenAPI Export

ByteDocs generates full OpenAPI 3.0 specifications:

- **JSON**: `http://localhost:8000/docs/openapi.json`
- **YAML**: `http://localhost:8000/docs/openapi.yaml`

Use these files with other tools like Postman, Insomnia, or code generators.

## 🎯 Use Cases

- **API Documentation** - Beautiful, interactive documentation for your Django API
- **API Testing** - Test endpoints directly in the browser
- **Team Collaboration** - Share documentation with your team
- **Client Integration** - Help clients understand your API
- **OpenAPI Export** - Generate OpenAPI specs for other tools

## 📦 Requirements

- Python 3.8+
- Django 3.2+
- Django REST Framework (optional, for DRF support)
- OpenAI/Gemini/Anthropic API key (optional, for AI features)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Credits

ByteDocs Django is inspired by:
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Scramble](https://scramble.dedoc.co/) (Laravel)
- [ByteDocs Express](https://github.com/bytedocs/bytedocs-express)

## 🔗 Links

- [Documentation](https://docs.bytedocs.com)
- [GitHub](https://github.com/bytedocs/bytedocs-django)
- [PyPI](https://pypi.org/project/bytedocs-django/)
- [Issues](https://github.com/bytedocs/bytedocs-django/issues)

## 💡 Example Projects

Check out the `examples/` directory for complete example projects:

- **Basic Example** - Simple Django + DRF API with ByteDocs
- More examples coming soon!

## 🚀 Roadmap

- [ ] Authentication middleware
- [ ] Custom CSS/JS injection
- [ ] Request/response examples from code
- [ ] Versioned documentation
- [ ] Markdown documentation pages
- [ ] API changelog generation
- [ ] GraphQL support
- [ ] WebSocket documentation

---

Made with ❤️ by the ByteDocs team
