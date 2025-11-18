"""
Sample YAML configurations for the WebProvider model.
These examples demonstrate how to structure the YAML file for each
supported authentication method and for a provider with no authentication.

--- Example 1: Basic Authentication ---
Use this for endpoints protected by HTTP Basic Auth.
The `username` and `password` will be used to generate the
'Authorization: Basic <base64_encoded_credentials>' header.

provider: web
config:
  endpoint: https://api.my-service.com/v1/resource
  auth:
    auth_type: basic
    username: myuser
    password: "mysecretpassword123"

--- Example 2: Bearer Token Authentication ---
This is a very common pattern for APIs that use a simple API key or JWT.
The `token` will be used to generate the
'Authorization: Bearer <token>' header.

provider: web
config:
  endpoint: https://api.some-saas.com/graphql
  auth:
    auth_type: bearer
    token: "your-secret-api-key-goes-here"

--- Example 3: OAuth2 Client Credentials Flow ---
Use this for machine-to-machine authentication where your application
needs to get a token from an authorization server first.

provider: web
config:
  endpoint: https://api.enterprise-app.com/data
  auth:
    auth_type: oauth2_client_credentials
    token_url: https://auth.enterprise-app.com/oauth/token
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    scope: "read:data write:data"

--- Example 4: Username/Password Authentication ---
This is distinct from Basic Auth. It's for services that might expect
the username and password in the request body (e.g., a JSON payload).
How these are used depends on the client implementation.

provider: web
config:
  endpoint: https://internal.dashboard.local/api/login
  auth:
    auth_type: username_password
    username: admin
    password: "admin_password_for_json_body"

--- Example 5: No Authentication ---
For interacting with public APIs that don't require any credentials.
The `auth` block is simply omitted.

provider: web
config:
  endpoint: https://api.public-apis.org/entries

--- Example 6: Complex Provider with Crawling Parameters ---
This shows how to include explicit parameters for controlling crawling behavior,
such as timeouts, retries, and custom headers.

provider: web
config:
  endpoint: https://api.custom-solution.dev/v2/invoke
  auth:
    auth_type: bearer
    token: "your-custom-token"
  params:
    timeout_seconds: 30
    max_retries: 3
    delay_between_requests_seconds: 1.5
    allow_redirects: true
    headers:
      User-Agent: "MyAwesomeCrawler/1.0 (contact@example.com)"
      X-Request-ID: "some-unique-value"
    extra_params:
      # Use extra_params for any other non-standard options
      # your client might need.
      some_other_option: true
"""
import os
from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, Field, SecretStr, HttpUrl, ConfigDict, field_validator

# --- AUTHENTICATION MODELS ---
# We use a "discriminated union" to model different authentication strategies.
# Pydantic will validate the data based on the value of the `auth_type` field.

class BaseAuthConfig(BaseModel):
    """Base model for all authentication types. Ensures env vars can be loaded."""
    model_config = ConfigDict(validate_assignment=True)

    env_vars: Dict[str, str] = {}
    login_instructions: Optional[str] = Field(
        default=None, description="Optional prompt on how to log in."
    )
    navigation_instructions: Optional[str] = Field(
        default=None, description="Optional additional navigational instructions after login."
    )
    
    def load_from_env(self):
        """Populate config fields from mapped environment variables (case-insensitive)."""
        env_lower_map = {k.lower(): v for k, v in os.environ.items()}
        for env_var, attr_name in self.env_vars.items():
            value = os.getenv(env_var)
            if value is None:
                value = env_lower_map.get(env_var.lower())
            if value is not None:
                setattr(self, attr_name, value)
    
    def set_env_var_values(self, values: Dict[str, str]):
        """Set multiple configuration values at once."""
        if not values:
            return
        lookup_map = {}
        for env_var, attr_name in self.env_vars.items():
            lookup_map[env_var.lower()] = attr_name
            lookup_map[attr_name.lower()] = attr_name

        for key, value in values.items():
            attr_name = lookup_map.get(key.lower())
            if attr_name:
                setattr(self, attr_name, value)


class BasicAuth(BaseAuthConfig):
    """Configuration for HTTP Basic Authentication."""
    auth_type: Literal["basic"] = Field(
        "basic", description="Discriminator for basic auth."
    )
    username: str
    password: SecretStr
    env_vars: Dict[str, str] = {
        "WEB_PROVIDER_USERNAME": "username",
        "WEB_PROVIDER_PASSWORD": "password",
    }

