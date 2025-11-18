from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import unicodedata

def normalize_text(text):
    """Remove acentos e normaliza o texto."""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

LOGO = r"""
  ____            _           _   
 |  _ \  ___  ___| | ___   __| | __
 | | | |/ _ \/ __| |/ _ \ / _` |/ _` \
 | |_| |  __/\__ \ | (_) | (_| | (_| |
 |____/ \___||___/_|\___/ \__,_|\__,_|
                                    
"""

def pretty_print_project(p: dict):
    console = Console()
    score = p.get("score", 0.0)

    console.print(Text(LOGO, style="bold blue"))

    # Painel principal
    content = Text()
    content.append("Projeto: ", style="bold green")
    content.append(p.get("title", "—"), style="white")
    if score > 0:
        content.append(f"\nSimilaridade (0..1): {score:.3f}", style="dim")

    console.print(Panel(content, title="[bold cyan]Recomendação Encontrada[/bold cyan]", border_style="cyan"))

    # Painel de Stack
    stack = p.get("stack")
    if stack:
        stack_content = Text()
        for item in stack:
            stack_content.append(f"- {item}\n")
        console.print(Panel(stack_content, title="[bold yellow]Sugestão de Stack[/bold yellow]", border_style="yellow"))

    # Painel de Passos
    steps = p.get("steps")
    if steps:
        steps_content = Text()
        for i, step in enumerate(steps, 1):
            steps_content.append(f"{i}. {step}\n")
        console.print(Panel(steps_content, title="[bold magenta]Passos Iniciais[/bold magenta]", border_style="magenta"))

    # Tags
    tags = p.get("tags")
    if tags:
        tags_text = Text("Tags: ", style="bold")
        tags_text.append(", ".join(tags))
        console.print(tags_text)
