Text generation
===============
- cogito:3b
- cogito:8b
- gpt-oss:20b
- gemma3n:e4b

----

For gpt-oss:20b:

.. code-block::

    ollama cp gpt-oss:20b openai:gpt-4.1
    ollama cp gpt-oss:20b openai:gpt-4.1-mini
    ollama cp gpt-oss:20b openai:gpt-4.1-nano
    ollama cp gpt-oss:20b openai:o4-mini
    ollama cp gpt-oss:20b openai:gpt-4o
    ollama cp gpt-oss:20b openai:gpt-4o-mini
    ollama cp gpt-oss:20b openai:gpt-5
    ollama cp gpt-oss:20b openai:gpt-5-mini

----

For cogito:3b:

.. code-block::

    ollama cp cogito:3b openai:gpt-4.1
    ollama cp cogito:3b openai:gpt-4.1-mini
    ollama cp cogito:3b openai:gpt-4.1-nano
    ollama cp cogito:3b openai:o4-mini
    ollama cp cogito:3b openai:gpt-4o
    ollama cp cogito:3b openai:gpt-4o-mini
    ollama cp cogito:3b openai:gpt-5
    ollama cp cogito:3b openai:gpt-5-mini

----

For gemma3n:e4b:

.. code-block::

    ollama cp gemma3n:e4b openai:gpt-4.1
    ollama cp gemma3n:e4b openai:gpt-4.1-mini
    ollama cp gemma3n:e4b openai:gpt-4.1-nano
    ollama cp gemma3n:e4b openai:o4-mini
    ollama cp gemma3n:e4b openai:gpt-4o
    ollama cp gemma3n:e4b openai:gpt-4o-mini
    ollama cp gemma3n:e4b openai:gpt-5
    ollama cp gemma3n:e4b openai:gpt-5-mini

----

Image generation
================
- SDXL Base (v1.0)
- LoRA add-detail-xl (SDXL Base)

Use via DrawThings API (preview out of the box, quite fast, no need to download external models)

Pros: Takes about 30 seconds per image, but high quality, good for testing.
Cons: Inconsistent
