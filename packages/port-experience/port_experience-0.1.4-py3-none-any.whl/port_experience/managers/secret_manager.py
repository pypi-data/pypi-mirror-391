import os
import json
from typing import Dict
from pathlib import Path

from port_experience.managers import BasePortManager


class PortSecretManager(BasePortManager):
    """Manages Port.io organization secrets creation from .env file."""

    def __init__(self, client_id: str, client_secret: str, port_host: str = "api.port.io"):
        """Initialize the Port Secret Manager."""
        super().__init__(client_id, client_secret, port_host, "PortSecretManager")

    def parse_env_file(self, env_file: str = ".env") -> Dict[str, str]:
        """
        Parse .env file and extract PORT_KEYS entries.

        Args:
            env_file: Path to the .env file

        Returns:
            Dictionary mapping secret names to secret values
        """
        secrets = {}
        env_path = Path(env_file)

        if not env_path.exists():
            self.logger.debug(f".env file not found: {env_file} (this is fine)")
            return secrets

        self.logger.debug(f"Reading .env file: {env_file}")

        try:
            port_keys_str = os.getenv('PORT_KEYS')
            
            if not port_keys_str:
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                json_lines = []
                in_port_keys = False
                brace_count = 0
                
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith('PORT_KEYS='):
                        value_part = line.split('=', 1)[1] if '=' in line else ''
                        json_lines = [value_part]
                        brace_count = value_part.count('{') - value_part.count('}')
                        in_port_keys = True
                        if brace_count == 0:
                            break
                    elif in_port_keys:
                        json_lines.append(line)
                        brace_count += line.count('{') - line.count('}')
                        if brace_count == 0:
                            break
                
                if json_lines:
                    port_keys_str = '\n'.join(json_lines).strip()
            
            if port_keys_str:
                port_keys = json.loads(port_keys_str)
                
                if isinstance(port_keys, dict):
                    for key, value in port_keys.items():
                        if isinstance(value, str):
                            secrets[key] = value
                            self.logger.info(f"Found secret key: {key}")
                        else:
                            self.logger.warning(f"Skipping non-string value for key '{key}'")
                else:
                    self.logger.warning(f"PORT_KEYS value is not a JSON object")

            if not secrets:
                self.logger.debug("No PORT_KEYS entries found in .env file (this is fine)")
            else:
                self.logger.info(f"Found {len(secrets)} secrets to create")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse PORT_KEYS JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error reading .env file: {e}")

        return secrets

    def secret_exists(self, secret_key: str) -> bool:
        """
        Check if a secret exists in Port.

        Args:
            secret_key: Secret key/name

        Returns:
            True if secret exists, False otherwise
        """
        response = self.make_api_request('GET', f'/v1/organization/secrets/{secret_key}', silent_404=True)
        exists = response is not None

        if exists:
            self.logger.info(f"Secret '{secret_key}' found in portal")
        else:
            self.logger.info(f"Secret '{secret_key}' not found in portal - will create it")

        return exists

    def create_secret(self, secret_key: str, secret_value: str) -> bool:
        """
        Create an organization secret in Port.io.

        Args:
            secret_key: Secret key/name
            secret_value: Secret value

        Returns:
            True if successful, False otherwise
        """
        if not secret_key:
            self.logger.error("Secret key is required")
            return False

        self.logger.info(f"Creating secret: {secret_key}")

        secret_data = {
            'secretName': secret_key,
            'secretValue': secret_value
        }

        response = self.make_api_request('POST', '/v1/organization/secrets', secret_data)

        if response:
            self.logger.info(f"Successfully created secret: {secret_key}")
            return True
        else:
            self.logger.error(f"Failed to create secret: {secret_key}")
            return False

    def update_secret(self, secret_key: str, secret_value: str) -> bool:
        """
        Update an existing organization secret in Port.io.

        Args:
            secret_key: Secret key/name
            secret_value: Secret value

        Returns:
            True if successful, False otherwise
        """
        if not secret_key:
            self.logger.error("Secret key is required")
            return False

        self.logger.info(f"Updating secret: {secret_key}")

        secret_data = {
            'secretValue': secret_value
        }

        response = self.make_api_request('PATCH', f'/v1/organization/secrets/{secret_key}', secret_data)

        if response:
            self.logger.info(f"Successfully updated secret: {secret_key}")
            return True
        else:
            self.logger.error(f"Failed to update secret: {secret_key}")
            return False

    def setup_all_secrets(self, env_file: str = ".env", update_existing: bool = True) -> Dict[str, bool]:
        """
        Setup all secrets from the .env file.

        Args:
            env_file: Path to the .env file
            update_existing: If True, update existing secrets; if False, skip them

        Returns:
            Dictionary mapping secret keys to success status
        """
        results = {}

        secrets = self.parse_env_file(env_file)

        if not secrets:
            self.logger.debug("No secrets found to setup (this is fine)")
            return results

        self.logger.info(f"Setting up {len(secrets)} secrets...")

        for secret_key, secret_value in secrets.items():
            exists = self.secret_exists(secret_key)

            if exists and update_existing:
                success = self.update_secret(secret_key, secret_value)
            elif not exists:
                success = self.create_secret(secret_key, secret_value)
            else:
                self.logger.info(f"Skipping existing secret: {secret_key}")
                success = True

            results[secret_key] = success

            if not success:
                self.logger.error(f"Failed to process secret: {secret_key}")

                # Check if we should continue on error
                if not self.should_continue_on_error():
                    self.logger.error("Stopping due to error and continue_on_error is false")
                    break

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        self.logger.info(f"Secret setup complete: {successful}/{total} secrets processed successfully")

        return results

