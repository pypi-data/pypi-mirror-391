# Quick Start Guide

This guide will help you get started with the Python IDA SDK in minutes.

## Step 1: Install the SDK

```bash
pip install fayda-python-sdk
```

## Step 2: Set Up Keys

Place your PKCS12 key files in a `keys/` directory:

```
keys/
├── your-partner-id-partner.p12
└── your-partner-id-partner.cer
```

## Step 3: Configure the SDK

### Option A: Environment Variables

```bash
export PARTNER_ID="your-partner-id"
export FAYDA_BASE_URL="https://api.fayda.et"
export MISP_LICENSE_KEY="your-license-key"
export PARTNER_API_KEY="your-api-key"
export CLIENT_ID="your-client-id"
export SECRET_KEY="your-secret-key"
export P12_PATH="keys"
export P12_PASSWORD="your-password"
```

### Option B: Dictionary Configuration

```python
from fayda_py_sdk import ConfigBuilder

config = ConfigBuilder().from_dict({
    "partnerId": "your-partner-id",
    "fayda.base.url": "https://api.fayda.et",
    "mispLicenseKey": "your-license-key",
    "partnerApiKey": "your-api-key",
    "clientId": "your-client-id",
    "secretKey": "your-secret-key",
    "p12.path": "keys",
    "p12.password": "your-password",
    "ida.ssl.verify": True
})
```

## Step 4: Build the Client

```python
client = config.build()
```

## Step 5: Use the SDK

### Request OTP

```python
from fayda_py_sdk.dto import OtpRequestDTO

otp_request = OtpRequestDTO(
    individual_id="1234567890",
    individual_id_type="VID",
    otp_channel=["email"]
)

response = client.request_otp(otp_request)
print(response)
```

### Yes/No Auth

```python
from fayda_py_sdk.dto import AuthRequestDTO

auth_request = AuthRequestDTO(
    individual_id="1234567890",
    individual_id_type="VID",
    otp="123456"
)

response = client.yes_no_auth(auth_request)
print(response)
```

### Perform eKYC

```python
ekyc_request = AuthRequestDTO(
    individual_id="1234567890",
    individual_id_type="VID",
    otp="123456"
)

response = client.perform_ekyc(ekyc_request)
print(response)
```

## Complete Example

See the [example.py](../example.py) file in the repository for a complete working example.


