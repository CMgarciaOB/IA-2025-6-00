import re
import language_tool_python

# Inicializar LanguageTool para español
_tool = language_tool_python.LanguageTool("es")

def _clean_text(text: str) -> str:
    """
    hacemos una normalizacion quitando espacios blancos .
    """
    if text is None:
        return ""

    # Reemplazar espacios por uno
    text = re.sub(r"\s+", " ", text)
    # Normalizamos los saltos de linea quitandolos de inicio o de final
    text = text.strip()
    return text

def _spell_and_grammar_correction(text: str) -> str:
    """
    Correcciónes ortográficas con LanguageTool.
    """
    if not text:
        return text
    matches = _tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected

def postprocess_text(text: str) -> str:
    cleaned = _clean_text(text)
    corrected = _spell_and_grammar_correction(cleaned)
    return corrected