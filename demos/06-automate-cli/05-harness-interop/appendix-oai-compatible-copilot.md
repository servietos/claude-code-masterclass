# Appendix: DeepSeek V4.1 Flash and Kimi K3 in VS Code Copilot Chat

[OAI Compatible Provider for Copilot](https://marketplace.visualstudio.com/items?itemName=johnny-zhao.oai-compatible-copilot) by Johnny Zhao adds OpenAI-compatible providers to the model picker of GitHub Copilot Chat in VS Code. With it, the two DeepInfra models of this topic move from the terminal into the editor on the same key and the same model ids. It needs VS Code 1.104.0 or higher.

## Configure the Two Models

Install the extension, then add DeepInfra and both models to your user `settings.json`:

```json
"oaicopilot.baseUrl": "https://api.deepinfra.com/v1/openai",
"oaicopilot.models": [
  {
    "id": "deepseek-ai/DeepSeek-V4.1-Flash",
    "owned_by": "deepinfra"
  },
  {
    "id": "moonshotai/Kimi-K3",
    "owned_by": "deepinfra",
    "context_length": 1048576
  }
]
```

`owned_by` groups the API key, so both models share one DeepInfra key, stored as `oaicopilot.apiKey.deepinfra`. Without `context_length` a model gets the default of 128000 tokens.

## Add the Key and Pick a Model

1. Open Copilot Chat with `Ctrl+Shift+I`, click the model picker and select **Manage Models...**.
2. Choose the **OAI Compatible** provider and paste your DeepInfra key when asked.
3. Tick DeepSeek V4.1 Flash and Kimi K3.
4. Select either model in the picker and chat.

To change the key later, run **OAICopilot: Set OAI Compatible Multi-Provider API Key** from the Command Palette (`Ctrl+Shift+P`).
