from mcp_clients.zepto_mcp_client import classify_order_message


def test_order_placed_is_completed() -> None:
    result = classify_order_message(
        "Login successful! Address selected. Item added to cart and order placed with Pay on Delivery."
    )
    assert result == {"success": True, "status": "completed"}


def test_login_otp_is_not_order_success() -> None:
    result = classify_order_message(
        "Order started! OTP sent to 9000000000. Please provide the login OTP."
    )
    assert result["success"] is False
    assert result["status"] == "login_otp_required"
    assert result["requires_otp"] is True


def test_payment_otp_is_not_order_success() -> None:
    result = classify_order_message("Waiting for payment OTP")
    assert result["success"] is False
    assert result["status"] == "payment_otp_required"


def test_error_text_is_failed() -> None:
    result = classify_order_message("Error: Address is required")
    assert result["success"] is False
    assert result["status"] == "failed"

