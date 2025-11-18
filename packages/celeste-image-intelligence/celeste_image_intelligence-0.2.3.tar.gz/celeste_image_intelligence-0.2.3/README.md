<div align="center">

# <img src="../../logo.svg" width="48" height="48" alt="Celeste Logo" style="vertical-align: middle;"> Celeste Image Intelligence

**Image Intelligence capability for Celeste AI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red?style=for-the-badge)](../../LICENSE)

[Quick Start](#-quick-start) • [Documentation](https://withceleste.ai/docs) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

---

## 🚀 Quick Start

```python
from celeste import create_client, Capability, Provider
from celeste.artifacts import ImageArtifact

client = create_client(
    capability=Capability.IMAGE_INTELLIGENCE,
    provider=Provider.GOOGLE,
)

image = ImageArtifact(url="https://example.com/image.jpg")
response = await client.generate(
    image=image,
    prompt="What's in this image?"
)
print(response.content)
```

**Install:**
```bash
uv add "celeste-ai[image-intelligence]"
```

---

## Supported Providers


<div align="center">

<img src="https://www.google.com/s2/favicons?domain=google.com&sz=64" width="64" height="64" alt="Google" title="Google">


**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---

**Streaming**: ✅ Supported

**Parameters**: See [API Documentation](https://withceleste.ai/docs/api) for full parameter reference.

---

## 🤝 Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

**Request a provider:** [GitHub Issues](https://github.com/withceleste/celeste-python/issues/new)

---

## 📄 License

Apache 2.0 License – see [LICENSE](../../LICENSE) for details.

---

<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
