import testapp.settings


def test_csp_default(client):
    response = client.get("/dummy/")

    csp_header = response.headers.get("Content-Security-Policy")

    assert csp_header is not None
    assert "default-src 'self'" in csp_header
    assert "base-uri 'self'" in csp_header
    assert "object-src 'none'" in csp_header
    assert "worker-src 'self' blob:" in csp_header
    assert "style-src 'self' 'unsafe-inline' fonts.googleapis.com" in csp_header
    assert "frame-ancestors 'none'" in csp_header
    assert "script-src 'self' 'unsafe-inline'" in csp_header
    assert "font-src 'self' fonts.gstatic.com" in csp_header
    assert "img-src 'self' data: cdn.redoc.ly" in csp_header
    assert "form-action 'self'" in csp_header
    assert "frame-src 'self'" in csp_header


def test_csp_with_envvars_configured(client, monkeypatch, settings):
    monkeypatch.setenv("CSP_EXTRA_DEFAULT_SRC", "https://default.local")
    monkeypatch.setenv("CSP_EXTRA_FORM_ACTION", "https://form-action.local")
    monkeypatch.setenv("CSP_EXTRA_IMG_SRC", "https://img.local")
    monkeypatch.setenv("CSP_OBJECT_SRC", "https://object.local")
    monkeypatch.setenv("CSP_REPORT_URI", "https://report-uri.local")
    monkeypatch.setenv("CSP_REPORT_PERCENTAGE", "0.5")

    # Unfortunately it's not possible to reload settings with envvars, so we manually
    # recompute the CSP setting instead
    settings.CONTENT_SECURITY_POLICY = testapp.settings.get_content_security_policy()
    try:
        response = client.get("/dummy/")

        csp_header = response.headers.get("Content-Security-Policy")

        # Number between 0 and 1 should be converted to number between 0 and 100
        assert settings.CONTENT_SECURITY_POLICY["REPORT_PERCENTAGE"] == 50

        assert csp_header is not None
        assert "default-src 'self' https://default.local" in csp_header
        assert "base-uri 'self'" in csp_header
        assert "object-src https://object.local" in csp_header
        assert "worker-src 'self' blob:" in csp_header
        assert (
            "style-src 'self' https://default.local 'unsafe-inline' fonts.googleapis.com"
            in csp_header
        )
        assert "frame-ancestors 'none'" in csp_header
        assert "script-src 'self' https://default.local 'unsafe-inline'" in csp_header
        assert "font-src 'self' fonts.gstatic.com" in csp_header
        assert (
            "img-src 'self' https://default.local data: cdn.redoc.ly https://img.local"
            in csp_header
        )
        assert "form-action 'self'" in csp_header
        assert "frame-src 'self'" in csp_header
    finally:
        # Manually revert the CSP back to the default, to make sure the envvar docs
        # do not use the envvar values used in this test
        monkeypatch.undo()
        settings.CONTENT_SECURITY_POLICY = (
            testapp.settings.get_content_security_policy()
        )
