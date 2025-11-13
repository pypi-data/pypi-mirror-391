# Emotion Machine Python SDK

Official Python helper for the Emotion Machine Companion API. It wraps the `/v1` endpoints
documented in `docs/client-companion-api-plan.md` so you can provision companions, ingest
knowledge, and chat/stream with them in just a few lines of code.

## Installation

```bash
pip install emotion-machine
```

The client depends on `httpx` and targets Python 3.9+.

## Quickstart

1. **Export your project API key** (project-scoped):

```bash
export EM_API_KEY="emk_prod_...."
export EM_API_BASE_URL="https://api.emotionmachine.ai"  # or http://localhost:8100 for local dev
```

2. **Bootstrap a companion, ingest curated knowledge, and chat:**

```python
from emotion_machine import EmotionMachine

client = EmotionMachine()  # reads EM_API_KEY / EM_API_BASE_URL

# Create a fresh companion
companion = client.create_companion(
    name="Luteal Support Coach",
    description="Helps users track luteal phase cravings",
    config={
        "system_prompt": {
            "full_system_prompt": "You are an encouraging health coach."
        }
    },
)
companion_id = companion["id"]

# Optionally shape the profile schema for per-user traits
client.upsert_profile_schema(
    companion_id,
    schema={
        "type": "object",
        "properties": {
            "craving_intensity": {"type": "integer", "minimum": 0, "maximum":5}
        },
    },
)

# Ingest curated luteal-phase knowledge via the built-in key
job = client.ingest_knowledge(
    companion_id,
    payload_type="json",
    key="data_id_x",
)
job_result = client.wait_for_job(job["id"], timeout=20)
assert job_result["status"] == "succeeded", job_result

# Or upload & ingest your own JSON/Markdown/TXT file in one step.
# The helper uploads the file, kicks off ingestion, waits for completion,
# and raises if the job fails.
result = client.ingest_file(
    companion_id,
    file_path="important_app_related_knowledge.jsonl",
    payload_type="json",
)
print(result["job"]["status"])  # -> "succeeded"

# Run a synchronous chat completion
completion = client.chat_completion(
    companion_id,
    message="Hi! I'm feeling intense salt cravings today, what should I know?",
       external_user_id="user-123",
   )

print(completion["choices"][0]["message"]["content"])

# Stream responses (Server-Sent Events) and collect message chunks
stream = client.chat_stream(
    companion_id,
    message="Can you summarise key luteal phase symptoms?",
    external_user_id="user-123",
)
for event in stream:
    if event["event"] == "delta":
        chunk = event["data"]["choices"][0]["delta"].get("content", "")
        if chunk:
            print(chunk, end="", flush=True)
    elif event["event"] == "done":
         conversation_id = event["data"]["conversation_id"]

# Retrieve the full conversation transcript
transcript = client.get_conversation(conversation_id)
for message in transcript["messages"]:
    print(f"{message['role']}: {message['content']}")
```

3. **Tidy up when finished:**

```python
client.close()
```

   or use `with EmotionMachine() as client:` to auto-close the HTTP session.

## Knowledge management tips

- `client.list_knowledge_assets(companion_id)` shows the latest uploads plus their statuses (`ready`, `superseded`, etc.).
- Uploading a file with the **same filename** automatically replaces older ingestions for that companion’s vector store—no manual delete required.
- `client.search_knowledge(..., mode="semantic" | "keyword" | "hybrid")` lets you compare retrieval strategies against the same dataset.
- `client.wait_for_job()` and `client.ingest_file()` raise `KnowledgeJobFailed` if OpenAI reports the ingestion job as `failed`, so you can catch mistakes early in CI.

## API Coverage

| Resource        | Method                                           | SDK helper                                   |
|-----------------|---------------------------------------------------|----------------------------------------------|
| Companions      | `GET /v1/companions`                              | `client.list_companions()`                   |
|                 | `POST /v1/companions`                             | `client.create_companion(...)`               |
|                 | `GET /v1/companions/{id}`                         | `client.get_companion(id)`                   |
|                 | `PATCH /v1/companions/{id}`                       | `client.update_companion(...)`               |
| Profile Schema  | `PUT /v1/companions/{id}/profile-schema`          | `client.upsert_profile_schema(...)`          |
|                 | `GET /v1/companions/{id}/profile-schema`          | `client.get_profile_schema(...)`             |
| Knowledge       | `POST /v1/companions/{id}/knowledge`              | `client.ingest_knowledge(...)`               |
|                 | `GET /v1/knowledge-jobs/{job_id}`                 | `client.knowledge.get_job(job_id)`           |
| Chat            | `POST /v1/companions/{id}/chat`                   | `client.chat_completion(...)`                |
| Chat (stream)   | `POST /v1/companions/{id}/chat/stream`            | `client.chat_stream(...)`                    |
| Conversations   | `GET /v1/conversations/{conversation_id}`         | `client.get_conversation(...)`               |

All helpers raise `emotion_machine.APIError` on non-success HTTP codes. Inspect
`e.status_code` and `e.payload` for diagnostics.

## Development

```bash
cd packages/pip-emotion-machine
pip install -e .[dev]
```

The package ships from `src/emotion_machine`. Update `pyproject.toml` to bump versions.
