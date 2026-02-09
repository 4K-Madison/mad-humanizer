import structlog
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.config import settings

logger = structlog.get_logger()


class HumanizerService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self):
        """Load base Llama 3.2 model with LoRA adapter. Call once at startup."""
        logger.info(
            "Loading humanizer model",
            base_model=settings.BASE_MODEL_NAME,
            lora_path=settings.LORA_ADAPTER_PATH,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            settings.BASE_MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.model = PeftModel.from_pretrained(
            base_model,
            settings.LORA_ADAPTER_PATH,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(settings.BASE_MODEL_NAME)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.eval()
        self._loaded = True
        logger.info("Humanizer model loaded successfully")

    def humanize(
        self,
        text: str,
        temperature: float = settings.TEMPERATURE,
        max_tokens: int = settings.MAX_OUTPUT_TOKENS,
    ) -> str:
        """Run humanization inference on the given text."""
        if not self._loaded:
            raise RuntimeError("Humanizer model is not loaded")

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True).to(
            self.model.device
        )
        input_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
            )

        # Only decode the newly generated tokens (strip the echoed input)
        new_tokens = outputs[0][input_length:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)

    def unload_model(self):
        """Release model from memory. Call at shutdown."""
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Humanizer model unloaded")
