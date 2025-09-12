from unittest import TestCase, mock
from utils.proxies import get_proxys


class TestProxies(TestCase):
    @mock.patch("keyring.get_password")
    def test_get_proxys_return_correct_format(self, mock_get_password):
        mock_get_password.return_value = "secret"
        proxies = get_proxys(file_path="mock_proxies.txt")

        self.assertEqual(
            ["socks5h://secret:secret@proxy1.nl:1080", "socks5h://secret:secret@proxy2.nl:1080"],
            proxies
        )



