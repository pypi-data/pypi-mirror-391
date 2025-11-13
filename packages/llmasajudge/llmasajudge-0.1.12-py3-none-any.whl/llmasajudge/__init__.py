# import os
# from openai import OpenAI

# __all__ = ["WandbInferenceLLMJudge"]

# class WandbInferenceLLMJudge:
#     DEFAULT_TEMPLATE = """\
# You are a judge. Read input, model_output, and ground_truth.
# Return exactly one word: right or wrong.
# Rules:
# - Treat extra words or punctuation as irrelevant if the same final value is present.
# - Output must be exactly right or wrong. No JSON. No quotes. No extra text.
# ##################
# {notes_section}{input_section}model_output:
# {model_output}
# ##################
# ground_truth:
# {ground_truth}
# ##################
# """
#     def __init__(self, models, api_key=None, base_url=None, project=None, default_headers=None,
#                  custom_template=None, notes=None):
#         self.models = models
#         self.notes = notes or ""
#         self.template = custom_template or self.DEFAULT_TEMPLATE

#         kwargs = {"base_url": base_url or "https://api.inference.wandb.ai/v1"}
#         if api_key or os.getenv("WANDB_API_KEY"):
#             kwargs["api_key"] = api_key or os.getenv("WANDB_API_KEY")
#         if project or os.getenv("WANDB_PROJECT"):
#             kwargs["project"] = project or os.getenv("WANDB_PROJECT")

#         headers = dict(default_headers or {})
#         if project or os.getenv("WANDB_PROJECT"):
#             headers.setdefault("OpenAI-Project", project or os.getenv("WANDB_PROJECT"))
#         headers.setdefault("OpenAI-Project", "wandb_fc/quickstart_playground")
#         kwargs["default_headers"] = headers

#         self.client = OpenAI(**kwargs)

#     def _build_prompt(self, input, model_output, ground_truth):
#         notes_section = f"notes:\n{self.notes}\n" if self.notes else ""
#         input_section = f"input:\n{input}\n##################\n" if input else ""
#         return self.template.format(
#             notes_section=notes_section,
#             input_section=input_section,
#             model_output=str(model_output),
#             ground_truth=str(ground_truth),
#         )
    

#     @staticmethod
#     def _last6_right_wrong(s: str):
#         if not s:
#             return None
#         tail = s.strip()[-6:].lower()
#         if "right" in tail:
#             return True
#         if "wrong" in tail:
#             return False
#         return None

#     def _ask_model(self, model, prompt, max_tokens, model_output, ground_truth):
#         try:
#             resp = self.client.chat.completions.create(
#                 model=model,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0,
#                 max_tokens=max_tokens,
#             )
#             content = (resp.choices[0].message.content or "").strip()
#             parsed = self._last6_right_wrong(content)
#             if parsed is not None:
#                 return parsed
#         except Exception:
#             print("model call failed, falling back to string match", flush=True)
#         return str(model_output).strip() == str(ground_truth).strip()

#     def judge(self, input, model_output, ground_truth, max_tokens=8, mode="majority"):
#         prompt = self._build_prompt(input, model_output, ground_truth)
#         votes = []
#         for m in self.models:
#             res = self._ask_model(m, prompt, max_tokens, model_output, ground_truth)
#             print(f"Model {m} voted: {res}", flush=True)
#             votes.append({"model": m, "correct": res})

#         if mode == "single":
#             final = votes[0]["correct"]
#         elif mode == "majority":
#             true_votes = sum(v["correct"] for v in votes)
#             false_votes = len(votes) - true_votes
#             final = True if true_votes >= false_votes else False
#         else:
#             raise ValueError("mode must be 'majority' or 'single'")

#         return {"correct": final, "mode": mode, "votes": votes}



# import os
# from openai import OpenAI

# __all__ = ["WandbInferenceLLMJudge"]

