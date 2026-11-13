"""Noetfield Connect -> existing Company OS read-only source-key contract."""
import json
from unittest.mock import patch

from noetfield_governance.company_os_connect_readback import readback


class Response:
    status=200
    def __init__(self,body):
        self.body=body
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,cap):return json.dumps(self.body).encode("utf-8")


def test_valid_ack_and_no_external_action_assertion():
    intake_id="INT-ABCDEF123456"
    body={"source":"existing_company_os_core","found":True,
          "source_intake_id":intake_id,"signal_state":"tasks_created",
          "task_count":1,"tasks":[{"task_id":"task_001","role":"partnerships",
                                    "status":"queued"}],"run_count":0,"runs":[],
          "independent_receipts_verified":False,"external_effects_verified":False}
    with patch.dict("os.environ",{"CONNECT_BUSINESS_OS_READ_TOKEN":"x"*48,
                                   "CONNECT_BUSINESS_OS_READ_URL":"https://core.example.org"}):
        with patch("noetfield_governance.company_os_connect_readback.urlopen",
                   return_value=Response(body)) as req:
            result=readback(intake_id)
    assert result["connected"] is True
    assert result["task_count"]==1
    assert result["independent_receipts_verified"] is False
    request=req.call_args.args[0]
    assert request.get_method()=="GET"
    assert request.get_header("X-noetfield-connect-read-token")=="x"*48
    assert request.data is None
    assert request.full_url.endswith(intake_id)


def test_bad_or_unconfigured_config_fails_closed():
    intake_id="INT-ABCDEF123456"
    with patch.dict("os.environ",{"CONNECT_BUSINESS_OS_READ_TOKEN":"",
                                   "CONNECT_BUSINESS_OS_READ_URL":""}):
        with patch("noetfield_governance.company_os_connect_readback.urlopen") as req:
            result=readback(intake_id)
            req.assert_not_called()
    assert result["connected"] is False
    assert result["error"]=="COMPANY_OS_READ_NOT_CONFIGURED"
    assert readback("WRONG-ID")["connected"] is False


def test_untrusted_ack_is_not_reported_connected():
    with patch.dict("os.environ",{"CONNECT_BUSINESS_OS_READ_TOKEN":"x"*48,
                                   "CONNECT_BUSINESS_OS_READ_URL":"https://core.example.org"}):
        with patch("noetfield_governance.company_os_connect_readback.urlopen",
                   return_value=Response({"found":True,"source_intake_id":"INT-OTHER111111",
                                          "source":"existing_company_os_core"})):
            result=readback("INT-ABCDEF123456")
    assert result["connected"] is False
    assert result["error"]=="UNTRUSTED_UPSTREAM_ACK"
