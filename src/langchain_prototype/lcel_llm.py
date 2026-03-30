"""
LCEL LLM Factory für LangChain-Prototyp

Erzeugt ChatOpenAI korrekt für OpenAI- oder BFH-Provider.

Scope: Nur für LangChain-LCEL-Chains (langchain_prototype/).
Nicht verwenden in LangGraph-Nodes oder Hybrid-Nodes — die nutzen
common.llm_handler.get_llm_handler() direkt.

_extract_json ist ein Rückwärts-Kompatibilitäts-Alias für common.utils.extract_json.
"""
from typing import Optional

from langchain_openai import ChatOpenAI

from common.config import Config
from common.logger import setup_logger
from common.utils import extract_json as _extract_json  # backward-compat re-export

logger = setup_logger(__name__)


def _resolve_provider() -> str:
    """Bestimmt den aktiven Provider aus Config oder Auto-Detection."""
    provider = Config.LLM_PROVIDER or "auto"
    if provider != "auto":
        return provider
    # Auto-Detection: BFH-Key hat Vorrang
    if Config.BFH_LLM_API_KEY:
        logger.info("LCEL Auto-detect: BFH-LLM Token gefunden → BFH")
        return "bfh"
    if Config.OPENAI_API_KEY:
        logger.info("LCEL Auto-detect: OpenAI Token gefunden → OpenAI")
        return "openai"
    raise ValueError(
        "Kein LLM-Token gefunden! "
        "Setze OPENAI_API_KEY oder BFH_LLM_API_KEY in .env.dev"
    )


def get_lcel_llm(
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> ChatOpenAI:
    """
    Factory: gibt ChatOpenAI zurück – konfiguriert für OpenAI oder BFH.

    Der BFH-Endpoint ist OpenAI-kompatibel; ChatOpenAI wird daher für beide
    Provider verwendet, wobei bei BFH base_url und ein abweichendes Modell
    gesetzt werden.

    Args:
        temperature: LLM-Temperatur (0.0–1.0)
        max_tokens:  Optionales Token-Limit

    Returns:
        ChatOpenAI-Instanz (echte LangChain-Komponente)
    """
    provider = _resolve_provider()

    kwargs: dict = {"temperature": temperature}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    if provider == "openai":
        if not Config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY nicht gesetzt! "
                "Trage deinen Key in .env.dev ein."
            )
        model = Config.OPENAI_MODEL or "gpt-4o-mini"
        logger.debug(f"LCEL LLM: OpenAI ({model}, temp={temperature})")
        return ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=model,
            **kwargs,
        )

    if provider == "bfh":
        if not Config.BFH_LLM_API_KEY:
            raise ValueError(
                "BFH_LLM_API_KEY nicht gesetzt! "
                "Trage deinen BFH PAT in .env.dev ein."
            )
        model = Config.BFH_LLM_MODEL or "gpt-oss:120b"
        logger.debug(f"LCEL LLM: BFH ({model}, temp={temperature})")
        return ChatOpenAI(
            api_key=Config.BFH_LLM_API_KEY,
            base_url=Config.BFH_LLM_ENDPOINT,
            model=model,
            **kwargs,
        )

    raise ValueError(
        f"Unbekannter Provider: '{provider}'. Nutze 'openai' oder 'bfh'."
    )


