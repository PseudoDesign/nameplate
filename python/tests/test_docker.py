from unittest import TestCase
import docker


class TestDockerSecrets(TestCase):
    NONEXISTENT_SECRET = "fake_secret"

    def test_nonexistent_secret_returns_provided_default_value(self):
        default_value = "dummy"
        self.assertEqual(default_value, docker.secrets.get(self.NONEXISTENT_SECRET, default_value))

    def test_nonexistent_secret_raises_value_error_when_default_value_is_not_provided(self):
        with self.assertRaises(ValueError):
            docker.secrets.get(self.NONEXISTENT_SECRET)
