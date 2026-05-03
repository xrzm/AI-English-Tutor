import base64
from typing import List, Optional, Any

import dashscope
from dashscope import Generation
from dashscope import MultiModalConversation
from dashscope.audio.tts import SpeechSynthesizer

# LangChain Core  imports for compatibility
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun

from app.core.config import settings

# 设置全局 API Key
dashscope.api_key = settings.DASHSCOPE_API_KEY


def get_chat_llm(temperature=0.7):
    """
    返回一个兼容 LangChain Runnable 协议的 LLM 实例
    """
    dashscope.api_key = settings.DASHSCOPE_API_KEY

    class SimpleLLM(BaseChatModel):
        """
        自定义 Qwen LLM，继承 BaseChatModel 以支持 LangChain Chain (|) 操作
        """
        
        # 定义模型参数，以便 LangChain 内部识别
        model_name: str = "qwen-plus"
        temperature_val: float = temperature

        @property
        def _llm_type(self) -> str:
            return "simple_qwen_llm"

        def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> ChatResult:
            """
            核心方法：将 LangChain Messages 转换为 DashScope 格式并调用
            """
            # 1. 转换 LangChain Messages -> DashScope 格式
            formatted_messages = []
            for m in messages:
                role = "user"
                if isinstance(m, SystemMessage):
                    role = "system"
                elif isinstance(m, AIMessage):
                    role = "assistant"
                elif isinstance(m, HumanMessage):
                    role = "user"
                else:
                    # 兜底处理
                    role = "user"

                formatted_messages.append({
                    "role": role,
                    "content": m.content
                })

            # 2. 调用 DashScope API
            try:
                resp = Generation.call(
                    model=self.model_name,
                    messages=formatted_messages,
                    temperature=self.temperature_val,
                    result_format="message"
                )
            except Exception as e:
                raise Exception(f"DashScope API call failed: {str(e)}")

            # 3. 检查响应状态
            if resp.status_code != 200:
                raise Exception(f"DashScope error: Code={resp.status_code}, Message={resp.message}")

            # 4. 提取内容
            if not resp.output or not resp.output.choices:
                raise Exception("DashScope returned empty output")
            
            content = resp.output.choices[0].message.content

            # 5. 构造 LangChain 要求的返回对象 (ChatResult)
            generation = ChatGeneration(
                message=AIMessage(content=content),
                generation_info={"finish_reason": resp.output.choices[0].finish_reason}
            )
            
            return ChatResult(generations=[generation])

    # 返回实例化后的对象
    return SimpleLLM()


def multimodal_call(model: str, content: List[dict]) -> str:
    response = MultiModalConversation.call(
        model=model,
        messages=[{"role": "user", "content": content}],
    )
    # 增加健壮性检查
    if response.status_code != 200:
        raise Exception(f"Multimodal call failed: {response.message}")
    return response.output.choices[0].message.content[0]["text"]


def ocr_image_bytes(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return multimodal_call(
        model=settings.QWEN_OCR_MODEL,
        content=[
            {"image": f"data:{mime_type};base64,{image_base64}"},
            {"text": "请识别图片中的文字内容，包括题目和学生的答案。"},
        ],
    )


def speech_to_text_from_wav_bytes(audio_bytes: bytes) -> str:
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    return multimodal_call(
        model=settings.QWEN_AUDIO_MODEL,
        content=[
            {"audio": f"data:audio/wav;base64,{audio_base64}"},
            {"text": "请将这段语音转换为文字。"},
        ],
    )


def text_to_speech_bytes(text: str) -> bytes:
    result = SpeechSynthesizer.call(
        model=settings.QWEN_TTS_MODEL,
        text=text,
        sample_rate=16000,
        format="wav",
    )
    # 增加健壮性检查
    if result.status_code != 200:
        raise Exception(f"TTS failed: {result.message}")
    return result.get_audio_data()

