import torch
import onnx
import onnxruntime as rt
from torchvision import transforms as T
from PIL import Image
from .tokenizer import Tokenizer
import pathlib
import os
import urllib.request

model_url = "https://github.com/ramSeraph/captchabreaker/releases/download/model/captcha.onnx"
model_file_name = "captcha.onnx"
img_size = (32, 128)
charset = r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
tokenizer_base = Tokenizer(charset)

_transform = None
_ort_session = None
_cache_dir = None

def get_cache_dir():
    """Get cache directory for the model."""
    global _cache_dir

    if _cache_dir is not None:
        return _cache_dir

    if os.name == 'nt':
        cache_dir = pathlib.Path.home() / 'AppData' / 'Local' / 'captchabreaker'
    else:
        cache_dir = pathlib.Path.home() / '.cache' / 'captchabreaker'

    return cache_dir

def set_cache_dir(path: str):
    """Set custom cache directory for the model."""
    global _cache_dir
    print(f"Setting cache directory to: {path}")
    _cache_dir = pathlib.Path(path)

def download_model():
    """Download the model if it doesn't exist in the cache."""

    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    model_path = cache_dir / model_file_name
    if not model_path.exists():
        print(f"Downloading model to {model_path}...")
        urllib.request.urlretrieve(model_url, model_path)

    return model_path

def get_transform(img_size):
    transforms = []
    transforms.extend([
        T.Resize(img_size, T.InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(0.5, 0.5)
    ])
    return T.Compose(transforms)

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

def initialize_model():
    """Initialize the model and transform."""
    global _transform, _ort_session
    if _transform is None or _ort_session is None:
        model_path = download_model()
        _transform = get_transform(img_size)
        onnx_model = onnx.load(model_path)
        onnx.checker.check_model(onnx_model)
        _ort_session = rt.InferenceSession(str(model_path))

def solve(img_org: Image.Image) -> str:
    """Predict the text from a captcha image."""
    initialize_model()
    x = _transform(img_org.convert('RGB')).unsqueeze(0)
    ort_inputs = {_ort_session.get_inputs()[0].name: to_numpy(x)}
    logits = _ort_session.run(None, ort_inputs)[0]
    probs = torch.tensor(logits).softmax(-1)
    preds, _ = tokenizer_base.decode(probs)
    return preds[0]
