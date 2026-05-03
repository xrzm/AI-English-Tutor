from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.schemas.speaking import AnalysisResult
from app.services.qwen_clients import get_chat_llm


class SpeakingAnalysisOutput(BaseModel):
    grammar_errors: List[str] = Field(description="语法错误列表")
    suggestions: List[str] = Field(description="改进建议")
    improved_version: str = Field(description="改进后的版本")


class SpeakingPartner:
    level_prompts = {
        "beginner": "使用简单词汇和短句，语速慢，多重复",
        "intermediate": "使用日常词汇，适当使用从句",
        "advanced": "使用丰富词汇，复杂句式，地道表达",
    }

    def __init__(self, level: str = "intermediate", history: List[dict] | None = None):
        self.llm = get_chat_llm(temperature=0.7)
        self.level = level
        self.history = history or []
        self.system_prompt = f"""You are a friendly and patient English speaking tutor.

Student level: {level}
Teaching style: {self.level_prompts.get(level, self.level_prompts['intermediate'])}

Your role:
1. Have natural, engaging English conversations with the student
2. Gently correct grammar, vocabulary, and pronunciation errors by providing the correct form in parentheses, e.g., "I have went (gone) to the store"
3. Encourage the student to speak more by asking follow-up questions
4. Provide useful vocabulary and expressions when appropriate
5. Keep the conversation fun, interesting, and educational

Conversation topics: daily life, hobbies, travel, study, work, culture, food, technology, etc.

Important rules:
- Always respond in English (unless the student is really struggling, then briefly explain in Chinese)
- Keep responses concise (2-4 sentences) so the student has room to respond
- Match your language complexity to the student's level
- If the student's sentence has obvious errors, briefly point out 1-2 corrections max per response"""

    def _history_messages(self):
        messages = []
        for item in self.history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "human":
                messages.append(HumanMessage(content=content))
            elif role == "ai":
                messages.append(AIMessage(content=content))
        return messages

    # ✅ 修复：缩进进 class
    def chat(self, user_input: str) -> str:
        try:
            messages = [SystemMessage(content=self.system_prompt)]
            messages.extend(self._history_messages())
            messages.append(HumanMessage(content=user_input))

            response = self.llm.invoke(messages)
            ai_response = response.content

            self.history.append({"role": "human", "content": user_input})
            self.history.append({"role": "ai", "content": ai_response})

            return ai_response

        except Exception as e:
            import traceback
            print("SPEAKING PARTNER ERROR:")
            traceback.print_exc()
            raise

    # ✅ 修复：缩进进 class（且不在 chat 里面）
    def analyze_speaking(self, text: str) -> AnalysisResult:
        parser = PydanticOutputParser(pydantic_object=SpeakingAnalysisOutput)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an English speaking analyst. Analyze the student's spoken English and provide feedback.

{format_instructions}

Analysis guidelines:
- grammar_errors: List specific grammar/vocabulary/usage errors found. If none, return empty list.
- suggestions: List 1-3 practical tips for improvement (fluency, word choice, natural expression, etc.)
- improved_version: A polished version of the student's sentence that sounds natural and correct, keeping the original meaning.""",
                ),
                ("user", "Analyze this English sentence:\n{text}"),
            ]
        )
        chain = prompt | self.llm | parser
        result = chain.invoke({"format_instructions": parser.get_format_instructions(), "text": text})
        return AnalysisResult(**result.model_dump())
