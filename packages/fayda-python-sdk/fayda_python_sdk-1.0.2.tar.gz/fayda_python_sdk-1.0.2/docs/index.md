# Python IDA SDK Documentation

Welcome to the Python IDA SDK documentation.

## Overview

The Python IDA SDK provides a Python interface for interacting with Fayda's Identity Authentication (IDA) services. It enables Python applications to:

- Request OTPs for individual verification
- Yes/No Auth using OTP
- Perform eKYC (electronic Know Your Customer) operations

## Installation

```bash
pip install fayda-python-sdk
```

## Quick Start

```python
from fayda_py_sdk import ConfigBuilder, EkycClient
from fayda_py_sdk.dto import OtpRequestDTO, AuthRequestDTO

# Configure the SDK
config = ConfigBuilder().from_dict({
    "partnerId": "your-partner-id",
    "fayda.base.url": "https://api.fayda.et",
    # ... other configuration
})

# Build the client
client = config.build()

# Request OTP
otp_request = OtpRequestDTO(
    individual_id="1234567890123456",
    individual_id_type="FAN",
    otp_channel=["email"]
)
otp_response = client.request_otp(otp_request)

# Yes/No Auth
auth_request = AuthRequestDTO(
    individual_id="1234567890123456",
    individual_id_type="FAN",
    otp="123456"
)
auth_response = client.yes_no_auth(auth_request)

# Perform eKYC
ekyc_response = client.perform_ekyc(auth_request)
```

## API Reference

### ConfigBuilder

Configuration builder for setting up the SDK.

#### Methods

- `from_dict(config: Dict[str, Any]) -> ConfigBuilder`: Load configuration from dictionary
- `from_env() -> ConfigBuilder`: Load configuration from environment variables
- `set_config(key: str, value: Any) -> ConfigBuilder`: Set individual configuration value
- `build() -> EkycClient`: Build and return configured client

### EkycClient

Main client class for interacting with IDA services.

#### Methods

- `request_otp(otp_request: OtpRequestDTO) -> Dict[str, Any]`: Request OTP for an individual
- `yes_no_auth(auth_request: AuthRequestDTO) -> Dict[str, Any]`: Yes/No Auth using OTP
- `perform_ekyc(auth_request: AuthRequestDTO) -> Dict[str, Any]`: Perform eKYC operation

## Configuration

See the main [README.md](../README.md) for detailed configuration options.

## Examples

See the [example.py](../example.py) file for complete working examples.

## Support

For issues or questions, please visit the [GitHub Issues](https://github.com/National-ID-Program-Ethiopia/python-ida-sdk/issues) page.

