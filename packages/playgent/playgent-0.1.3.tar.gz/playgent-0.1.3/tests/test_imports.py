"""Test that the package imports correctly."""



def test_package_imports():
    """Test that the main package can be imported."""
    import playgent
    assert playgent is not None


def test_version_exists():
    """Test that the package version is defined."""
    import playgent
    assert hasattr(playgent, '__version__')
    assert playgent.__version__ == "0.2.0"


def test_core_imports():
    """Test that core functions can be imported."""
    from playgent import (
        create_trace,
        get_trace,
        get_trace_events,
        init,
        reset,
        trace,
        set_session,
    )

    assert init is not None
    assert trace is not None
    assert reset is not None
    assert create_trace is not None
    assert get_trace_events is not None
    assert get_trace is not None
    assert set_session is not None


def test_decorator_imports():
    """Test that decorators can be imported."""
    from playgent import record
    assert record is not None


def test_type_imports():
    """Test that data types can be imported."""
    from playgent import EndpointEvent, EvaluationResult, Trace, TestCase

    assert EndpointEvent is not None
    assert Trace is not None
    assert TestCase is not None
    assert EvaluationResult is not None


def test_openai_client_imports():
    """Test that the OpenAI client replacements can be imported."""
    # OpenAI imports removed as openai.py file was deleted
    # This test is kept as a placeholder in case OpenAI support is re-added
    pass