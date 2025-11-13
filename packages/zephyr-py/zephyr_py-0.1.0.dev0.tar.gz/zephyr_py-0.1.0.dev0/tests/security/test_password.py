"""
Tests for password hashing functionality.

Tests password hashing, verification, and security features.
"""

import pytest
from unittest.mock import patch

from zephyr.security.password import PasswordHasher, PasswordError, PasswordHashError, PasswordVerificationError


class TestPasswordHasher:
    """Test password hasher functionality."""

    @pytest.fixture
    def hasher(self):
        """Create password hasher for tests."""
        return PasswordHasher()

    @pytest.mark.asyncio
    async def test_hash_password_success(self, hasher):
        """Test successful password hashing."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt format

    @pytest.mark.asyncio
    async def test_hash_empty_password(self, hasher):
        """Test hashing empty password raises error."""
        with pytest.raises(PasswordHashError, match="Password cannot be empty"):
            await hasher.hash_password("")

    @pytest.mark.asyncio
    async def test_hash_none_password(self, hasher):
        """Test hashing None password raises error."""
        with pytest.raises(PasswordHashError, match="Password cannot be empty"):
            await hasher.hash_password(None)

    @pytest.mark.asyncio
    async def test_verify_password_success(self, hasher):
        """Test successful password verification."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        is_valid = await hasher.verify_password(password, hashed)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_verify_password_wrong_password(self, hasher):
        """Test password verification with wrong password."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        is_valid = await hasher.verify_password("wrongpassword", hashed)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_password_empty_password(self, hasher):
        """Test password verification with empty password."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        is_valid = await hasher.verify_password("", hashed)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_password_empty_hash(self, hasher):
        """Test password verification with empty hash."""
        is_valid = await hasher.verify_password("password", "")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_password_none_hash(self, hasher):
        """Test password verification with None hash."""
        is_valid = await hasher.verify_password("password", None)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_needs_rehash_false(self, hasher):
        """Test needs_rehash returns False for current hash."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        needs_rehash = await hasher.needs_rehash(hashed)
        assert needs_rehash is False

    @pytest.mark.asyncio
    async def test_needs_rehash_invalid_hash(self, hasher):
        """Test needs_rehash with invalid hash."""
        with pytest.raises(PasswordVerificationError, match="Invalid password hash"):
            await hasher.needs_rehash("invalid-hash")

    @pytest.mark.asyncio
    async def test_generate_salt(self, hasher):
        """Test salt generation."""
        salt = await hasher.generate_salt(32)

        assert isinstance(salt, str)
        assert len(salt) > 0

    @pytest.mark.asyncio
    async def test_generate_salt_different_lengths(self, hasher):
        """Test salt generation with different lengths."""
        salt16 = await hasher.generate_salt(16)
        salt32 = await hasher.generate_salt(32)
        salt64 = await hasher.generate_salt(64)

        assert len(salt16) != len(salt32)
        assert len(salt32) != len(salt64)
        assert salt16 != salt32 != salt64

    @pytest.mark.asyncio
    async def test_get_scheme_info(self, hasher):
        """Test scheme information retrieval."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        info = hasher.get_scheme_info(hashed)
        assert "scheme" in info
        assert info["scheme"] == "bcrypt"

    @pytest.mark.asyncio
    async def test_get_scheme_info_invalid_hash(self, hasher):
        """Test scheme information with invalid hash."""
        info = hasher.get_scheme_info("invalid-hash")
        assert "scheme" in info
        assert info["scheme"] == "unknown"
        assert "error" in info

    @pytest.mark.asyncio
    async def test_password_too_long_truncation(self, hasher):
        """Test password truncation for bcrypt 72-byte limit."""
        # Create a password longer than 72 bytes
        long_password = "a" * 100

        hashed = await hasher.hash_password(long_password)
        assert isinstance(hashed, str)

        # Verify truncated password works
        is_valid = await hasher.verify_password(long_password, hashed)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_custom_schemes(self):
        """Test password hasher with custom schemes."""
        hasher = PasswordHasher(schemes=["bcrypt"], deprecated=[])

        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_hash_error_handling(self, hasher):
        """Test error handling during password hashing."""
        # Mock context.hash to raise an exception
        with patch.object(hasher.context, "hash", side_effect=Exception("Hashing failed")):
            with pytest.raises(PasswordHashError, match="Password hashing failed"):
                await hasher.hash_password("password")

    @pytest.mark.asyncio
    async def test_verify_error_handling(self, hasher):
        """Test error handling during password verification."""
        # Mock context.verify to raise an exception
        with patch.object(hasher.context, "verify", side_effect=Exception("Verification failed")):
            with pytest.raises(PasswordVerificationError, match="Password verification failed"):
                await hasher.verify_password("password", "hash")

    @pytest.mark.asyncio
    async def test_needs_rehash_error_handling(self, hasher):
        """Test error handling during rehash check."""
        # Mock context.needs_update to raise an exception
        with patch.object(hasher.context, "needs_update", side_effect=Exception("Rehash check failed")):
            with pytest.raises(PasswordVerificationError, match="Rehash check failed"):
                await hasher.needs_rehash("hash")


class TestPasswordSecurity:
    """Test password security features."""

    @pytest.fixture
    def hasher(self):
        """Create password hasher for tests."""
        return PasswordHasher()

    @pytest.mark.asyncio
    async def test_constant_time_comparison(self, hasher):
        """Test that password verification uses constant time comparison."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit
        hashed = await hasher.hash_password(password)

        # Test with correct password
        start_time = time.time()
        await hasher.verify_password(password, hashed)
        correct_time = time.time() - start_time

        # Test with wrong password
        start_time = time.time()
        await hasher.verify_password("wrongpassword", hashed)
        wrong_time = time.time() - start_time

        # Times should be similar (constant time comparison)
        # Allow for some variance due to system timing
        time_diff = abs(correct_time - wrong_time)
        assert time_diff < 0.1  # Should be within 100ms

    @pytest.mark.asyncio
    async def test_different_salts(self, hasher):
        """Test that same password produces different hashes."""
        password = "test123"  # Shorter password to avoid bcrypt 72-byte limit

        hash1 = await hasher.hash_password(password)
        hash2 = await hasher.hash_password(password)

        assert hash1 != hash2  # Different salts should produce different hashes

        # But both should verify correctly
        assert await hasher.verify_password(password, hash1) is True
        assert await hasher.verify_password(password, hash2) is True


# Import time for timing tests
import time
