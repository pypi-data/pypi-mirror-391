import json
import uuid

from vaxbnana import XrayConfig, V2Data


def test_xray_chaining():
    detour_config = V2Data(
        "vmess",
        "detour_outbound",
        "127.0.0.1",
        1234,
        uuid=uuid.UUID("bb34fc3a-529d-473a-a3d9-1749b2116f2a"),
    )
    main_config = V2Data(
        "vmess",
        "main_outbound",
        "127.0.0.1",
        1234,
        uuid=uuid.UUID("bb34fc3a-529d-473a-a3d9-1749b2116f2a"),
        next=detour_config,
    )
    x = XrayConfig()
    x.add_proxies([main_config])
    result = json.loads(x.render())

    main_outbound = None
    for outbound in result[0]["outbounds"]:
        if outbound["tag"] == "main_outbound":
            main_outbound = outbound
            break
    assert (
        main_outbound["streamSettings"]["sockopt"]["dialerProxy"] == "detour_outbound"
    )


def test_tcp_http_headers_with_none_type():
    """
    Test that TCP headers are included even when header_type is 'none'.

    This is an expected behavior where HTTP headers should be present
    in the request section regardless of header_type value.
    """
    # Test case 1: header_type="none" with headers should include request
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
    }
    result = XrayConfig.tcp_http_config(header_type="none", headers=headers)

    assert result["header"]["type"] == "none"
    assert (
        "request" in result["header"]
    ), "Request section should be present even with header_type='none' when headers are provided"
    assert "headers" in result["header"]["request"]
    assert result["header"]["request"]["headers"]["Accept-Encoding"] == [
        "gzip, deflate"
    ]
    assert result["header"]["request"]["headers"]["Connection"] == ["keep-alive"]
    assert result["header"]["request"]["headers"]["Pragma"] == ["no-cache"]

    # Test case 2: header_type="none" without headers should not include request
    result_no_headers = XrayConfig.tcp_http_config(header_type="none")
    assert result_no_headers["header"]["type"] == "none"
    assert (
        "request" not in result_no_headers["header"]
    ), "Request section should not be present when no headers are provided"


def test_tcp_http_config_integration():
    """
    Test full integration: VLESS with TCP transport and HTTP headers.
    """
    config = V2Data(
        protocol="vless",
        remark="TCP",
        address="62.60.247.98",
        port=8080,
        uuid=uuid.UUID("154c2ccf-5cad-5f6b-014d-fb6e74912e7f"),
        transport_type="tcp",
        header_type="none",
        http_headers={
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        },
    )

    x = XrayConfig()
    x.add_proxies([config])
    result = json.loads(x.render())

    # Find the proxy outbound
    proxy_outbound = None
    for outbound in result[0]["outbounds"]:
        if outbound["tag"] == "TCP":
            proxy_outbound = outbound
            break

    assert proxy_outbound is not None, "TCP outbound should exist"
    assert "streamSettings" in proxy_outbound
    assert "tcpSettings" in proxy_outbound["streamSettings"]

    tcp_settings = proxy_outbound["streamSettings"]["tcpSettings"]
    assert tcp_settings["header"]["type"] == "none"
    assert (
        "request" in tcp_settings["header"]
    ), "Request should be present with HTTP headers"
    assert "headers" in tcp_settings["header"]["request"]

    # Verify headers are properly formatted
    request_headers = tcp_settings["header"]["request"]["headers"]
    assert "Accept-Encoding" in request_headers
    assert "Connection" in request_headers
    assert "Pragma" in request_headers
    assert "Cache-Control" in request_headers
