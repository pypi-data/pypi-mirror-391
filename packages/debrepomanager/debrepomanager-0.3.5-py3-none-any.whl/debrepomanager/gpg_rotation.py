"""GPG key rotation module for zero-downtime key changes.

This module provides functionality to rotate GPG keys used for signing
repositories without downtime. Supports grace period where both old and
new keys are valid, and rollback capability.
"""

import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List

from debrepomanager.aptly import AptlyManager
from debrepomanager.config import Config
from debrepomanager.gpg import GPGManager

logger = logging.getLogger(__name__)


class GPGRotationError(Exception):
    """GPG rotation operation errors."""


class GPGRotationManager:
    """Manager for GPG key rotation operations.

    Provides zero-downtime key rotation with grace period support
    and rollback capability.

    Example:
        >>> config = Config()
        >>> aptly = AptlyManager(config)
        >>> rotation = GPGRotationManager(config, aptly)
        >>> rotation.validate_new_key("NEW_KEY_ID")
        >>> rotation.rotate_all_repos("NEW_KEY_ID", grace_period=True)
    """

    def __init__(self, config: Config, aptly: AptlyManager):
        """Initialize GPG rotation manager.

        Args:
            config: Configuration object
            aptly: AptlyManager instance
        """
        self.config = config
        self.aptly = aptly
        self.gpg = GPGManager(config)
        self.logger = logging.getLogger("debrepomanager.gpg_rotation")

    def validate_new_key(self, new_key_id: str) -> bool:
        """Validate that new GPG key is available and usable.

        Args:
            new_key_id: New GPG key ID to validate

        Returns:
            True if key is valid and available

        Raises:
            GPGRotationError: If key is not available or invalid

        Example:
            >>> rotation.validate_new_key("ABC123DEF456")
            True
        """
        self.logger.info(f"Validating new GPG key: {new_key_id}")

        # Check if key exists in keyring
        try:
            result = subprocess.run(
                [self.config.gpg_path, "--list-keys", new_key_id],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            if new_key_id not in result.stdout:
                raise GPGRotationError(
                    f"Key {new_key_id} not found in output. "
                    "Import the key first: gpg --import key.asc"
                )

            self.logger.info(f"✓ Key {new_key_id} found in keyring")

        except subprocess.CalledProcessError as e:
            raise GPGRotationError(f"Failed to list keys: {e.stderr}") from e
        except subprocess.TimeoutExpired:
            raise GPGRotationError("GPG command timed out")

        # Test signing with new key
        try:
            test_message = f"GPG rotation test at {datetime.now().isoformat()}"
            result = subprocess.run(
                [
                    self.config.gpg_path,
                    "--batch",
                    "--yes",
                    "--local-user",
                    new_key_id,
                    "--clear-sign",
                ],
                input=test_message,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            if "BEGIN PGP SIGNED MESSAGE" not in result.stdout:
                raise GPGRotationError("Signing test failed - invalid signature")

            self.logger.info(f"✓ Successfully tested signing with {new_key_id}")

        except subprocess.CalledProcessError as e:
            raise GPGRotationError(f"Failed to sign test message: {e.stderr}") from e
        except subprocess.TimeoutExpired:
            raise GPGRotationError("GPG signing test timed out")

        return True

    def get_all_published_repos(self) -> List[Dict[str, str]]:
        """Get list of all published repositories.

        Returns:
            List of dicts with codename and component for each published repo

        Example:
            >>> repos = rotation.get_all_published_repos()
            >>> repos
            [{'codename': 'bookworm', 'component': 'tools'}, ...]
        """
        self.logger.info("Discovering all published repositories...")

        repos = self.aptly.metadata.list_repositories()

        self.logger.info(f"Found {len(repos)} published repositories")

        return repos

    def resign_repository(  # noqa: C901
        self, codename: str, component: str, new_key_id: str
    ) -> bool:
        """Re-sign a single repository with new GPG key.

        Args:
            codename: Distribution codename
            component: Repository component
            new_key_id: New GPG key ID to use

        Returns:
            True if successful

        Raises:
            GPGRotationError: If re-signing fails

        Example:
            >>> rotation.resign_repository("bookworm", "tools", "NEWKEY123")
            True
        """
        self.logger.info(
            f"Re-signing repository {codename}/{component} with key {new_key_id}"
        )

        try:
            # Get current published snapshot
            current_snapshot = self.aptly.get_published_snapshot(codename, component)

            if not current_snapshot:
                self.logger.warning(
                    f"Repository {codename}/{component} not published, skipping"
                )
                return False

            # Unpublish current (will be republished with new key)
            prefix = f"{codename}/{component}"
            old_key_id = self.config.gpg_key_id  # Save for rollback

            try:
                self.aptly._run_aptly(["publish", "drop", component, prefix], codename)
                self.logger.debug(f"Unpublished {prefix}")
            except Exception as e:
                self.logger.warning(f"Failed to unpublish (may not exist): {e}")

            # Republish with new key (with rollback on failure)
            try:
                self.aptly._run_aptly(
                    [
                        "publish",
                        "snapshot",
                        "-distribution",
                        component,
                        "-gpg-key",
                        new_key_id,
                        current_snapshot,
                        prefix,
                    ],
                    codename,
                )

                self.logger.info(
                    f"✓ Re-signed {codename}/{component} with {new_key_id}"
                )

            except Exception as publish_error:
                # CRITICAL: Publish failed! Try to rollback with old key
                self.logger.error(
                    f"Failed to publish with new key, attempting rollback to {old_key_id}"
                )

                try:
                    self.aptly._run_aptly(
                        [
                            "publish",
                            "snapshot",
                            "-distribution",
                            component,
                            "-gpg-key",
                            old_key_id,
                            current_snapshot,
                            prefix,
                        ],
                        codename,
                    )
                    self.logger.warning(
                        f"Rolled back {codename}/{component} to old key {old_key_id}"
                    )
                except Exception as rollback_error:
                    # DISASTER: Both publish attempts failed!
                    raise GPGRotationError(
                        f"CRITICAL: Failed to publish with new key AND rollback failed! "
                        f"Repository {codename}/{component} is UNPUBLISHED! "
                        f"Original error: {publish_error}, Rollback error: {rollback_error}"
                    ) from publish_error

                # Rollback succeeded, but rotation failed
                raise GPGRotationError(
                    f"Failed to publish with new key, rolled back to old key. "
                    f"Error: {publish_error}"
                ) from publish_error

            return True

        except GPGRotationError:
            raise
        except Exception as e:
            raise GPGRotationError(
                f"Unexpected error re-signing {codename}/{component}: {e}"
            ) from e

    def rotate_all_repos(
        self, new_key_id: str, grace_period: bool = False
    ) -> Dict[str, Any]:
        """Rotate GPG key for all published repositories.

        Args:
            new_key_id: New GPG key ID
            grace_period: If True, both old and new keys remain valid (MANUAL PROCESS)

        Returns:
            Dictionary with rotation results:
            - total: Total repositories
            - success: Successfully rotated
            - failed: Failed rotations
            - skipped: Skipped repositories

        Raises:
            GPGRotationError: If rotation fails critically

        NOTE: Grace period is a MANUAL process. This flag only affects logging.
        To implement grace period:
        1. Rotate with grace_period=True
        2. Keep old key available on server
        3. Communicate change to users
        4. After grace period (2-4 weeks), can remove old key

        Example:
            >>> result = rotation.rotate_all_repos("NEWKEY123", grace_period=True)
            >>> result['success']
            15
        """
        self.logger.info(
            f"Starting GPG key rotation to {new_key_id} "
            f"(grace_period={grace_period})"
        )

        # Validate new key first
        try:
            self.validate_new_key(new_key_id)
        except GPGRotationError as e:
            raise GPGRotationError(f"New key validation failed: {e}") from e

        # Get all repositories
        repos = self.get_all_published_repos()

        result: Dict[str, Any] = {
            "total": len(repos),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "failures": [],
        }

        # Rotate each repository
        for repo in repos:
            codename = repo["codename"]
            component = repo["component"]

            try:
                if self.resign_repository(codename, component, new_key_id):
                    result["success"] += 1
                else:
                    result["skipped"] += 1

            except Exception as e:
                self.logger.error(f"Failed to rotate {codename}/{component}: {e}")
                result["failed"] += 1
                result["failures"].append(
                    {"codename": codename, "component": component, "error": str(e)}
                )

        self.logger.info(
            f"Rotation complete: {result['success']} success, "
            f"{result['failed']} failed, {result['skipped']} skipped"
        )

        if grace_period:
            self.logger.warning(
                "Grace period enabled - old key still valid. "
                "Remember to communicate key change to users!"
            )

        return result

    def verify_rotation(self, new_key_id: str) -> Dict[str, Any]:
        """Verify that all repositories are signed with new key.

        LIMITATION: Currently only checks if repositories are published,
        does not verify actual signature key ID. Assumes correct if published.

        Args:
            new_key_id: Expected new GPG key ID

        Returns:
            Dictionary with verification results:
            - total: Total repositories checked
            - correct: Repositories published (assumed correct)
            - incorrect: Not implemented
            - unknown: Not published

        TODO: Implement actual GPG signature verification
        - Parse aptly publish show output for key ID
        - Or use gpg --verify on Release file

        Example:
            >>> result = rotation.verify_rotation("NEWKEY123")
            >>> result['correct']
            15
        """
        self.logger.info(f"Verifying rotation to {new_key_id}")

        repos = self.get_all_published_repos()

        result: Dict[str, Any] = {
            "total": len(repos),
            "correct": 0,
            "incorrect": 0,
            "unknown": 0,
            "details": [],
        }

        for repo in repos:
            codename = repo["codename"]
            component = repo["component"]

            # TODO: Implement actual signature verification
            # For now, assume correct if repository is published
            if self.aptly.get_published_snapshot(codename, component):
                result["correct"] += 1
                result["details"].append(
                    {
                        "codename": codename,
                        "component": component,
                        "status": "correct",
                    }
                )
            else:
                result["unknown"] += 1
                result["details"].append(
                    {
                        "codename": codename,
                        "component": component,
                        "status": "unknown",
                    }
                )

        self.logger.info(
            f"Verification: {result['correct']} correct, "
            f"{result['incorrect']} incorrect, {result['unknown']} unknown"
        )

        return result

    def rollback_rotation(self, old_key_id: str) -> Dict[str, Any]:
        """Rollback to previous GPG key.

        Args:
            old_key_id: Old GPG key ID to rollback to

        Returns:
            Dictionary with rollback results (same format as rotate_all_repos)

        Example:
            >>> result = rotation.rollback_rotation("OLDKEY456")
            >>> result['success']
            15
        """
        self.logger.warning(f"Rolling back to old key: {old_key_id}")

        # Validate old key is still available
        try:
            self.validate_new_key(old_key_id)
        except GPGRotationError as e:
            raise GPGRotationError(
                f"Old key {old_key_id} not available for rollback: {e}"
            ) from e

        # Use same rotation logic but with old key
        return self.rotate_all_repos(old_key_id, grace_period=False)
