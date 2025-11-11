import numpy as np
from typing import Literal
from .utils import get_lindormai_async_client_instance
from ..config import LOG


async def lindormai_embedding(
        model: str,
        texts: list[str],
        phase: Literal["query", "document"] = "document",
        config=None
) -> np.ndarray:
    """Lindormai Embedding 请求

    Args:
        model: 模型名称，如 "text-embedding-v1" 或其他 Lindormai 支持的 embedding 模型
        texts: 要转换的文本列表
        phase: 阶段标识，用于日志记录（"query" 或 "document"）
        config: 配置字典

    Returns:
        np.ndarray: embedding 向量数组，shape 为 (len(texts), embedding_dim)
    """
    lindormai_async_client = get_lindormai_async_client_instance(config)

    try:
        response = await lindormai_async_client.embeddings.create(
            model=model,
            input=texts,
            encoding_format="float"
        )

        prompt_tokens = getattr(response.usage, "prompt_tokens", None)
        total_tokens = getattr(response.usage, "total_tokens", None)
        LOG.info(f"Lindormai embedding, {model}, {phase}, {prompt_tokens}/{total_tokens}")

        return np.array([dp.embedding for dp in response.data])

    except Exception as e:
        LOG.error(f"Error in Lindormai embedding: {e}")
        raise
    finally:
        await lindormai_async_client.close()