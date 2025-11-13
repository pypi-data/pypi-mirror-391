"""
Custom Cache Implementation for Ouro Universal Transformer

This fixes the KV cache bug while preserving the 4-loop Universal Transformer architecture.
"""

import logging
import time
import traceback
from typing import Any, List, Optional, Tuple, Union

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizerBase
from transformers.cache_utils import Cache
from transformers.modeling_utils import PreTrainedModel

logger = logging.getLogger(__name__)


class UniversalTransformerCache(Cache):
    """
    Custom cache for Universal Transformer architecture.

    Ouro uses total_ut_steps=4, meaning each layer processes the input 4 times.
    This requires a 2D cache structure: [ut_step][layer]

    The cache index calculation in Ouro is:
        cache_idx = current_ut * num_hidden_layers + layer_idx

    For 32 layers and 4 UT steps:
        - UT step 0: indices 0-31
        - UT step 1: indices 32-63
        - UT step 2: indices 64-95
        - UT step 3: indices 96-127

    Args:
        max_cache_size: Optional maximum number of cache indices to prevent OOM.
                       For Ouro-1.4B: total_ut_steps (4) × num_hidden_layers (32) = 128
                       Default is None (unlimited).
    """

    def __init__(self, max_cache_size: Optional[int] = None):
        # Don't call super().__init__() to avoid the ValueError
        self.key_cache: List[Optional[torch.Tensor]] = []
        self.value_cache: List[Optional[torch.Tensor]] = []
        self._seen_tokens = 0  # Track number of tokens processed
        self.layers: List[Any] = []  # Required by transformers Cache interface
        self.max_cache_size = max_cache_size

        logger.debug(f"Initialized UniversalTransformerCache with max_cache_size={max_cache_size}")

    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        layer_idx: int,
        cache_kwargs: Optional[dict] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Update cache for the given layer index.

        Args:
            key_states: New key states [batch, num_heads, seq_len, head_dim]
            value_states: New value states [batch, num_heads, seq_len, head_dim]
            layer_idx: Global cache index (0-127 for Ouro with 4 UT steps × 32 layers)

        Returns:
            Updated key and value states
        """
        # Input validation
        if layer_idx < 0:
            raise ValueError(
                f"layer_idx must be non-negative, got {layer_idx}. "
                f"This typically indicates an error in the model's cache indexing logic."
            )

        if self.max_cache_size is not None and layer_idx >= self.max_cache_size:
            logger.warning(
                f"Cache index {layer_idx} exceeds max_cache_size={self.max_cache_size}. "
                f"This may indicate a configuration mismatch."
            )
            raise ValueError(
                f"Cache index {layer_idx} exceeds max_cache_size={self.max_cache_size}. "
                f"This may indicate a configuration mismatch or attempt to cache beyond limits."
            )

        if not isinstance(key_states, torch.Tensor) or not isinstance(value_states, torch.Tensor):
            raise TypeError(
                "key_states and value_states must be torch.Tensor. "
                "Ensure model layers are producing valid attention outputs. "
                f"Got key_states type: {type(key_states).__name__}, "
                f"value_states type: {type(value_states).__name__}"
            )

        if key_states.dim() != 4 or value_states.dim() != 4:
            raise ValueError(
                f"Expected 4D tensors [batch, heads, seq, dim], "
                f"got key_states: {key_states.dim()}D, value_states: {value_states.dim()}D"
            )

        # Extend cache list if needed
        while len(self.key_cache) <= layer_idx:
            self.key_cache.append(None)
            self.value_cache.append(None)

        # Update cache at this index
        if self.key_cache[layer_idx] is None:
            # First time seeing this cache index
            self.key_cache[layer_idx] = key_states
            self.value_cache[layer_idx] = value_states
        else:
            # Validate shapes match for concatenation (except seq_len dimension)
            cached_key = self.key_cache[layer_idx]
            assert cached_key is not None  # Type narrowing for mypy
            if (
                key_states.shape[0] != cached_key.shape[0]
                or key_states.shape[1] != cached_key.shape[1]
                or key_states.shape[3] != cached_key.shape[3]
            ):
                raise ValueError(
                    f"Shape mismatch: cannot concatenate cached {cached_key.shape} "
                    f"with new {key_states.shape} (must match on batch, heads, dim). "
                    f"This may happen if batch_size or num_heads changed between forward passes."
                )

            # Concatenate with existing cache
            cached_value = self.value_cache[layer_idx]
            assert cached_value is not None  # Type narrowing for mypy
            self.key_cache[layer_idx] = torch.cat([cached_key, key_states], dim=2)
            self.value_cache[layer_idx] = torch.cat([cached_value, value_states], dim=2)

        result_key = self.key_cache[layer_idx]
        result_value = self.value_cache[layer_idx]
        assert result_key is not None and result_value is not None  # Type narrowing
        return result_key, result_value

    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        """Get sequence length from cache."""
        if layer_idx is None:
            layer_idx = 0
        if layer_idx < 0 or len(self.key_cache) <= layer_idx or self.key_cache[layer_idx] is None:
            return 0
        cached = self.key_cache[layer_idx]
        assert cached is not None  # Type narrowing for mypy
        return cached.shape[2]

    def get_max_length(self) -> Optional[int]:
        """No maximum length for this cache implementation."""
        return None

    def get_usable_length(self, new_seq_length: int, layer_idx: Optional[int] = 0) -> int:
        """Get usable cache length."""
        return self.get_seq_length(layer_idx)

    def reorder_cache(self, beam_idx: torch.LongTensor) -> None:
        """Reorder cache for beam search."""
        for idx, (key_cache_entry, value_cache_entry) in enumerate(
            zip(self.key_cache, self.value_cache)
        ):
            if key_cache_entry is not None:
                assert value_cache_entry is not None  # Type narrowing
                device = key_cache_entry.device
                self.key_cache[idx] = key_cache_entry.index_select(0, beam_idx.to(device))
                self.value_cache[idx] = value_cache_entry.index_select(0, beam_idx.to(device))

    @property
    def is_compileable(self) -> bool:
        """Whether this cache is compatible with torch.compile."""
        return False  # Custom cache, not compileable

    def clear(self) -> None:
        """
        Clear all cached key-value pairs to free memory.

        This is useful for:
        - Releasing GPU memory after generation
        - Starting fresh for a new sequence
        - Debugging/testing
        """
        cache_size = len(self.key_cache)
        logger.debug(f"Clearing cache with {cache_size} entries")

        self.key_cache = []
        self.value_cache = []
        self._seen_tokens = 0


def load_ouro_with_custom_cache(  # pragma: no cover
    model_path: str = "ByteDance/Ouro-1.4B",
) -> Tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """
    Load Ouro model that uses custom Universal Transformer cache.

    This preserves the 4-loop architecture while fixing the cache bug.

    Args:
        model_path: HuggingFace model path or local directory.

    Returns:
        Tuple of (model, tokenizer) ready for inference.
    """
    print("Loading Ouro with custom Universal Transformer cache...")

    # Load config and tokenizer
    config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    print("Config loaded:")
    print(f"   - total_ut_steps: {config.total_ut_steps}")
    print(f"   - num_hidden_layers: {config.num_hidden_layers}")
    print(f"   - Total cache indices needed: {config.total_ut_steps * config.num_hidden_layers}")

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_path, config=config, dtype=torch.float16, device_map="auto", trust_remote_code=True
    )

    print(f"Model loaded on device: {model.device}")

    return model, tokenizer


def test_custom_cache() -> None:  # pragma: no cover
    """Test Ouro with custom cache on medical reasoning examples."""

    model, tokenizer = load_ouro_with_custom_cache()

    test_cases = [
        {
            "input": "Patient presents with fever, cough, and difficulty breathing.",
            "max_new_tokens": 100,
        },
        {"input": "Diagnosis: Type 2 Diabetes. Treatment plan:", "max_new_tokens": 80},
        {"input": "Side effects of aspirin include:", "max_new_tokens": 60},
    ]

    print("\n" + "=" * 80)
    print("Testing Ouro with Custom Universal Transformer Cache")
    print("=" * 80 + "\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test Case {i}")
        print(f"{'─'*80}")
        print(f"Input: {test_case['input']}")
        print(f"\n{'─'*40}")

        # Tokenize
        inputs = tokenizer(test_case["input"], return_tensors="pt").to(model.device)

        # Create custom cache
        past_key_values = UniversalTransformerCache()

        try:
            start_time = time.time()

            # Generate with custom cache
            with torch.no_grad():
                outputs = model.generate(  # type: ignore[operator]
                    **inputs,
                    max_new_tokens=test_case["max_new_tokens"],
                    past_key_values=past_key_values,
                    use_cache=True,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                )

            end_time = time.time()
            elapsed = end_time - start_time

            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            num_tokens = outputs[0].shape[0] - inputs["input_ids"].shape[1]
            tokens_per_sec = num_tokens / elapsed if elapsed > 0 else 0

            print(f"Output:\n{generated_text}")
            print(f"\n{'─'*40}")
            print("SUCCESS")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Tokens: {num_tokens}")
            print(f"   Speed: {tokens_per_sec:.2f} tokens/s (~{1/tokens_per_sec:.3f}s per token)")
            print(f"   Cache size: {len(past_key_values.key_cache)} indices")

        except Exception as e:
            print(f"\nFAILED: {str(e)}")
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("Testing Complete")
    print("=" * 80)


if __name__ == "__main__":  # pragma: no cover
    test_custom_cache()
