from pydantic import BaseModel, Field
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import extract_events_string, default_extract_strings


class RecallResultsModels(BaseModel):
    recalled_episode: str = Field(
        ...,
        description="从历史记忆中提取的与当前情况最相关的具体经验或模式",
    )
    current_situation: str = Field(
        ...,
        description="结合历史上下文后对当前情境的深化理解",
    )


associative_recall_system_template = """将**当前情况**与**历史记忆**进行智能关联，找出有用的经验和模式，更好地理解现状。

【当前情境】
{{current_situation}}

【刚才的对话和事件】
{{recent_events}}

【相关的历史记忆】
{{episodic_memories}}

【你正在做的事】
{{active_goals}}"""


associative_recall_template = f"""
<|im_start|>system
{associative_recall_system_template}
<|im_end|>
<|im_start|>assistant
"""


def create_associative_recall_output_json_template(examples: str):
    PromptTemplate(
        template="""请严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

- `recalled_episode`: 字符串。从历史记忆中提取的与当前情况**最相关**的具体经验、事件或行为模式。请描述具体的记忆内容。

- `current_situation`: 字符串。在结合历史经验和上下文后，对**当前情境的深化理解和分析**。说明历史经验如何影响对现状的理解。

# 输出示例
```json
{examples}""",
        variables={"examples": examples},
    )


def associative_recall_task_format_inputs(inputs):
    return {
        "current_situation": inputs.get("current_situation", "未知"),
        # TODO: 增加时间
        "recent_events": extract_events_string(inputs.get("recent_events", [])),
        "episodic_memories": default_extract_strings(
            inputs.get("episodic_memories", []), "content"
        ),
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
    }
