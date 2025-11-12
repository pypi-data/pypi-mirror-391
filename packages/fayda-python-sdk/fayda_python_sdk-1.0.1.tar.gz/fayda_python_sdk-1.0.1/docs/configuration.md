# Configuration

The Python IDA SDK can be configured using environment variables or a dictionary.

## Configuration Options

### Required Configuration

- `partnerId`: Your partner identifier
- `fayda.base.url`: Base URL for the Fayda API
- `mispLicenseKey`: MISP license key
- `partnerApiKey`: Partner API key
- `clientId`: Client ID for authentication
- `secretKey`: Secret key for authentication
- `p12.path`: Path to directory containing PKCS12 key files
- `p12.password`: Password for PKCS12 files

### Optional Configuration

- `ida.reference.id`: IDA reference ID (default: "PARTNER")
- `appId`: Application ID (default: "regproc")
- `ida.ssl.verify`: Enable/disable SSL verification (default: False)

## Environment Variables

Set these environment variables:

```bash
export PARTNER_ID="your-partner-id"
export FAYDA_BASE_URL="https://api.fayda.et"
export MISP_LICENSE_KEY="your-license-key"
export PARTNER_API_KEY="your-api-key"
export IDA_REFERENCE_ID="PARTNER"
export CLIENT_ID="your-client-id"
export SECRET_KEY="your-secret-key"
export APP_ID="regproc"
export P12_PATH="keys"
export P12_PASSWORD="your-password"
export IDA_SSL_VERIFY="true"
```

## Dictionary Configuration

```python
config = ConfigBuilder().from_dict({
    "partnerId": "your-partner-id",
    "fayda.base.url": "https://api.fayda.et",
    "mispLicenseKey": "your-license-key",
    "partnerApiKey": "your-api-key",
    "ida.reference.id": "PARTNER",
    "clientId": "your-client-id",
    "secretKey": "your-secret-key",
    "appId": "regproc",
    "p12.path": "keys",
    "p12.password": "your-password",
    "ida.ssl.verify": True
})
```

## Key Files

The SDK expects PKCS12 key files in the specified directory:

- `{partnerId}-partner.p12`: Partner private key and certificate
- `{partnerId}-partner.cer`: Partner certificate

## Auto-Generated URLs

The SDK automatically generates the following URLs from your configuration:

- OTP URL: `{base_url}/idauthentication/v1/otp/{license_key}/{partner_id}/{api_key}`
- Auth URL: `{base_url}/idauthentication/v1/auth/{license_key}/{partner_id}/{api_key}`
- eKYC URL: `{base_url}/idauthentication/v1/kyc/{license_key}/{partner_id}/{api_key}`
- Certificate URL: `{base_url}/idauthentication/v1/internal/getCertificate`
- Auth Manager URL: `{base_url}/v1/authmanager/authenticate/clientidsecretkey`