# class WandbInferenceLLMJudge:
#     DEFAULT_TEMPLATE = """\
# You are a judge. Read input, model_output, and ground_truth.
# Return exactly one word: right or wrong.
# Rules:
# - Treat extra words or punctuation as irrelevant if the same final value is present.
# - Output must be exactly right or wrong. No JSON. No quotes. No extra text.
# ##################
# {notes_section}input:
# {input_block}
# ##################
# model_output:
# {model_output}
# ##################
# ground_truth:
# {ground_truth}
# ##################
# """

#     def __init__(self, models, api_key=None, base_url=None, project=None, default_headers=None,
#                  custom_template=None, notes=None):
#         self.models = models
#         self.notes = notes or ""
#         self.template = custom_template or self.DEFAULT_TEMPLATE

#         kwargs = {"base_url": base_url or "https://api.inference.wandb.ai/v1"}
#         if api_key or os.getenv("WANDB_API_KEY"):
#             kwargs["api_key"] = api_key or os.getenv("WANDB_API_KEY")
#         if project or os.getenv("WANDB_PROJECT"):
#             kwargs["project"] = project or os.getenv("WANDB_PROJECT")

#         headers = dict(default_headers or {})
#         if project or os.getenv("WANDB_PROJECT"):
#             headers.setdefault("OpenAI-Project", project or os.getenv("WANDB_PROJECT"))
#         headers.setdefault("OpenAI-Project", "wandb_fc/quickstart_playground")
#         kwargs["default_headers"] = headers

#         self.client = OpenAI(**kwargs)

#     def _build_prompt(self, input, model_output, ground_truth):
#         notes_section = f"notes:\n{self.notes}\n" if self.notes else ""
#         input_text = str(input) if input not in (None, "") else "[ommitted input for brevity]"
#         return self.template.format(
#             notes_section=notes_section,
#             input_block=input_text,
#             model_output=str(model_output),
#             ground_truth=str(ground_truth),
#         )

#     @staticmethod
#     def _last6_right_wrong(s: str):
#         if not s:
#             return None
#         tail = s.strip()[-6:].lower()
#         if "right" in tail:
#             return True
#         if "wrong" in tail:
#             return False
#         return None

#     def _ask_model(self, model, prompt, max_tokens, model_output, ground_truth):
#         try:
#             resp = self.client.chat.completions.create(
#                 model=model,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0,
#                 max_tokens=max_tokens,
#             )
#             content = (resp.choices[0].message.content or "").strip()
#             parsed = self._last6_right_wrong(content)
#             if parsed is not None:
#                 return parsed
#         except Exception:
#             print("model call failed, falling back to string match", flush=True)
#         return str(model_output).strip() == str(ground_truth).strip()

#     def judge(self, input=None, model_output=None, ground_truth=None, max_tokens=8, mode="majority"):
#         prompt = self._build_prompt(input, model_output, ground_truth)
#         votes = []
#         for m in self.models:
#             res = self._ask_model(m, prompt, max_tokens, model_output, ground_truth)
#             print(f"Model {m} voted: {res}", flush=True)
#             votes.append({"model": m, "correct": res})

#         if mode == "single":
#             final = votes[0]["correct"]
#         elif mode == "majority":
#             true_votes = sum(v["correct"] for v in votes)
#             false_votes = len(votes) - true_votes
#             final = True if true_votes >= false_votes else False
#         else:
#             raise ValueError("mode must be 'majority' or 'single'")

#         return {"correct": final, "mode": mode, "votes": votes}





import os
import time
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
import litellm
from litellm import completion
from litellm.caching.caching import Cache


__all__ = ["LLMAsAJudge", "OutputParsers"]


