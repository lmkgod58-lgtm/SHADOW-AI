import os
import urllib.request

class LLMEngine:
    """
    Self-hosted Qwen2.5-0.5B-Instruct via llama-cpp-python.
    No OpenAI API. No Ollama. Pure local inference.
    """

    def __init__(self):
        self.model_path = os.environ.get("MODEL_PATH", "/app/models/model.gguf")
        self.model_url = os.environ.get(
            "MODEL_URL",
            "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q3_k_m.gguf"
        )
        self.llm = None
        self._ensure_model()
        self._load_model()

    def _ensure_model(self):
        if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1000000:
            print(f"[LLM] Model found: {os.path.getsize(self.model_path)} bytes")
            return
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        print(f"[LLM] Downloading model...")
        try:
            urllib.request.urlretrieve(self.model_url, self.model_path)
            print(f"[LLM] Downloaded: {os.path.getsize(self.model_path)} bytes")
        except Exception as e:
            print(f"[LLM] Download failed: {e}")

    def _load_model(self):
        if not os.path.exists(self.model_path) or os.path.getsize(self.model_path) < 1000000:
            print("[LLM] Model missing. Fallback mode active.")
            return
        try:
            from llama_cpp import Llama
            print("[LLM] Loading model into RAM (~30s)...")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=2,
                n_batch=1,
                verbose=False
            )
            print("[LLM] Model loaded.")
        except Exception as e:
            print(f"[LLM] Load failed: {e}")

    def is_loaded(self) -> bool:
        return self.llm is not None

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if self.llm is None:
            return None
        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                stop=["User:", "Human:", "You:", "</s>", "[INST]"],
                repeat_penalty=1.1
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            print(f"[LLM] Generation error: {e}")
            return None
