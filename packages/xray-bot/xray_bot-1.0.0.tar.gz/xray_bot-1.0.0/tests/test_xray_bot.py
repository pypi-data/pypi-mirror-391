import pytest
import requests
from xraybot import XrayBot, TestEntity, TestResultEntity, XrayResultType
local_draft_tests = [
    TestEntity(
        key=None,
        summary='["foo"]foo1 it\'s foo',
        description="""
        "foo"
        ///.g.e.g []*&)&^
        """,
        repo_path=["foo", "2nd folder", "inner"],
        unique_identifier="tests.function.foo1",
    )
]
local_tests = [
    TestEntity(
        key="XT-6353",
        summary='["foo"]foo1 \.\it\'s foo',
        description="""
        "foo"
        ///.g.e.g []*&)&^
        """,
        repo_path=["foo", "2nd folder", "inner"],
        unique_identifier="tests.function.foo1",
    ),
    TestEntity(
        key="XT-6354",
        summary="foo2",
        description="desc",
        repo_path=["foo", "2nd folder"],
        unique_identifier="tests.function.foo2",
        labels=["foo", "bar"],
        req_keys=["XT-5380", "XT-5457"],
        defect_keys=["XT-6339", "XT-6338"]
    ),
    TestEntity(
        key="XT-6355",
        summary="foo3",
        description="desc",
        repo_path=["bar"],
        unique_identifier="tests.function.foo3",
        labels=["foo"],
        req_keys=["XT-5380"],
        defect_keys=["XT-6339"]
    ),
    TestEntity(
        key="XT-5791",
        summary="foo4",
        description="desc",
        repo_path=["bar"],
        unique_identifier="tests.function.foo4",
        labels=["bar"],
        req_keys=["XT-5380"]
    ),
    TestEntity(
        key="XT-6205",
        summary="foo5",
        description="desc",
        unique_identifier="tests.function.foo5",
        labels=["bar"],
        req_keys=["XT-5380"]
    )
]
test_results = [
    TestResultEntity(
        key="XT-6353",
        result=XrayResultType.FAILED
    ),
    TestResultEntity(
        key="XT-6205",
        result=XrayResultType.PASSED
    )
]
class TestXrayBot:
    @pytest.fixture(scope="class")
    def bot(self) -> XrayBot:
        client_id = "D52D10B068C14F6A8ACBB24BCC15CDA4"
        client_secret = "22ecad281fa69173f3328f220ed4ca03b4a49194cf2940334055c5bbb51a5806"
        r = requests.post("https://xray.cloud.getxray.app/api/v2/authenticate", json={
            "client_id": client_id,
            "client_secret": client_secret
        })
        token = r.json()
        bot = XrayBot(
            jira_url="https://telenav.atlassian.net",
            jira_username="svcqauser01@telenav.com",
            jira_pwd="ATATT3xFfGF0pe828m5YLY5yg5NU5iQq4kGDrfFzjOuWFGTXf-7yBm6C9zQM_BCEHvXUXIJ4Gi4MKKQH850bx7CzeGJ0kvhJrdCokESsjmfW1lxStdAjCIfMBgWtpq9mKpNebGRJF6ydGyQFkCQgS4cYo_C6C15bI81mO3B3yBeDTxdZTFzfmdo=4E80225E",
            jira_account_id="5dd2b03ab6b3230eefb767df",
            project_key="XT",
            xray_api_token=token,
        )
        bot.config.configure_automation_folder_name("My Automation Test Folder")
        return bot

    def test_create_tests_draft(self, bot: XrayBot):
        bot.create_tests_draft(local_draft_tests)

    def test_sync_tests(self, bot: XrayBot):
        bot.sync_tests(local_tests)

    def test_get_xray_tests(self, bot: XrayBot):
        results = bot.get_xray_tests()
        assert results

    def test_sync_check(self, bot: XrayBot):
        bot.sync_check(local_tests)

    def test_upload_test_results(self, bot: XrayBot):
        bot.upload_test_results(
            "my test plan 1019",
            "my test execution 1019",
            test_results,
            ignore_missing=True,
            clean_obsolete=True
        )

    def test_upload_test_results_by_key(self, bot: XrayBot):
        bot.upload_test_results_by_key(
            "XT-6358",
            test_results,
            "XT-6356",
            full_test_set=True,
            clean_obsolete=True,
        )