class UsernamePasswordAuth(BaseAuthConfig):
    """
    Configuration for simple username/password authentication, often used in form data or JSON bodies.
    This is distinct from HTTP Basic Auth header.
    """
    auth_type: Literal["username_password"] = Field(
        "username_password", description="Discriminator for username/password auth."
    )
    username: str
    password: SecretStr
    env_vars: Dict[str, str] = {
        "WEB_PROVIDER_USERNAME": "username",
        "WEB_PROVIDER_PASSWORD": "password",
    }

class BearerTokenAuth(BaseAuthConfig):
    """Configuration for Bearer Token Authentication (e.g., API Keys, JWT)."""
    auth_type: Literal["bearer"] = Field(
        "bearer", description="Discriminator for bearer token auth."
    )
    token: SecretStr
    env_vars: Dict[str, str] = {
        "WEB_PROVIDER_TOKEN": "token",
    }

class OAuth2ClientCredentialsAuth(BaseAuthConfig):
    """Configuration for OAuth2 Client Credentials Flow."""
    auth_type: Literal["oauth2_client_credentials"] = Field(
        "oauth2_client_credentials", description="Discriminator for OAuth2 client credentials auth."
    )
    token_url: str = Field(..., description="The URL to fetch the OAuth2 token from.")
    client_id: str
    client_secret: SecretStr
    scope: Optional[str] = Field(None, description="Optional scope for the token request.")
    env_vars: Dict[str, str] = {
        "OAUTH_TOKEN_URL": "token_url",
        "OAUTH_CLIENT_ID": "client_id",
        "OAUTH_CLIENT_SECRET": "client_secret",
        "OAUTH_SCOPE": "scope",
    }

    @field_validator("token_url")
    @classmethod
    def validate_and_normalize_token_url(cls, v: str) -> str:
        """Validate the token_url and normalize it."""
        try:
            # Use HttpUrl for validation and normalization, then cast back to string.
            return str(HttpUrl(v))
        except Exception as e:
            raise ValueError(f"Invalid token URL: {v}") from e

# The discriminated union of all possible authentication types.
Auth = Union[BasicAuth, UsernamePasswordAuth, BearerTokenAuth, OAuth2ClientCredentialsAuth]


# --- PARAMETER AND BASE CONFIGURATION ---

class WebProviderParams(BaseModel):
    """Optional parameters for fine-tuning web provider and crawling behavior."""
    timeout_seconds: Optional[int] = Field(
        default=30, ge=1, description="Timeout for network requests in seconds."
    )
    max_retries: Optional[int] = Field(
        default=0, ge=0, description="Maximum number of retries for failed requests."
    )
    delay_between_requests_seconds: Optional[float] = Field(
        default=0, ge=0, description="Polite delay between consecutive requests to the same endpoint."
    )
    allow_redirects: Optional[bool] = Field(
        default=True, description="Whether to follow HTTP redirects."
    )
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Custom HTTP headers to send with each request (e.g., User-Agent)."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional, provider-specific parameters for the request body or query string.",
    )


class BaseWebProviderConfig(BaseModel):
    """Base configuration for web providers."""
    model_config = ConfigDict(validate_assignment=True)

    endpoint: str = Field(
        description="Base URL of the server or proxy endpoint.",
    )
    env_vars: Dict[str, str] = {
        "WEB_PROVIDER_ENDPOINT": "endpoint",
    }

    @field_validator("endpoint")
    @classmethod
    def validate_and_normalize_endpoint(cls, v: str) -> str:
        """Validate the endpoint URL and normalize it."""
        try:
            # Use HttpUrl for validation and normalization, then cast back to string.
            return str(HttpUrl(v))
        except Exception as e:
            raise ValueError(f"Invalid endpoint URL: {v}") from e

    def load_from_env(self):
        """Populate config fields from mapped environment variables (case-insensitive)."""
        env_lower_map = {k.lower(): v for k, v in os.environ.items()}
        for env_var, attr_name in self.env_vars.items():
            value = os.getenv(env_var)
            if value is None:
                value = env_lower_map.get(env_var.lower())
            if value is not None:
                setattr(self, attr_name, value)

    def get_env_keys(self) -> Dict[str, str]:
        """Return a dictionary of environment variables and their corresponding values."""
        return {env_var: getattr(self, attr_name, None) for env_var, attr_name in self.env_vars.items()}

    def set_env_var_values(self, values: Dict[str, str]):
        """Set multiple configuration values at once."""
        if not values:
            return
        lookup_map = {}
        for env_var, attr_name in self.env_vars.items():
            lookup_map[env_var.lower()] = attr_name
            lookup_map[attr_name.lower()] = attr_name

        for key, value in values.items():
            attr_name = lookup_map.get(key.lower())
            if attr_name:
                setattr(self, attr_name, value)


