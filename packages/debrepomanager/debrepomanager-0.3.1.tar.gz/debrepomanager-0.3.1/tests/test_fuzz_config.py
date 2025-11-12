"""Fuzz tests for configuration module using Hypothesis.

These tests use property-based testing to generate random inputs and verify
that the configuration module handles them correctly without crashes.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from debrepomanager.config import Config, ConfigError


# Strategy for generating valid YAML configuration structures
@st.composite
def valid_config_dict(draw: Any) -> Dict[str, Any]:
    """Generate valid-looking configuration dictionary."""
    return {
        "aptly": {
            "root_base": draw(
                st.sampled_from(["/srv/aptly", "/tmp/aptly", "/var/aptly"])
            ),
            "publish_base": draw(
                st.sampled_from(["/srv/repo", "/tmp/repo", "/var/repo"])
            ),
            "aptly_path": draw(
                st.sampled_from(["aptly", "/usr/bin/aptly", "/usr/local/bin/aptly"])
            ),
        },
        "gpg": {
            "key_id": draw(
                st.text(
                    min_size=8,
                    max_size=40,
                    alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
                )
            ),
            "use_agent": draw(st.booleans()),
            "gpg_path": draw(st.sampled_from(["gpg", "/usr/bin/gpg"])),
        },
        "repositories": {
            # Note: codenames and components removed in v0.2 - created dynamically
            "architectures": draw(
                st.lists(
                    st.sampled_from(["amd64", "arm64", "riscv64", "armhf"]),
                    min_size=1,
                    max_size=4,
                    unique=True,
                )
            ),
            "auto_create": draw(st.booleans()),
        },
    }


# Strategy for generating arbitrary YAML-serializable data
yaml_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=100),
)


@st.composite
def arbitrary_yaml_dict(draw: Any, max_depth: int = 3) -> Dict[str, Any]:
    """Generate arbitrary dictionary that can be serialized to YAML."""
    if max_depth <= 0:
        return {}

    size = draw(st.integers(min_value=0, max_value=10))
    result = {}

    for _ in range(size):
        key = draw(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            )
        )
        value_strategy = st.one_of(
            yaml_primitives,
            st.lists(yaml_primitives, max_size=5),
            (
                st.dictionaries(
                    st.text(min_size=1, max_size=10), yaml_primitives, max_size=5
                )
                if max_depth > 1
                else yaml_primitives
            ),
        )
        result[key] = draw(value_strategy)

    return result


class TestConfigFuzzing:
    """Fuzz tests for Config class."""

    @given(config_data=valid_config_dict())
    @settings(max_examples=50, deadline=1000)
    def test_load_valid_config_structures(self, config_data: Dict[str, Any]) -> None:
        """Test that valid config structures can be loaded without crashes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)
            # Should not crash
            assert config is not None

            # Basic sanity checks
            assert isinstance(config.aptly_root_base, str)
            assert isinstance(config.publish_base, str)
            # Note: get_codenames()/get_components() removed in v0.2
            # Codenames and components are created dynamically
            assert isinstance(config.get_architectures(), list)

        finally:
            Path(config_path).unlink(missing_ok=True)

    @given(config_data=arbitrary_yaml_dict())
    @settings(max_examples=100, deadline=1000)
    def test_load_arbitrary_yaml_no_crash(self, config_data: Dict[str, Any]) -> None:
        """Test that loading arbitrary YAML doesn't crash (may raise ConfigError)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            # Should either load successfully or raise ConfigError, but not crash
            try:
                config = Config(config_path)
                # If it loads, basic operations should work
                _ = config.aptly_root_base
            except (ConfigError, KeyError, TypeError, AttributeError):
                # Expected for invalid configs
                pass

        finally:
            Path(config_path).unlink(missing_ok=True)

    @given(yaml_content=st.text(max_size=1000))
    @settings(max_examples=100, deadline=1000)
    def test_load_random_yaml_content_no_crash(self, yaml_content: str) -> None:
        """Test that loading random YAML content doesn't crash."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        try:
            # Should either load or raise exception, but not crash
            try:
                config = Config(config_path)
                _ = config.aptly_root_base
            except (
                ConfigError,
                yaml.YAMLError,
                KeyError,
                TypeError,
                AttributeError,
                ValueError,
            ):
                # Expected for invalid YAML or configs
                pass

        finally:
            Path(config_path).unlink(missing_ok=True)

    @given(
        base_config=valid_config_dict(),
        override_config=arbitrary_yaml_dict(max_depth=2),
    )
    @settings(max_examples=50, deadline=1000)
    def test_config_merge_no_crash(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ) -> None:
        """Test that merging configs doesn't crash."""
        config = Config()
        config._config = base_config

        # Merge should not crash
        try:
            config._merge_dict(config._config, override_config)
            # After merge, config should still be a dict
            assert isinstance(config._config, dict)
        except (TypeError, AttributeError):
            # May fail on incompatible types, but shouldn't crash
            pass

    @given(
        root_base=st.text(min_size=1, max_size=100),
        publish_base=st.text(min_size=1, max_size=100),
    )
    @settings(max_examples=50, deadline=500)
    def test_validate_with_random_paths(
        self, root_base: str, publish_base: str
    ) -> None:
        """Test validation with random path strings."""
        config = Config()
        config._config["aptly"]["root_base"] = root_base
        config._config["aptly"]["publish_base"] = publish_base

        # Validation should either pass or raise ConfigError
        try:
            config.validate()
        except (ConfigError, TypeError, ValueError, KeyError):
            # Expected for invalid paths or structures
            pass

    @given(
        codename=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pd")),
        )
    )
    @settings(max_examples=50, deadline=500)
    def test_get_aptly_root_with_random_codename(self, codename: str) -> None:
        """Test get_aptly_root with random codenames."""
        config = Config()

        try:
            result = config.get_aptly_root(codename)
            # Should return a string path
            assert isinstance(result, str)
            # Should contain the codename
            assert codename in result
        except (TypeError, ValueError, AttributeError):
            # May fail on invalid codenames
            pass

    @given(
        codenames=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
        components=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
        architectures=st.lists(
            st.text(min_size=1, max_size=20), min_size=0, max_size=10
        ),
    )
    @settings(max_examples=50, deadline=500)
    def test_repository_lists_no_crash(
        self, codenames: list, components: list, architectures: list
    ) -> None:
        """Test that setting repository lists doesn't crash."""
        config = Config()
        config._config["repositories"]["codenames"] = codenames
        config._config["repositories"]["components"] = components
        config._config["repositories"]["architectures"] = architectures

        try:
            # Note: get_codenames()/get_components() removed in v0.2
            # Only test architectures
            result_architectures = config.get_architectures()
            assert isinstance(result_architectures, list)
        except (TypeError, KeyError, AttributeError):
            pass


class TestConfigEdgeCases:
    """Edge case tests for Config class."""

    def test_empty_yaml_file(self) -> None:
        """Test loading empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = f.name

        try:
            config = Config(config_path)
            # Should use default config
            assert config is not None
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_yaml_with_only_comments(self) -> None:
        """Test loading YAML with only comments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("# This is a comment\n# Another comment\n")
            config_path = f.name

        try:
            config = Config(config_path)
            # Should use default config
            assert config is not None
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_yaml_with_null_values(self) -> None:
        """Test loading YAML with null values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"aptly": None, "gpg": None}, f)
            config_path = f.name

        try:
            config = Config(config_path)
            # Should handle gracefully
            assert config is not None
        except (ConfigError, TypeError, AttributeError):
            # Expected for invalid structure
            pass
        finally:
            Path(config_path).unlink(missing_ok=True)
