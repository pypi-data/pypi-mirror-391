def test_simple_configuration(mock_base_worker_modern_conf, responses):
    # Provide the full configuration directly from the worker run
    responses.add(
        responses.GET,
        "http://testserver/api/v1/workers/runs/56785678-5678-5678-5678-567856785678/configuration/",
        status=200,
        json={"configuration": [{"key": "some_key", "value": "test", "secret": False}]},
    )

    mock_base_worker_modern_conf.configure()

    assert mock_base_worker_modern_conf.config == {"some_key": "test"}
    assert (
        mock_base_worker_modern_conf.user_configuration
        == mock_base_worker_modern_conf.config
    )
    assert mock_base_worker_modern_conf.secrets == {}


def test_empty(mock_base_worker_modern_conf, responses):
    # Provide the full configuration directly from the worker run
    responses.add(
        responses.GET,
        "http://testserver/api/v1/workers/runs/56785678-5678-5678-5678-567856785678/configuration/",
        status=200,
        json={"configuration": []},
    )

    mock_base_worker_modern_conf.configure()

    assert mock_base_worker_modern_conf.config == {}
    assert (
        mock_base_worker_modern_conf.user_configuration
        == mock_base_worker_modern_conf.config
    )
    assert mock_base_worker_modern_conf.secrets == {}


def test_with_secrets(mock_base_worker_modern_conf, responses):
    # Provide the full configuration directly from the worker run
    responses.add(
        responses.GET,
        "http://testserver/api/v1/workers/runs/56785678-5678-5678-5678-567856785678/configuration/",
        status=200,
        json={
            "configuration": [
                {"key": "some_key", "value": "test", "secret": False},
                {
                    "key": "a_secret",
                    "value": "471b9e64-29af-48dc-8bda-1a64a2da0c12",
                    "secret": True,
                },
            ]
        },
    )

    # Provide a secret value
    responses.add(
        responses.GET,
        "http://testserver/api/v1/secret/471b9e64-29af-48dc-8bda-1a64a2da0c12",
        status=200,
        json={
            "id": "471b9e64-29af-48dc-8bda-1a64a2da0c12",
            "name": "a_secret",
            "content": "My super duper secret value",
        },
    )

    mock_base_worker_modern_conf.configure()

    assert mock_base_worker_modern_conf.config == {
        "a_secret": "My super duper secret value",
        "some_key": "test",
    }
    assert (
        mock_base_worker_modern_conf.user_configuration
        == mock_base_worker_modern_conf.config
    )
    assert mock_base_worker_modern_conf.secrets == {
        "a_secret": "My super duper secret value"
    }
