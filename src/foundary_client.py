from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    AssistantMessage,
    ChatCompletionsToolsDefinition,
    FunctionDefinition,
    SystemMessage,
    UserMessage
    ToolMessage
)
from azure.core.credentials import AzureKeyCredential

from src.config import AZURE_AI_ENDPOINT, AZURE_AI_KEY, PRIMARY_MODEL
from src.cost_tracker import log_cost

client = ChatCompletionsClient(
    endpoint=AZURE_AI_ENDPOINT,
    credential=AzureKeyCredential(AZURE_AI_KEY)
)

def ask_ai(
    system_message: str,
    user_prompt: str,
    model: str = None,
    temperature : float = 0.2,
    feature: str = "general"
):
    
    selected_model = model or PRIMARY_MODEL
    
    response = client.complete(
        model=selected_model,
        messages=[
            SystemMessage(content=system_message),
            UserMessage(content=user_prompt)
        ],
        temperature=temperature,
    )
    
    answer = response.choices[0].message.content

    usage = getattr(response, "usage", None)
    
    input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
    
    log_cost(
        feature=feature,
        model=selected_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
    
    return answer


def ask_ai_with_tools(
    system_prompt,
    user_prompt,
    tools,
    tool_executor,
    model=None,
    temperature=0.1,
    feature="tool_calling",
    max_rounds=6,
):
    selected_model = model or PRIMARY_MODEL

    tool_definitions = [
        ChatCompletionsToolsDefinition(
            function=FunctionDefinition(
                name=tool["name"],
                description=tool["description"],
                parameters=tool["parameters"]
            )
        )
        
        for tool in tools
    ]
    
    messages = [
        SystemMessage(content=system_prompt),
        UserMessage(content=user_prompt)
    ]
    
    for _ in range(max_rounds):
        response = client.complete(
            model=selected_model,
            messages=messages,
            tools=tool_definitions,            
            temperature=temperature
        )
        
        answer = response.choices[0].message.content
        messages.append(UserMessage(content=answer))
        
        usage = getattr(response, "usage", None)
        
        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        
        log_cost(
            feature=feature,
            model=selected_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)
        
        if not tool_calls:
            return message.content or ""

    
    