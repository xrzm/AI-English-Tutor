from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.schemas.homework import HomeworkErrorItem
from app.services.qwen_clients import get_chat_llm


class HomeworkFeedback(BaseModel):
    score: int = Field(description="分数 0-100")
    strengths: List[str] = Field(description="优点列表")
    errors: List[HomeworkErrorItem] = Field(description="错误列表，包含 location 和 correction")
    suggestions: str = Field(description="改进建议")
    corrected_text: str = Field(description="修改后的完整文本")


class HomeworkGrader:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0.3)
        self.parser = PydanticOutputParser(pydantic_object=HomeworkFeedback)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一位经验丰富的教师，负责批改学生作业。\n\n{format_instructions}\n\n批改要求：\n1. 指出语法、拼写、标点错误\n2. 评估内容质量、逻辑性、创意性\n3. 给出具体的改进建议\n4. 提供修改后的完整文本\n5. 打分要公正，有理有据""",
                ),
                (
                    "user",
                    """科目：{subject}\n题目：{question}\n学生答案：\n{answer}\n\n请批改这份作业。""",
                ),
            ]
        )
        self.chain = self.prompt | self.llm | self.parser

    def grade(self, subject: str, question: str, answer: str) -> HomeworkFeedback:
        return self.chain.invoke(
            {
                "format_instructions": self.parser.get_format_instructions(),
                "subject": subject,
                "question": question,
                "answer": answer,
            }
        )
