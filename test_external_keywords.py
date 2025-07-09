from insightpipe import init_from_file, keyword_file, describe_file

try:
    tags = keyword_file("/Volumes/wildlife/processed_detections/multifrigate_20250709_005510.jpg", "qwen2.5vl:latest",4)
except Exception as e:
    print(f"Error generating tags: {e}")
    tags = None
print(tags)  # This will print the generated tags in JSON format.
try:
    tags = describe_file("/Volumes/wildlife/processed_detections/multifrigate_20250709_005510.jpg", "If you were to describe this image to a children, what would you say?", "qwen2.5vl:latest")
except Exception as e:
    print(f"Error generating tags: {e}")
    tags = None
print(tags)  # This will print the generated tags in JSON format.