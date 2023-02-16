from oemof_b3.config import config


def test_config_with_dynaconf():
    assert config.settings.optimize.solver == "cbc"
