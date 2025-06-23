# image-search-llm

Command line tool to interpret, tag and search collections of images using a locally run LLM / Multi-Modal model.

Intended as a showcase, to be run on an Apple Silicon Mac with sufficient RAM to run models with ~10B parameters.  Not tested on other hardware,
but should work on any system that can run `ollama`, e.g. Windows systems with recent Nvidia GPUs.

## 1. Getting started

- **Installing `ollama` & `llava:7b` model**
  - Install ollama
    - run `brew install ollama`
    - check installation with `ollama --version`  (you'll get a warning no server is running)
  - Start ollama server: `ollama serve`
  - Pull llava 7B model: `ollama pull llava:7b`   (=about ±5GB download)
  - Test-run it by running `ollama run llava:7b` allowing you to interact with the model, like having a local chatGPT.
- **Install Python dependencies**
  - set up a virtual environment (optional but recommended) as desired (e.g conda)
  - `pip install -r requirements.txt`