class UnlimitedDiskCache:
    """
    Drop-in replacement backend with 'unlimited' size for LiteLLM cache.

    This wraps diskcache.Cache with a very large size limit (2^62 bytes ~ 4.6 exabytes)
    to effectively disable automatic cache eviction, allowing the cache to grow
    without size constraints.
    """

    def __init__(self, directory, size_limit=None):
        """
        Initialize unlimited disk cache.

        Args:
            directory: Path to cache directory
            size_limit: Optional size limit in bytes. If None, uses 2^62 bytes (~4.6 exabytes)
        """
        import diskcache as dc

        # Set to very large cap so culling never triggers (effectively unlimited)
        cap = size_limit if size_limit is not None else (1 << 62)
        self._dc = dc.Cache(directory, size_limit=cap)

    # Sync API used by LiteLLM
    def get_cache(self, key, **kwargs):
        """Get value from cache by key."""
        return self._dc.get(key)

    def set_cache(self, key, value, ttl=None, **kwargs):
        """Set value in cache with optional TTL."""
        expire = None if ttl is None else float(ttl)
        self._dc.set(key, value, expire=expire)

    # Async API used by LiteLLM
    async def async_get_cache(self, key, **kwargs):
        """Async get value from cache by key."""
        return self.get_cache(key, **kwargs)

    async def async_set_cache(self, key, value, ttl=None, **kwargs):
        """Async set value in cache with optional TTL."""
        return self.set_cache(key, value, ttl=ttl, **kwargs)

    async def async_set_cache_pipeline(self, cache_list, ttl=None, **kwargs):
        """
        Async batch set multiple cache entries.

        Args:
            cache_list: List of (key, value) tuples
            ttl: Optional time-to-live in seconds
        """
        for k, v in cache_list:
            self.set_cache(k, v, ttl=ttl)

    async def batch_cache_write(self, key, value, ttl=None, **kwargs):
        """Async batch write (single entry)."""
        self.set_cache(key, value, ttl=ttl)

    async def ping(self):
        """Async ping check."""
        return True

    async def delete_cache_keys(self, keys):
        """
        Async delete multiple cache keys.

        Args:
            keys: List of keys to delete
        """
        for k in keys:
            try:
                del self._dc[k]
            except KeyError:
                pass
        return True

    async def disconnect(self):
        """Async disconnect and close cache."""
        self._dc.close()

    def get_stats(self):
        """
        Get cache statistics.

        Returns:
            dict with size_limit, current_size, item_count, and percent_full
        """
        size_limit = self._dc.size_limit
        volume = self._dc.volume()  # Current size in bytes
        count = len(self._dc)  # Number of items

        return {
            "size_limit": size_limit,
            "current_size": volume,
            "item_count": count,
            "percent_full": (volume / size_limit) * 100 if size_limit > 0 else 0.0,
        }

    def print_stats(self):
        """Print human-readable cache statistics."""
        stats = self.get_stats()

        def human_size(bytes_val):
            """Convert bytes to human readable format."""
            for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB"]:
                if bytes_val < 1024.0:
                    return f"{bytes_val:.2f} {unit}"
                bytes_val /= 1024.0
            return f"{bytes_val:.2f} EB"

        print("=" * 60)
        print("CACHE STATISTICS")
        print("=" * 60)
        print(f"  Size limit:     {human_size(stats['size_limit'])} ({stats['size_limit']:,} bytes)")
        print(f"  Current size:   {human_size(stats['current_size'])} ({stats['current_size']:,} bytes)")
        print(f"  Items cached:   {stats['item_count']}")
        print(f"  % full:         {stats['percent_full']:.6f}%")
        print("=" * 60)


class OutputParsers:
    """Stock output parsers for common judge output formats."""

    @staticmethod
    def right_wrong(s: str) -> Optional[bool]:
        """Parse 'right' or 'wrong' from the last 6 characters."""
        if not s:
            return None
        tail = s.strip()[-6:].lower()
        if "right" in tail:
            return True
        if "wrong" in tail:
            return False
        return None

    @staticmethod
    def pass_fail(s: str) -> Optional[bool]:
        """Parse 'pass' or 'fail' from the response."""
        if not s:
            return None
        text = s.strip().lower()
        if "pass" in text:
            return True
        if "fail" in text:
            return False
        return None

    @staticmethod
    def yes_no(s: str) -> Optional[bool]:
        """Parse 'yes' or 'no' from the response."""
        if not s:
            return None
        text = s.strip().lower()
        if "yes" in text:
            return True
        if "no" in text:
            return False
        return None

    @staticmethod
    def numeric_score(s: str) -> Optional[float]:
        """Extract first numeric value from the response."""
        if not s:
            return None
        match = re.search(r'[-+]?\d*\.?\d+', s.strip())
        if match:
            return float(match.group())
        return None

    @staticmethod
    def json_extract(key: str) -> Callable[[str], Any]:
        """Create a parser that extracts a specific key from JSON output."""
        import json
        def parser(s: str) -> Any:
            if not s:
                return None
            try:
                data = json.loads(s.strip())
                return data.get(key)
            except (json.JSONDecodeError, AttributeError):
                return None
        return parser


