## Azure cli

Tools:
- az (read-only verbs only; requires `--subscription`)
- search_context (lists subscriptions)

Requires the Azure CLI (`az`) in your `PATH`.

Authentication uses a service principal if these environment variables are set before launch:
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`

Run:
```bash
python -m src.cloud_ops_azure.server
```
