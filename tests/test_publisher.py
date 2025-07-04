from insightpipe.publisher import publish
from unittest.mock import patch

@patch("paho.mqtt.client.Client")
def test_publish(mock_client_class):
    mock_client = mock_client_class.return_value
    publish("/path/img.jpg", "description", "llava")
    mock_client.connect.assert_called()
    mock_client.publish.assert_called_with(
        "wildlife/insightpipe",
        str({
            "path": "/path/img.jpg",
            "description": "description",
            "model": "llava"
        })
    )
