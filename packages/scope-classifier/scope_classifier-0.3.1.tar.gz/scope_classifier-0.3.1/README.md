# Scope Classifier

[![Type Checked with ty](https://img.shields.io/badge/type%20checked-ty-blue.svg)](https://github.com/hauntsaninja/ty)

Given the specifications of an AI assistant and a user query, `scope-classifier` classifies the user query into one of the following five classes:
*   **Directly Supported**: The query is clearly within the assistant's capabilities.
*   **Potentially Supported**: The query could plausibly be handled by the assistant.
*   **Out of Scope**: The query is outside the assistant's defined role.
*   **Restricted**: The query cannot be handled due to a specific constraint.
*   **Chit Chat**: The query is a social interaction not related to the assistant's function.

## Available Models

Currently, the following models are supported:

| Model | Parameters | Description | Accuracy | Required VRAM | Relative Speed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `small` (or `edobobo/cernas-qwen3-1.7B-v0.4`) | 1.7B | A compact and fast model for general use. | 85.3 | 8GB | 1x |
| `medium` (or `(mocked) organization/medium-model-7B`) | 7B | A larger model with better performance. | 90.7 | 12GB | 0.75x |
| `large` (or `(mocked) organization/large-model-13B`) | 13B | The best performing model for complex tasks. | 94.2 | 24GB | 0.5x |

## Quickstart

Install `scope-classifier`:

```bash
pip install scope-classifier[vllm]
```

Then:

```python
from scope_classifier import ScopeClassifier

# Initialize the classifier
classifier = ScopeClassifier(
    "vllm",  # backend (or use "hf" if you prefer not to use vllm)
    "small"  # model
)

# Define the AI assistant's scope
ai_service_description = (
    "You are a virtual assistant for a parcel delivery service. "
    "You can only answer questions about package tracking. "
    "Never respond to requests for refunds."
)

# Classify a user's query
user_query = "If the package hasn't arrived by tomorrow, can I get my money back?"
classification_output = classifier.classify(user_query, ai_service_description)

print(f"Scope: {classification_output.scope_class.value}")
if classification_output.evidences:
    print("Evidences:")
    for evidence in classification_output.evidences:
        print(f"  - {evidence}")
```

## Installation

Internally, `scope-classifier` works by prompting **local LLMs** on your data. To do this, we currently support two possible backends:
1. **HuggingFace** (`hf`): Uses HuggingFace pipelines, ideal for offline processing
2. **vLLM** (`vllm`): Faster version using vLLM, **strongly encouraged** for better performance

While `hf` comes always bundled with `scope-classifier`, you need to install some more dependencies to use `vllm`:
```bash
pip install scope-classifier[vllm]
```

> **IMPORTANT**: these two backends are local, meaning **no external API call, no data leaving your network**

## Usage

### Input Formats

The `classify` method is flexible and accepts various input formats for the conversation.

#### User query as a string

As shown in the Quick Start, you can pass the user query as a simple string.

```python
classification_output = classifier.classify(
    "When is my package scheduled to arrive?",
    ai_service_description
)
```

#### User query as a dictionary

You can also provide the user query in a dictionary format, similar to OpenAI's API:

```python
classification_output = classifier.classify(
    {"role": "user", "content": "When is my package scheduled to arrive?"},
    ai_service_description
)
```
Note that the role must be `"user"`.

#### Conversation as a list of dictionaries

For multi-turn conversations, you can pass a list of messages:

```python
conversation_history = [
    {"role": "user", "content": "I ordered a package, tracking number 1234567890"},
    {"role": "assistant", "content": "Great, the package is in transit. What would you like to know?"},
    {"role": "user", "content": "If it doesn't arrive tomorrow, can I get a refund?"},
]

classification_output = classifier.classify(conversation_history, ai_service_description)
```
The classifier will always consider the last user message for scope classification.

### Batch Processing

You can classify multiple conversations at once using `batch_classify`.

#### Single AI Service Description

Classify multiple user queries against the same AI service description:

```python
queries = [
    "If the package hasn't arrived by tomorrow, can I get my money back?",
    "When is the package expected to be delivered?"
]

classification_outputs = classifier.batch_classify(
    queries,
    ai_service_description=ai_service_description
)

for i, output in enumerate(classification_outputs):
    print(f"--- Query {i+1} ---")
    print(f"Scope: {output.scope_class.value}")
    if output.evidences:
        print("Evidences:")
        for evidence in output.evidences:
            print(f"  - {evidence}")
```

#### Multiple AI Service Descriptions

You can also provide a different AI service description for each conversation:

```python
ai_service_descriptions = [
    "You are a virtual assistant for Postal Service. You only answer questions about package tracking. Never respond to refund requests.",
    "You are a virtual assistant for a Courier. You answer questions about package tracking. Never respond to refund requests."
]

classification_outputs = classifier.batch_classify(
    queries,
    ai_service_descriptions=ai_service_descriptions
)

# Process outputs...
```

### AI Service Description

The AI service description can be provided in two ways:

1.  **As a single string**: This is a straightforward way to describe the assistant's purpose and constraints.
2.  **As a structured object**: For more detailed specifications and better performance, you can provide a dictionary or an object of type `scope_classifier.modeling.AIServiceDescription`. **This is the recommended approach.**

The `AIServiceDescription` object has the following fields:

*   `identity_role` (str): The identity, role, and objectives of the AI Service.
*   `context` (str): The context in which the AI Service operates (e.g., company, sector).
*   `functionalities` (str): The functionalities provided by the AI Service.
*   `knowledge_scope` (str): The scope of knowledge and expertise of the AI Service.
*   `conduct_guidelines` (str): Conduct guidelines and principles followed by the AI Service.
*   `constraints` (str): Constraints and limitations of the AI Service.
*   `fallback` (str): Fallback mechanisms for out-of-scope requests.
*   `website_url` (str, optional): The URL of the AI Service's website.

Using the structured format allows the underlying model to better understand the nuances of your AI assistant's scope and, therefore, perform better.

## Example Usage

The `examples/simple.py` script demonstrates a basic use of the ScopeClassifier. It provides an example of how to classify a user query based on the AI service description using command-line arguments.

```bash
python examples/simple.py vllm small
```

The script will print the classification results and evidences extracted from the AI description:

```
# scope: Restricted
# evidences:
  * evidence: Non rispondere mai a richieste di rimborso.
# time: X.XX seconds
```

## Model Serving

`scope-classifier` comes with built-in support for serving. For better performance, it consists of two components:
1. A **vLLM serving engine** that runs the model
2. A **FastAPI server** that provides the end-to-end API interface, mapping input data to prompts, invoking the vLLM serving engine and returning the response to the user

All of this is setup via the `scope-classifier serve` command:

```bash
# install the necessary packages
pip install scope-classifier[serve]

# start everything
scope-classifier serve small --port 8000
```

Once the server is running, you can interact with it as follows:

#### 1. Direct HTTP Requests

Send requests to the `/api/n/scope-classifier/classify` (or `/api/in/scope-classifier/batch-classify`) endpoint using cURL or any HTTP client:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/in/scope-classifier/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation": "If the package doesn''t arrive by tomorrow, can I get my money back?",
  "ai_service_description": "You are a virtual assistant for a parcel delivery service. You can only answer questions about package tracking. Never respond to requests for refunds."
}'
```

Response:

```json
{
  "evidences": [
    "Never respond to requests for refunds."
  ],
  "scope_class": "Restricted",
  "time_taken": 0.23,
  "model": "small"
}
```

#### 2. Python SDK

`scope-classifier` comes with built-in SDKs to invoke the server directly from Python. These SDKs support both synchronous and asynchronous invocations:

**Synchronous API client:**

```python
from scope_classifier import ScopeClassifier

classifier = ScopeClassifier(
    "api",  # backend
    "http://localhost:8000"  # API URL
)

result = classifier.classify(
    "If the package doesn't arrive by tomorrow, can I get my money back?",
    "You are a virtual assistant for a parcel delivery service. You can only answer questions about package tracking. Never respond to requests for refunds."
)

print(f"Scope: {result.scope_class.value}")
```

**Asynchronous API client:**

For async usage, use the `AsyncScopeClassifier` with the `async` backend and `await` the classify calls:

```python
from scope_classifier import AsyncScopeClassifier

classifier = AsyncScopeClassifier(
    "async",  # backend
    "http://localhost:8000"  # API URL
)

result = await classifier.classify(
    "If the package doesn't arrive by tomorrow, can I get my money back?",
    "You are a virtual assistant for a parcel delivery service. You can only answer questions about package tracking. Never respond to requests for refunds."
)

print(f"Scope: {result.scope_class.value}")
```

## License

This project is licensed under the Apache 2.0 License.
