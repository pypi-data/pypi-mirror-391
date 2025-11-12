"""GPG operations for Debian Repository Manager.

This module handles GPG key management and signing operations.
"""

import getpass
import logging
import subprocess
from typing import Optional

from debrepomanager.config import Config

logger = logging.getLogger(__name__)


class GPGError(Exception):
    """GPG operation errors."""


class GPGManager:
    """Manager for GPG operations.

    Handles GPG key availability checking, passphrase management,
    and configuration for aptly signing.

    Assumptions:
    - GPG key is already imported in user's keyring
    - If key has passphrase, it will be requested via getpass
    - gpg-agent can cache passphrase if configured

    Attributes:
        config: Configuration object
        logger: Logger instance
        _passphrase_cache: Cached passphrase (optional)

    Example:
        >>> config = Config("config.yaml")
        >>> gpg = GPGManager(config)
        >>> if gpg.check_key_available():
        ...     gpg.test_signing()
    """

    def __init__(self, config: Config):
        """Initialize GPG manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger("debrepomanager.gpg")
        self._passphrase_cache: Optional[str] = None

    def check_key_available(self, key_id: Optional[str] = None) -> bool:
        """Check if GPG key is available in keyring.

        Args:
            key_id: GPG key ID to check. If None, uses config.gpg_key_id

        Returns:
            True if key is available, False otherwise

        Example:
            >>> gpg.check_key_available("1234567890ABCDEF")
            True
        """
        if key_id is None:
            try:
                key_id = self.config.gpg_key_id
            except Exception:
                return False

        try:
            result = subprocess.run(
                [self.config.gpg_path, "--list-secret-keys", key_id],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

            if result.returncode == 0:
                self.logger.debug(f"GPG key {key_id} is available")
                return True
            else:
                self.logger.warning(f"GPG key {key_id} not found in keyring")
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Failed to check GPG key: {e}")
            return False

    def get_passphrase(self, force: bool = False) -> Optional[str]:
        """Get GPG passphrase from user.

        Uses cached passphrase if available, otherwise prompts user.
        If gpg-agent is enabled, passphrase may not be needed.

        Args:
            force: Force prompt even if cached

        Returns:
            Passphrase string or None if using gpg-agent

        Example:
            >>> passphrase = gpg.get_passphrase()
            GPG passphrase: ****
        """
        # If using gpg-agent, passphrase not needed
        if self.config.gpg_use_agent:
            self.logger.debug("Using gpg-agent for passphrase")
            return None

        # Return cached if available and not forcing
        if self._passphrase_cache and not force:
            return self._passphrase_cache

        # Prompt user
        try:
            passphrase = getpass.getpass(
                f"GPG passphrase for key {self.config.gpg_key_id}: "
            )
            self._passphrase_cache = passphrase
            return passphrase
        except (KeyboardInterrupt, EOFError):
            self.logger.warning("Passphrase input cancelled")
            raise GPGError("Passphrase input cancelled")

    def test_signing(self) -> bool:
        """Test if GPG signing works with configured key.

        Creates a test signature to verify GPG key and passphrase work.

        Returns:
            True if signing works

        Raises:
            GPGError: If signing test fails

        Example:
            >>> gpg.test_signing()
            True
        """
        # Check key is available
        if not self.check_key_available():
            raise GPGError(
                f"GPG key {self.config.gpg_key_id} not found in keyring. "
                "Please import the key first."
            )

        try:
            # Create test data to sign
            test_data = b"Test signing\n"

            cmd = [
                self.config.gpg_path,
                "--default-key",
                self.config.gpg_key_id,
                "--armor",
                "--detach-sign",
            ]

            # Add batch mode if using agent
            if self.config.gpg_use_agent:
                cmd.insert(1, "--batch")

            result = subprocess.run(
                cmd,
                input=test_data,
                capture_output=True,
                timeout=30,
                check=True,
            )

            if b"BEGIN PGP SIGNATURE" in result.stdout:
                self.logger.info("GPG signing test successful")
                return True
            else:
                raise GPGError("No signature in output")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"GPG signing test failed: {e.stderr.decode()}")
            raise GPGError(f"GPG signing failed: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise GPGError("GPG signing timed out (passphrase prompt?)")
        except FileNotFoundError:
            raise GPGError(f"GPG binary not found: {self.config.gpg_path}")

    def configure_for_aptly(self) -> dict:
        """Get GPG configuration parameters for aptly.

        Returns:
            Dictionary with aptly GPG parameters

        Example:
            >>> gpg_params = gpg.configure_for_aptly()
            >>> print(gpg_params)
            {'gpg_key': '1234567890ABCDEF', 'gpg_provider': 'gpg'}
        """
        return {
            "gpg_key": self.config.gpg_key_id,
            "gpg_provider": "gpg",
            "skip_signing": False,
        }
