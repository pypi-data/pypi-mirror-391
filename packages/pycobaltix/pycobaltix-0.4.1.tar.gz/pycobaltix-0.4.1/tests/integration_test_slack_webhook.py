"""
Slack 웹훅 통합 테스트
Integration tests for Slack webhooks

실제 Slack API를 호출하는 통합 테스트입니다.
This integration test makes actual calls to the Slack API.

실행 방법 / How to run:
    # 환경 변수 설정 후 실행 / Run after setting environment variables
    export SLACK_WEBHOOK_URL="your_webhook_url"
    uv run pytest tests/integration_test_slack_webhook.py -v -s

    # 또는 특정 테스트만 실행 / Or run specific tests
    uv run pytest tests/integration_test_slack_webhook.py::test_real_sync_webhook -v -s
"""

import os

import pytest

from pycobaltix.slack import AsyncSlackWebHook, SlackWebHook


@pytest.fixture
def slack_webhook_url():
    """
    Slack 웹훅 URL을 환경 변수에서 가져오는 fixture
    Fixture to get Slack webhook URL from environment variable

    환경 변수가 설정되지 않은 경우 테스트를 건너뜁니다.
    Skip tests if environment variable is not set.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        pytest.skip(
            "SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다. / SLACK_WEBHOOK_URL environment variable is not set."
        )
    return webhook_url


@pytest.mark.integration
@pytest.mark.slow
def test_real_sync_webhook(slack_webhook_url):
    """
    실제 Slack 웹훅으로 동기 메시지 전송 테스트
    Test sending synchronous message with real Slack webhook
    """
    print("\n🔹 동기 SlackWebHook 테스트 시작...")

    webhook = SlackWebHook(webhook_url=slack_webhook_url)

    # 메시지 전송 (예외 발생 시 테스트 실패)
    webhook.send_slack_message(
        title="✅ pycobaltix 통합 테스트",
        content="동기 방식(SlackWebHook)으로 전송된 메시지입니다.",
        detail="실제 Slack API를 호출한 통합 테스트입니다. 🎉",
    )

    print("✅ 동기 메시지 전송 성공!")


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_async_webhook(slack_webhook_url):
    """
    실제 Slack 웹훅으로 비동기 메시지 전송 테스트
    Test sending asynchronous message with real Slack webhook
    """
    print("\n🔹 비동기 AsyncSlackWebHook 테스트 시작...")

    webhook = AsyncSlackWebHook(webhook_url=slack_webhook_url)

    # 비동기 메시지 전송 (예외 발생 시 테스트 실패)
    await webhook.send_slack_message(
        title="✅ pycobaltix 비동기 통합 테스트",
        content="비동기 방식(AsyncSlackWebHook)으로 전송된 메시지입니다.",
        detail="aiohttp를 사용한 실제 비동기 API 호출 테스트입니다. 🚀",
    )

    print("✅ 비동기 메시지 전송 성공!")


@pytest.mark.integration
@pytest.mark.slow
def test_real_sync_webhook_with_title_only(slack_webhook_url):
    """
    제목만 있는 메시지 전송 테스트
    Test sending message with title only
    """
    print("\n🔹 제목만 있는 메시지 테스트...")

    webhook = SlackWebHook(webhook_url=slack_webhook_url)
    webhook.send_slack_message(title="✅ 제목만 있는 테스트")

    print("✅ 제목만 있는 메시지 전송 성공!")


@pytest.mark.integration
@pytest.mark.slow
def test_real_sync_webhook_error_handling(slack_webhook_url):
    """
    잘못된 웹훅 URL로 에러 처리 테스트
    Test error handling with invalid webhook URL
    """
    print("\n🔹 에러 처리 테스트...")

    webhook = SlackWebHook(webhook_url="https://hooks.slack.com/services/INVALID/URL")

    with pytest.raises(ValueError) as exc_info:
        webhook.send_slack_message(title="이 메시지는 전송되지 않습니다")

    assert "웹훅 요청 중 오류 발생" in str(exc_info.value)
    print("✅ 에러 처리 테스트 성공!")


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_async_webhook_with_all_params(slack_webhook_url):
    """
    모든 파라미터를 사용한 비동기 메시지 전송 테스트
    Test sending asynchronous message with all parameters
    """
    print("\n🔹 모든 파라미터 사용 비동기 메시지 테스트...")

    webhook = AsyncSlackWebHook(webhook_url=slack_webhook_url)

    await webhook.send_slack_message(
        title="📝 전체 파라미터 테스트",
        content="이것은 content 파라미터입니다.\n여러 줄로 작성할 수 있습니다.",
        detail="이것은 detail 파라미터입니다. 상세 정보를 표시합니다.",
    )

    print("✅ 모든 파라미터 사용 메시지 전송 성공!")


# 스크립트로 직접 실행 시
if __name__ == "__main__":
    """
    직접 실행 시 사용 방법 안내
    Usage guide when running directly
    """
    import sys

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        print("\n실행 방법:")
        print("  export SLACK_WEBHOOK_URL='your_webhook_url'")
        print("  uv run pytest tests/integration_test_slack_webhook.py -v -s")
        sys.exit(1)

    print("✅ 환경 변수가 설정되었습니다.")
    print("\n테스트 실행:")
    print("  uv run pytest tests/integration_test_slack_webhook.py -v -s")
    print("\n특정 테스트만 실행:")
    print(
        "  uv run pytest tests/integration_test_slack_webhook.py::test_real_sync_webhook -v -s"
    )
