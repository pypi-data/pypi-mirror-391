# API Reference

## ConfigBuilder

Configuration builder for the SDK.

### Methods

#### `from_dict(config: Dict[str, Any]) -> ConfigBuilder`

Load configuration from a dictionary.

**Parameters:**
- `config`: Dictionary containing configuration keys and values

**Returns:** `ConfigBuilder` instance for method chaining

#### `from_env() -> ConfigBuilder`

Load configuration from environment variables.

**Returns:** `ConfigBuilder` instance for method chaining

#### `set_config(key: str, value: Any) -> ConfigBuilder`

Set a single configuration value.

**Parameters:**
- `key`: Configuration key
- `value`: Configuration value

**Returns:** `ConfigBuilder` instance for method chaining

#### `build() -> EkycClient`

Build and return a configured `EkycClient` instance.

**Returns:** Configured `EkycClient` instance

## EkycClient

Main client class for interacting with IDA services.

### Methods

#### `request_otp(otp_request: OtpRequestDTO) -> Dict[str, Any]`

Request an OTP for an individual.

**Parameters:**
- `otp_request`: `OtpRequestDTO` containing individual ID and OTP channel

**Returns:** Dictionary containing the OTP response

#### `yes_no_auth(auth_request: AuthRequestDTO) -> Dict[str, Any]`

Yes/No Auth for an individual using OTP.

**Parameters:**
- `auth_request`: `AuthRequestDTO` containing individual ID and OTP

**Returns:** Dictionary containing authentication response

#### `perform_ekyc(auth_request: AuthRequestDTO) -> Dict[str, Any]`

Perform eKYC operation to retrieve verified identity information.

**Parameters:**
- `auth_request`: `AuthRequestDTO` containing individual ID and OTP

**Returns:** Dictionary containing eKYC response with decrypted identity information

## DTOs

### OtpRequestDTO

Request DTO for OTP generation.

**Fields:**
- `individual_id` (str): Individual identifier
- `individual_id_type` (str): Type of ID (FIN or FAN)
- `otp_channel` (List[str]): Channels for OTP delivery (["email"], ["phone"], ["mobile"])

### AuthRequestDTO

Request DTO for authentication and eKYC.

**Fields:**
- `individual_id` (str): Individual identifier
- `individual_id_type` (str): Type of ID
- `otp` (str): OTP code for authentication
- `requested_auth` (AuthTypeDTO, optional): Authentication type configuration
- `transaction_id` (str, optional): Transaction identifier


