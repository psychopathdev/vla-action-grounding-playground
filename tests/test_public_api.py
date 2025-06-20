import voicebench_load


def test_public_api_exports() -> None:
    assert voicebench_load.__version__ == "0.1.0"
    assert callable(voicebench_load.load_config)
    assert callable(voicebench_load.run_load_test)