class LLMAsAJudge:
    BASE_TEMPLATE = """\
You are a judge. Read input, model_output, and ground_truth.
{instruction}
##################
{notes_section}### input:
{input_block}
##################
model's output:
{model_output}
##################
ground_truth answer:
{ground_truth}
##################
"""

    PARSER_INSTRUCTIONS = {
        'right/wrong': """\
Return exactly one word: right or wrong.
Rules:
- Treat extra words or punctuation as irrelevant if the same final value is present.
- Output must be exactly right or wrong. No JSON. No quotes. No extra text.""",
        'yes/no': """\
Return exactly one word: yes or no.
Answer yes if the model output matches the ground truth, no otherwise.
Rules:
- Treat extra words or punctuation as irrelevant if the same final value is present.
- Output must be exactly yes or no. No JSON. No quotes. No extra text.""",
        'pass/fail': """\
Return exactly one word: pass or fail.
Answer pass if the model output matches the ground truth, fail otherwise.
Rules:
- Treat extra words or punctuation as irrelevant if the same final value is present.
- Output must be exactly pass or fail. No JSON. No quotes. No extra text.""",
        'numeric': """\
Return a single numeric score from 0-10 indicating how well the model output matches the ground truth.
- 10 = perfect match
- 7-9 = close match with minor differences
- 4-6 = partial match
- 1-3 = poor match
- 0 = completely wrong
Output only the number. No explanation. No extra text.""",
    }




    # def __init__(
    #     self,
    #     models: Optional[List[str]] = None,
    #     config: Optional[Dict[str, Dict[str, Any]]] = None,   # one dict for providers and models
    #     base_headers: Optional[Dict[str, str]] = None,
    #     wandb_project: Optional[str] = None,
    #     custom_template: Optional[str] = None,
    #     use_fully_custom_prompt: bool = False,
    #     notes: Optional[str] = None,
    #     output_parser: Optional[str] = 'right/wrong',
    #     fallback_comparison: bool = True,
    #     default_temperature: float = 0.0,
    #     verbose: bool = False,
    #     num_retries: int = 2,          # per-call retries before giving up on that model
    #     backoff_base: float = 0.5,     # seconds
    #     backoff_max: float = 4.0,      # seconds
    #     custom_generation_fns: Optional[List[Callable[[str], str]]] = None,
    #     mode: str = "majority",        # "single", "majority", "all"
    # ):
    #     """
    #     config keys can be a provider name ("wandb", "openai", "anthropic")
    #     or a full model name ("openai/gpt-4o-mini", "wandb/deepseek-ai/DeepSeek-V3.1").

    #     Values can include:
    #         api_base: Optional[str]
    #         headers: Dict[str, str]
    #         temperature: float

    #     Precedence:
    #         base_headers < provider config < model config

    #     Args:
    #         models: List of litellm model strings (e.g., ["openai/gpt-4", "anthropic/claude-3"])
    #         custom_template: Template with placeholders for input/output/ground_truth
    #         use_fully_custom_prompt: If True, pass complete prompt to judge(prompt=...).
    #                                  When True, input/output/ground_truth must NOT be passed to judge()
    #         output_parser: Parser name ('right/wrong', 'yes/no', 'pass/fail', 'numeric')
    #                       or custom function with signature (str) -> Any
    #         fallback_comparison: If True and parser returns None, falls back to string comparison
    #         custom_generation_fns: List of custom inference functions with signature fn(prompt: str) -> str
    #                                These will be used in addition to litellm models for voting.
    #         mode: Voting mode - "majority" (default), "single" (first judge only), or "all" (unanimous)
    #     """
    #     self.models = models or []
    #     self.custom_generation_fns = custom_generation_fns or []

    #     # Validate that at least one judge is provided
    #     if not self.models and not self.custom_generation_fns:
    #         raise ValueError("Must provide at least one of: models (litellm) or custom_generation_fns")

    #     # Validate mode
    #     if mode not in ("majority", "single", "all"):
    #         raise ValueError("mode must be 'majority', 'single', or 'all'")

    #     self.config = config or {}
    #     self.base_headers = dict(base_headers or {})
    #     self.wandb_project = wandb_project or os.getenv("WANDB_PROJECT")
    #     self.notes = notes or ""
    #     self.use_fully_custom_prompt = use_fully_custom_prompt
    #     self.mode = mode

    #     # Resolve output parser
    #     parser_name = None
    #     if isinstance(output_parser, str):
    #         parser_map = {
    #             'right/wrong': OutputParsers.right_wrong,
    #             'pass/fail': OutputParsers.pass_fail,
    #             'yes/no': OutputParsers.yes_no,
    #             'numeric': OutputParsers.numeric_score,
    #         }
    #         if output_parser not in parser_map:
    #             raise ValueError(f"Unknown parser '{output_parser}'. Available: {list(parser_map.keys())}")
    #         self.output_parser = parser_map[output_parser]
    #         parser_name = output_parser
    #     else:
    #         self.output_parser = output_parser

    #     # Set template based on mode
    #     if use_fully_custom_prompt:
    #         self.template = None  # No template in fully custom mode
    #     elif custom_template:
    #         self.template = custom_template
    #     elif parser_name and parser_name in self.PARSER_INSTRUCTIONS:
    #         self.template = self.BASE_TEMPLATE.format(
    #             instruction=self.PARSER_INSTRUCTIONS[parser_name],
    #             notes_section="{notes_section}",
    #             input_block="{input_block}",
    #             model_output="{model_output}",
    #             ground_truth="{ground_truth}",
    #         )
    #     else:
    #         # Default to right/wrong for custom parsers
    #         self.template = self.BASE_TEMPLATE.format(
    #             instruction=self.PARSER_INSTRUCTIONS['right/wrong'],
    #             notes_section="{notes_section}",
    #             input_block="{input_block}",
    #             model_output="{model_output}",
    #             ground_truth="{ground_truth}",
    #         )

    #     self.fallback_comparison = fallback_comparison
    #     self.default_temperature = float(default_temperature)
    #     self.verbose = verbose
    #     self.num_retries = int(num_retries)
    #     self.backoff_base = float(backoff_base)
    #     self.backoff_max = float(backoff_max)






    def __init__(
        self,
        models: Optional[List[str]] = None,
        config: Optional[Dict[str, Dict[str, Any]]] = None,
        base_headers: Optional[Dict[str, str]] = None,
        wandb_project: Optional[str] = None,
        custom_template: Optional[str] = None,
        use_fully_custom_prompt: bool = False,
        notes: Optional[str] = None,
        output_parser: Optional[str] = 'right/wrong',
        fallback_comparison: bool = True,
        default_temperature: float = 0.0,
        verbose: bool = False,
        num_retries: int = 2,
        backoff_base: float = 0.5,
        backoff_max: float = 4.0,
        custom_generation_fns: Optional[List[Callable[[str], str]]] = None,
        mode: str = "majority",
        litellm_cache_dir: Optional[str] = None,
        cache_size_gb: Optional[float] = None,
    ):
        self.models = models or []
        self.custom_generation_fns = custom_generation_fns or []

        if not self.models and not self.custom_generation_fns:
            raise ValueError("Must provide at least one of: models (litellm) or custom_generation_fns")

        if mode not in ("majority", "single", "all"):
            raise ValueError("mode must be 'majority', 'single', or 'all'")

        self.config = config or {}
        self.base_headers = dict(base_headers or {})
        self.wandb_project = wandb_project or os.getenv("WANDB_PROJECT")
        self.notes = notes or ""
        self.use_fully_custom_prompt = use_fully_custom_prompt
        self.mode = mode
        self.fallback_comparison = fallback_comparison
        self.default_temperature = float(default_temperature)
        self.verbose = verbose
        self.num_retries = int(num_retries)
        self.backoff_base = float(backoff_base)
        self.backoff_max = float(backoff_max)

        parser_name = None
        if isinstance(output_parser, str):
            parser_map = {
                'right/wrong': OutputParsers.right_wrong,
                'pass/fail': OutputParsers.pass_fail,
                'yes/no': OutputParsers.yes_no,
                'numeric': OutputParsers.numeric_score,
            }
            if output_parser not in parser_map:
                raise ValueError(f"Unknown parser '{output_parser}'")
            self.output_parser = parser_map[output_parser]
            parser_name = output_parser
        else:
            self.output_parser = output_parser

        if use_fully_custom_prompt:
            self.template = None
        elif custom_template:
            self.template = custom_template
        elif parser_name and parser_name in self.PARSER_INSTRUCTIONS:
            self.template = self.BASE_TEMPLATE.format(
                instruction=self.PARSER_INSTRUCTIONS[parser_name],
                notes_section="{notes_section}",
                input_block="{input_block}",
                model_output="{model_output}",
                ground_truth="{ground_truth}",
            )
        else:
            self.template = self.BASE_TEMPLATE.format(
                instruction=self.PARSER_INSTRUCTIONS['right/wrong'],
                notes_section="{notes_section}",
                input_block="{input_block}",
                model_output="{model_output}",
                ground_truth="{ground_truth}",
            )

        # optional local cache setup
        self.cache_enabled = litellm_cache_dir is not None
        if self.cache_enabled:
            # Convert GB to bytes if specified, otherwise unlimited
            size_limit_bytes = None if cache_size_gb is None else int(cache_size_gb * 1024 * 1024 * 1024)
            cache_backend = UnlimitedDiskCache(litellm_cache_dir, size_limit=size_limit_bytes)
            litellm.cache = Cache(disk_cache_dir=litellm_cache_dir)
            litellm.cache.cache = cache_backend









    def _build_prompt(self, input: Any, model_output: Any, ground_truth: Any) -> str:
        notes_section = f"notes:\n{self.notes}\n" if self.notes else ""
        input_text = str(input) if input not in (None, "") else "[omitted input for brevity]"
        return self.template.format(
            notes_section=notes_section,
            input_block=input_text,
            model_output=str(model_output),
            ground_truth=str(ground_truth),
        )

    @staticmethod
    def _last6_right_wrong(s: str):
        if not s:
            return None
        tail = s.strip()[-6:].lower()
        if "right" in tail:
            return True
        if "wrong" in tail:
            return False
        return None

    def _resolve_per_model(self, model: str) -> Tuple[Optional[str], Dict[str, str], float]:
        provider = model.split("/", 1)[0] if "/" in model else model

        api_base: Optional[str] = None
        headers: Dict[str, str] = dict(self.base_headers)
        temperature: float = self.default_temperature

        # provider-level defaults
        pc = self.config.get(provider, {})
        if pc.get("api_base") is not None:
            api_base = pc["api_base"]
        headers.update(pc.get("headers", {}))
        if "temperature" in pc:
            temperature = float(pc["temperature"])

        # model-level overrides
        mc = self.config.get(model, {})
        if mc.get("api_base") is not None:
            api_base = mc["api_base"]
        headers.update(mc.get("headers", {}))
        if "temperature" in mc:
            temperature = float(mc["temperature"])

        # wandb defaults
        if provider == "wandb":
            if api_base is None:
                api_base = "https://api.inference.wandb.ai/v1"
            if "OpenAI-Project" not in headers:
                headers["OpenAI-Project"] = self.wandb_project or "wandb_fc/quickstart_playground"

        return api_base, headers, temperature

    def _attempt_completion(
        self,
        model: str,
        api_base: Optional[str],
        headers: Dict[str, str],
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        attempts = self.num_retries + 1
        last_err = None
        for i in range(attempts):
            try:
                # resp = completion(
                #     model=model,
                #     api_base=api_base,  # None uses provider default
                #     messages=[{"role": "user", "content": prompt}],
                #     temperature=temperature,
                #     max_tokens=max_tokens,
                #     extra_headers=headers,
                # )

                resp = completion(
                    model=model,
                    api_base=api_base,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=headers,
                    caching=self.cache_enabled
                )                
                return (resp.choices[0].message.content or "").strip()
            except Exception as e:
                last_err = e
                if i == attempts - 1:
                    break
                sleep_s = min(self.backoff_max, self.backoff_base * (2 ** i))
                jitter = sleep_s * (0.1 * (2 * random.random() - 1.0))  # ±10%
                if self.verbose:
                    print(f"[retry {i+1}/{attempts-1}] {model} error: {e} — sleeping {max(0.0, sleep_s + jitter):.2f}s", flush=True)
                time.sleep(max(0.0, sleep_s + jitter))
        raise last_err  # fail after retries

    def _ask_model(self, model: str, prompt: str, max_tokens: int, model_output: Any, ground_truth: Any):
        api_base, headers, temperature = self._resolve_per_model(model)

        content = self._attempt_completion(
            model=model,
            api_base=api_base,
            headers=headers,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Use the instance parser
        parsed = self.output_parser(content)

        # If parser returns None and fallback is enabled, do string comparison
        if parsed is None and self.fallback_comparison:
            return str(model_output).strip() == str(ground_truth).strip()

        return parsed

    def judge(
        self,
        input: Any = None,
        model_output: Any = None,
        ground_truth: Any = None,
        prompt: Optional[str] = None,
        max_tokens: int = 10000,
    ):
        # Validation for fully_custom_prompt mode
        if self.use_fully_custom_prompt:
            if prompt is None:
                raise ValueError(
                    "When use_fully_custom_prompt=True, you must pass prompt to judge()."
                )
            if input is not None or model_output is not None or ground_truth is not None:
                raise ValueError(
                    "When use_fully_custom_prompt=True, you cannot pass input, model_output, or ground_truth to judge(). "
                    "Only pass the complete prompt."
                )
        elif prompt is not None:
            raise ValueError(
                "prompt parameter can only be used when use_fully_custom_prompt=True. "
                "Otherwise, use input/model_output/ground_truth."
            )
        else:
            prompt = self._build_prompt(input, model_output, ground_truth)

        votes = []

        # Vote with litellm models
        for m in self.models:
            res = self._ask_model(m, prompt, max_tokens, model_output, ground_truth)
            if self.verbose:
                print(f"Model {m} voted: {res}", flush=True)
            votes.append({"model": m, "correct": res})

        # Vote with custom generation functions
        for idx, custom_fn in enumerate(self.custom_generation_fns):
            try:
                content = custom_fn(prompt)
                parsed = self.output_parser(content)

                # If parser returns None and fallback is enabled, do string comparison
                if parsed is None and self.fallback_comparison:
                    res = str(model_output).strip() == str(ground_truth).strip()
                else:
                    res = parsed

                if self.verbose:
                    print(f"Custom function {idx} voted: {res}", flush=True)
                votes.append({"model": f"custom_fn_{idx}", "correct": res})
            except Exception as e:
                if self.verbose:
                    print(f"Custom function {idx} failed: {e}", flush=True)
                # If custom function fails and fallback is enabled, do string comparison
                if self.fallback_comparison:
                    res = str(model_output).strip() == str(ground_truth).strip()
                    votes.append({"model": f"custom_fn_{idx}", "correct": res})
                else:
                    raise

        if self.mode == "single":
            final = votes[0]["correct"]
        elif self.mode == "majority":
            true_votes = sum(v["correct"] for v in votes)
            false_votes = len(votes) - true_votes
            final = True if true_votes >= false_votes else False
        elif self.mode == "all":
            final = all(v["correct"] for v in votes)
        else:
            raise ValueError("mode must be 'majority', 'single', or 'all'")

        return {"correct": final, "mode": self.mode, "votes": votes}

