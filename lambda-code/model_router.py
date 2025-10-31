from claude_model import invoke_claude_model, create_summary_with_claude
from nova_model import invoke_nova_model, create_summary_with_nova
from gpt_model import invoke_gpt_model, create_summary_with_gpt

def select_tags_with_model(blog_text, filtered_tags, tags_hash, model_id):
    """モデルに応じてタグ選択を実行"""
    if 'anthropic' in model_id:
        return invoke_claude_model(blog_text, filtered_tags, tags_hash, model_id)
    elif 'nova' in model_id:
        return invoke_nova_model(blog_text, filtered_tags, tags_hash, model_id)
    elif 'openai' in model_id:
        return invoke_gpt_model(blog_text, filtered_tags, tags_hash, model_id)
    else:
        raise ValueError(f"Unsupported model: {model_id}")

def create_summary(blog_text, model_id):
    """モデルに応じて要約を作成"""
    if 'anthropic' in model_id:
        return create_summary_with_claude(blog_text, model_id)
    elif 'nova' in model_id:
        return create_summary_with_nova(blog_text, model_id)
    elif 'openai' in model_id:
        return create_summary_with_gpt(blog_text, model_id)
    else:
        raise ValueError(f"Unsupported model for summary: {model_id}")
