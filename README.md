# nameplate

A kiosk API for displaying conference room information

## Development Environment Setup

### Required Software

* Pycharm
* Docker
* A unix-like shell.  If you're using Windows, try [Cmder](https://cmder.net/).

### Outlook API keys

Generate API keys per the instructions [here](https://docs.microsoft.com/en-us/outlook/rest/python-tutorial)

Use the endpoint http://127.0.0.1:8000/get_token

### Docker Secrets

```bash
# Start or join a swarm
mkdir .keys
echo "APP ID" > .keys/nameplate_api_id
echo "APP PASSKEY" > .keys/nameplate_api_passkey
```

### Pycharm

