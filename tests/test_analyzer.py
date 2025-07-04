from insightpipe.analyzer import analyze_image
from unittest.mock import patch, mock_open

@patch("requests.post")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_analyze_image(mock_file, mock_post):
    mock_post.return_value.json.return_value = {
        "response": "Mocked description"
    }
    desc = analyze_image("dummy.jpg", "llava")
    assert desc == "Mocked description"
