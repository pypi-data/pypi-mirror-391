# Examples

## Complete Example

```python
from fayda_py_sdk import ConfigBuilder
from fayda_py_sdk.dto import OtpRequestDTO, AuthRequestDTO
import json

# Configure SDK
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

# Build client
client = config.build()

# Step 1: Request OTP
otp_request = OtpRequestDTO(
    individual_id="1234567890",
    individual_id_type="FAN",
    otp_channel=["email"]
)

otp_response = client.request_otp(otp_request)
print("OTP Response:", json.dumps(otp_response, indent=2))

# Step 2: Yes/No Auth (optional - OTP is consumed)
auth_request = AuthRequestDTO(
    individual_id="1234567890",
    individual_id_type="FAN",
    otp="123456"  # OTP received from step 1
)

auth_response = client.yes_no_auth(auth_request)
print("Yes/No Auth Response:", json.dumps(auth_response, indent=2))

# Step 3: Perform eKYC (requires fresh OTP)
# Note: Request a new OTP if you used it for authentication
ekyc_request = AuthRequestDTO(
    individual_id="1234567890",
    individual_id_type="FAN",
    otp="123456"  # Use fresh OTP
)

ekyc_response = client.perform_ekyc(ekyc_request)
print("eKYC Response:", json.dumps(ekyc_response, indent=2))
```

## Using Environment Variables

```python
import os
from fayda_py_sdk import ConfigBuilder

# Set environment variables (usually done in shell or .env file)
os.environ["PARTNER_ID"] = "your-partner-id"
os.environ["FAYDA_BASE_URL"] = "https://api.fayda.et"
# ... set other variables

# Build from environment
config = ConfigBuilder().from_env()
client = config.build()
```

## Error Handling

```python
from fayda_py_sdk import ConfigBuilder
from fayda_py_sdk.dto import OtpRequestDTO

try:
    client = ConfigBuilder().from_dict({
        # ... configuration
    }).build()
    
    otp_request = OtpRequestDTO(
        individual_id="1234567890",
        individual_id_type="FAN",
        otp_channel=["email"]
    )
    
    response = client.request_otp(otp_request)
    
    if "errors" in response and response["errors"]:
        print("Errors:", response["errors"])
    else:
        print("Success:", response)
        
except RuntimeError as e:
    print(f"Runtime error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## More Examples

See the [example.py](../example.py) file in the repository root for additional examples.


