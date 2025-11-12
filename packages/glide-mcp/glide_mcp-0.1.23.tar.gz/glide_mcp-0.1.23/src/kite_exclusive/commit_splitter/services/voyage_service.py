import os

# Lazy-loaded modules - only imported when needed to avoid import errors
# We cannot import helix modules at module level because helix.embedding.__init__.py
# imports gemini_client which requires google.genai
_VoyageAIEmbedder = None
_Chunk = None
_voyage_embedder = None


def _import_helix_modules():
    """Lazy import helix modules to avoid import errors if optional dependencies are missing.
    
    This function will fail if google-generativeai is not installed, but the error
    will only occur when embed_code() is called, not when this module is imported.
    """
    global _VoyageAIEmbedder, _Chunk
    
    if _VoyageAIEmbedder is None or _Chunk is None:
        try:
            # Import helix modules - this will trigger helix.embedding.__init__.py
            # which imports gemini_client, which requires google.genai
            from helix.embedding.voyageai_client import VoyageAIEmbedder as _VoyageAIEmbedder
            from helix import Chunk as _Chunk
        except ImportError as e:
            error_msg = str(e)
            if "google" in error_msg or "genai" in error_msg:
                raise ImportError(
                    "Failed to import helix modules. The 'google' module is missing. "
                    "This is likely because 'google-generativeai' is not installed. "
                    "Please install it with: pip install google-generativeai\n"
                    f"Original error: {e}"
                ) from e
            else:
                raise ImportError(
                    f"Failed to import helix modules. Original error: {e}. "
                    f"Please ensure all helix-py dependencies are installed."
                ) from e
    return _VoyageAIEmbedder, _Chunk


def _get_embedder():
    """Get or create the voyage embedder instance (lazy initialization)."""
    global _voyage_embedder
    if _voyage_embedder is None:
        VoyageAIEmbedder, _ = _import_helix_modules()
        _voyage_embedder = VoyageAIEmbedder()
    return _voyage_embedder


def embed_code(code: str, file_path: str = None):
    # Lazy import Chunk when actually needed
    _, Chunk = _import_helix_modules()
    
    # For diffs, use token_chunk instead of code_chunk since diffs are text format
    # and code_chunk has API compatibility issues
    try:
        # Try code_chunk first if we have a valid language
        if file_path:
            ext = os.path.splitext(file_path)[1].lstrip(".")
            lang_map = {
                "py": "python",
                "js": "javascript",
                "ts": "typescript",
                "jsx": "javascript",
                "tsx": "typescript",
                "java": "java",
                "cpp": "cpp",
                "c": "c",
                "cs": "csharp",
                "go": "go",
                "rs": "rust",
                "rb": "ruby",
                "php": "php",
                "swift": "swift",
                "kt": "kotlin",
                "scala": "scala",
                "sh": "bash",
                "hx": "python",
            }
            language = lang_map.get(ext.lower())
            if language:
                code_chunks = Chunk.code_chunk(code, language=language)
            else:
                code_chunks = Chunk.token_chunk(code)
        else:
            code_chunks = Chunk.token_chunk(code)
    except Exception:
        # Fallback to token_chunk if code_chunk fails
        code_chunks = Chunk.token_chunk(code)

    voyage_embedder = _get_embedder()
    code_embeddings = voyage_embedder.embed_batch([f"{code_chunks}"])

    return code_embeddings
