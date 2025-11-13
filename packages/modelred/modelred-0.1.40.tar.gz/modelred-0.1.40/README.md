# 🧠 ModelRed Python SDK

> **Official Python SDK for [ModelRed.ai](https://www.modelred.ai)** —  
> Run large-scale security assessments and risk analysis on any LLM or AI system.

---

## 🚀 Overview

ModelRed helps you **red-team, benchmark, and secure** your language models and AI systems.

This SDK provides a simple interface to:

- ✅ List your registered models
- ✅ Browse owned & imported probe packs
- ✅ Run **security assessments** programmatically
- ✅ Retrieve assessment details & scores
- ✅ Handle robust error types for production reliability

The SDK is **typed, retry-aware**, and designed for both **sync** and **async** workflows.

---

## 🧩 Installation

```bash
pip install modelred
```

> Requires Python 3.8+

---

## 🔑 Authentication

Generate your API key (`mr_...`) from the **ModelRed web app**:

👉 [https://www.app.modelred.ai](https://www.app.modelred.ai)

Keep it private — your key determines the organization context.

---

## ⚡ Quickstart

### Synchronous example

```python
from modelred import ModelRed

client = ModelRed(api_key="mr_...")

# 1. List your models
models = client.list_models()
model_id = models["data"][0]["id"]

# 2. List your owned probe packs
packs = client.list_owned_probes()["data"]
probe_pack_ids = [p["id"] for p in packs[:2]]

# 3. Create a new assessment
resp = client.create_assessment(
    model_id=model_id,
    probe_pack_ids=probe_pack_ids,
)
print(resp)
```

### Asynchronous example

```python
import asyncio
from modelred import AsyncModelRed

async def main():
    async with AsyncModelRed(api_key="mr_...") as client:
        models = await client.list_models()
        model_id = models["data"][0]["id"]

        packs = await client.list_owned_probes()
        probe_pack_ids = [p["id"] for p in packs["data"][:2]]

        resp = await client.create_assessment(
            model_id=model_id,
            probe_pack_ids=probe_pack_ids,
        )
        print(resp)

asyncio.run(main())
```

---

## 📘 Common Methods

| Category        | Method                                           | Description                                    |
| --------------- | ------------------------------------------------ | ---------------------------------------------- |
| **Models**      | `list_models()`                                  | List your registered models                    |
| **Probe Packs** | `list_owned_probes()` / `list_imported_probes()` | Browse your probe packs                        |
| **Assessments** | `create_assessment()`                            | Run a test suite on a model                    |
|                 | `list_assessments()`                             | View past runs                                 |
|                 | `get_assessment(id)`                             | Fetch full details                             |
|                 | `cancel_assessment(id)`                          | Cancel (UI-only, raises `NotAllowedForApiKey`) |

---

## 🧱 Error Handling

Every API error is a specific exception:

```python
from modelred.errors import Unauthorized, LimitExceeded, NotAllowedForApiKey

try:
    resp = client.create_assessment(...)
except Unauthorized:
    print("Invalid or expired API key")
except LimitExceeded as e:
    print("Plan limit hit:", e.message)
except NotAllowedForApiKey:
    print("This action must be done from the web UI")
```

| Exception                          | Meaning                     |
| ---------------------------------- | --------------------------- |
| `Unauthorized`                     | 401 — bad or missing key    |
| `Forbidden`, `NotAllowedForApiKey` | 403 — disallowed action     |
| `LimitExceeded`                    | 403 — plan or usage limit   |
| `NotFound`                         | 404 — resource not found    |
| `Conflict`                         | 409 — concurrent/duplicate  |
| `ValidationFailed`                 | 400/422 — bad request       |
| `RateLimited`                      | 429 — retry with backoff    |
| `ServerError`                      | 5xx — internal server issue |

---

## 🧪 Testing (optional)

You can test locally using the included **mock mode**:

```bash
MODELRED_TEST_MODE=mock python test_runner.py
```

This uses `httpx.MockTransport` to simulate API responses — no network required.

To test live, set your real environment variables:

```bash
export MODELRED_API_KEY="mr_..."
python test_runner.py
```

---

## 🔗 Links

- 🌐 [Website](https://www.modelred.ai)
- 💡 [App Dashboard](https://www.app.modelred.ai)
- 📄 [Docs (MDX)](https://docs.modelred.ai)
- 🧰 [GitHub](https://github.com/modelred-ai/sdk-python)

---

## 📜 License

MIT License © 2025 ModelRed.ai  
Developed with ❤️ by the ModelRed Engineering Team
