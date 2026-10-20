import threading
import unittest
import urllib.error
import urllib.request

from agent_lab.compare_interfaces import call_direct_api
from agent_lab.http_api import make_server
from agent_lab.tools import compare_sla


class DirectAPIExamples(unittest.TestCase):
    def test_direct_api_uses_same_calculation(self):
        server = make_server()
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            url = "http://127.0.0.1:" + str(server.server_port)
            self.assertEqual(call_direct_api(url), compare_sla())
            bad = urllib.request.Request(url + "/tools/unknown", data=b"{}", method="POST")
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(bad, timeout=2)
            self.assertEqual(caught.exception.code, 404)
            caught.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