# --- WEB PROVIDER IMPLEMENTATION ---

class WebProviderConfig(BaseWebProviderConfig):
    """Configuration specific to a generic Web Provider."""
    type: Literal["web"] = Field(
        "web", description="Provider type discriminator."
    )
    
    auth: Optional[Auth] = Field(
        default=None,
        discriminator="auth_type",
        description="Authentication method for the endpoint."
    )
    
    params: WebProviderParams = Field(
        default_factory=WebProviderParams,
        description="Optional parameters for the web provider."
    )

    def get_name(self) -> str:
        """
        Returns a descriptive name for the provider based on its endpoint.
        """
        return f"Web Provider ({self.endpoint})"

    def load_from_env(self):
        """Overrides base method to also load auth credentials from environment."""
        super().load_from_env()
        if self.auth:
            self.auth.load_from_env()

    def get_env_keys(self) -> Dict[str, str]:
        """
        Return a combined dictionary of environment variables and their values
        from the main provider and the authentication model.
        """
        keys = super().get_env_keys()
        if self.auth:
            auth_keys = {
                env_var: getattr(self.auth, attr_name, None)
                for env_var, attr_name in self.auth.env_vars.items()
            }
            keys.update(auth_keys)
        return keys

    def set_env_var_values(self, values: Dict[str, str]):
        """
        Set multiple configuration values at once, delegating to the auth model as needed.
        """
        super().set_env_var_values(values)
        if self.auth:
            self.auth.set_env_var_values(values)


class WebProvider(BaseModel):
    """Top-level wrapper for the Web provider configuration."""
    provider: Literal["web"] = Field(
        "web", description="Provider ID, always set to 'web'."
    )
    config: WebProviderConfig


# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Example 1: Configuration with Basic Auth from a dictionary
    print("--- Example 1: Basic Auth ---")
    basic_auth_data = {
        "provider": "web",
        "config": {
            "endpoint": "https://api.example.com/v1/data",
            "auth": {
                "auth_type": "basic",
                "username": "testuser",
                "password": "testpassword123",
                "login_instructions": "Enter the credentials at the HTTP Basic Auth prompt."
            }
        }
    }
    try:
        web_provider_basic = WebProvider.model_validate(basic_auth_data)
        print("Validation successful!")
        print(f"Name: {web_provider_basic.config.get_name()}")
        print(f"Normalized Endpoint: {web_provider_basic.config.endpoint}")
        print(f"Auth Type: {web_provider_basic.config.auth.auth_type}")
        print(f"Username: {web_provider_basic.config.auth.username}")
        # Note: SecretStr hides the value in print statements
        print(f"Password: {web_provider_basic.config.auth.password}") 
        print(f"Revealed Password: {web_provider_basic.config.auth.password.get_secret_value()}")
        print(f"Login Instructions: {web_provider_basic.config.auth.login_instructions}")
        print("\nSerialized JSON:")
        print(web_provider_basic.model_dump_json(indent=2))

    except Exception as e:
        print(f"Validation failed: {e}")

    # Example 2: Bearer Token auth loaded from environment variables
    print("\n--- Example 2: Bearer Token from Environment ---")
    os.environ["WEB_PROVIDER_TOKEN"] = "secret-api-key-from-env"
    
    bearer_auth_data = {
        "provider": "web",
        "config": {
            "endpoint": "https://api.another-service.io/process",
            "auth": {
                "auth_type": "bearer",
                "token": "this-will-be-overwritten" 
            }
        }
    }
    web_provider_bearer = WebProvider.model_validate(bearer_auth_data)
    # Load credentials from environment
    web_provider_bearer.config.load_from_env()
    
    print(f"Auth Token: {web_provider_bearer.config.auth.token.get_secret_value()}")

    # Example 3: No authentication
    print("\n--- Example 3: No Authentication ---")
    no_auth_data = {
         "provider": "web",
         "config": {
             "endpoint": "https://public-api.net/status"
         }
    }
    web_provider_no_auth = WebProvider.model_validate(no_auth_data)
    print("Validation successful!")
    print(f"Name: {web_provider_no_auth.config.get_name()}")
    print(f"Auth: {web_provider_no_auth.config.auth}")

