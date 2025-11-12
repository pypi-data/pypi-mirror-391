import re

def markdown_to_rich_markup(text: str) -> str:
    result = text
    # Use [^\*] to prevent matching across multiple ** markers
    result = re.sub(r'\*\*([^\*]+?)\*\*', r'[bold]\1[/bold]', result)
    result = re.sub(r'(?<!\*)\*(?!\*)([^\*]+?)\*(?!\*)', r'[italic]\1[/italic]', result)
    # Removed underscore italic pattern to prevent breaking identifiers like ask_followup_question
    # result = re.sub(r'_(.+?)_', r'[italic]\1[/italic]', result)
    result = re.sub(r'`([^`]+)`', r'[cyan]\1[/cyan]', result)
    result = re.sub(r'~~(.+?)~~', r'[strike]\1[/strike]', result)
    return result

