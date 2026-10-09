import json, sys, tempfile, threading, unittest, urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"workspace"))
import desk

class NativeLedgerExport(unittest.TestCase):
    def test_exact_native_bytes_and_json_state_remain_distinct(self):
        original_root=desk.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            desk.ROOT=Path(tmp)
            ledger=json.loads((Path(__file__).parents[1]/"assets/campaign.template/campaign-ledger.json").read_text(encoding="utf-8"))
            ledger["campaign"].update(id="native-export",title="A quay — returning tonight")
            ledger["next_prep"]=["Ask which boat the players choose"]
            raw=(json.dumps(ledger,ensure_ascii=False,indent=3)+"\r\n").encode("utf-8")
            desk.ledger_path().write_bytes(raw)
            server=desk.ThreadingHTTPServer(("127.0.0.1",0),desk.Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            base="http://127.0.0.1:"+str(server.server_port)
            try:
                with opener.open(base+"/api/export-ledger",timeout=10) as response:
                    self.assertEqual(response.status,200)
                    self.assertEqual(response.headers["Content-Type"],"application/json")
                    self.assertEqual(int(response.headers["Content-Length"]),len(raw))
                    self.assertEqual(response.read(),raw)
                with opener.open(base+"/api/state",timeout=10) as response:
                    state=json.load(response)
                    self.assertEqual(state["ledger"],ledger)
                    self.assertTrue(state["etag"])
                self.assertEqual(desk.ledger_path().read_bytes(),raw)
                self.assertEqual(sorted(p.name for p in desk.ROOT.iterdir()),["campaign-ledger.json"])
            finally:
                server.shutdown();server.server_close();thread.join();desk.ROOT=original_root

if __name__=="__main__":unittest.main()
