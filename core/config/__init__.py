SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.webp', '.gif', '.png']

# The model configured below is used for image tagging, which requires a multimodal LLM with vision capabilities.
# Options:
#    llama3.2-vision:11b        Should be very capable, but was very slow (multi-minute per image) in tests.
#    llava:7b                   A smaller model, but fast (5-6sec) and capable enough for most tasks.
#    llava-llama3:8b            Slightly slower than llava:7b, with seemingly similar performance.
#    moondream:1.8b             Fastest model (1-2sec/image), but returned briefer outputs
#                                 + a peculiar focus on specific (irrelevant) tags (e.g. 'urns').
DEFAULT_LLM_MODEL_TEXT_IMAGE = 'llava:7b'   # alternatives: 'llama3.2-vision:11b', 'llava-llama3:8b', 'moondream:1.8b'
DEFAULT_LLM_MODEL_TEXT = 'llama3.2-vision:11b'