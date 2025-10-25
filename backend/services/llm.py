import os
from typing import List
from models.generation import Generation
from models.template import Template
from models.questions import Question
from openai import OpenAI

def render_template(template: Template, question: Question) -> str:
    return template.template_text.replace("{{question}}", question.text)


def generate_output(template: Template, question: Question, client: OpenAI = None) -> str:
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        client = OpenAI(api_key=api_key)
    template_text = render_template(template, question)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": template_text}]
    )
    return {
        "output_text": response.choices[0].message.content,
        "latency": response.usage.completion_tokens / 150,
        "output_tokens": response.usage.completion_tokens,
        "input_tokens": response.usage.prompt_tokens,
        "llm_model": "gpt-4o-mini",
    }    

def generate_outputs(templates: List[Template], question: Question, client: OpenAI = None) -> List[Generation]:
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        client = OpenAI(api_key=api_key)
    outputs = []
    for template in templates:
        output = generate_output(template, question, client)
        outputs.append(Generation(
            template_id=template.id,
            question_id=question.id,
            output_text=output["output_text"],
            llm_model="gpt-4o-mini",
            latency=output["latency"],
            output_tokens=output["output_tokens"],
            input_tokens=output["input_tokens"],
        ))
    return outputs