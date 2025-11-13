# Captcha Breaker [![PyPI - Latest Version](https://img.shields.io/pypi/v/captchabreaker)](https://pypi.org/project/captchabreaker/) [![GitHub Tag](https://img.shields.io/github/v/tag/ramSeraph/captchabreaker?filter=v*)](https://github.com/ramSeraph/captchabreaker/releases/latest)

A library to break captchas using a deep learning model.

## Provenance

This project's inference code is adapted from the [Hugging Face Space by docparser](https://huggingface.co/spaces/docparser/Text_Captcha_breaker/tree/main).

The underlying model is a copy of [DocParser/captcha](https://huggingface.co/DocParser/captcha), licensed under CC BY 4.0. 

A local copy of the model is hosted in this repository for convenience [https://github.com/ramSeraph/captchabreaker/releases/tag/model](https://github.com/ramSeraph/captchabreaker/releases/tag/model).

## Installation

To install the necessary dependencies, run:

```bash
pip install captchabreaker
```

## Usage

To use the captcha breaker, you can use the `captchabreaker.solve()` function.
It takes a PIL Image object as input and returns the predicted text.

Here is an example:

```python
from PIL import Image
import captchabreaker

if __name__ == '__main__':
    # This is an example of how to use the captchabreaker package.
    # You need to have a captcha image file (e.g., captcha.png) in the same directory.
    try:
        img = Image.open("sample.png")
        text = captchabreaker.solve(img)
        print(f"Predicted text: {text}")
    except FileNotFoundError:
        print("Error: captcha.png not found. Please provide a captcha image.")
```
