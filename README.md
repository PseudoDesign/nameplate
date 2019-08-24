# nameplate

A kiosk API for displaying conference room information

## Development Environment Setup

### Required Software

* Docker

### Outlook API keys

Generate API keys per the instructions [here](https://docs.microsoft.com/en-us/outlook/rest/python-tutorial)

Use the endpoint http://127.0.0.1:8000/get_token

### Docker Secrets

```bash
# Start or join a swarm
docker swarm init 

echo "APP ID" | docker secret create nameplate_api_id -
echo "APP PASSKEY" | docker secret create nameplate_api_passkey - 
```

