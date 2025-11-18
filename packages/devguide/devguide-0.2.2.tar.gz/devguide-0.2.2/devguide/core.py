import os
import sys
import json
from .db.repository import Repository
from .recommender import Recommender
from .utils import pretty_print_project
from .db.database import init_db

def handle_recommendation(projects: list, desc: str):
    """Lida com a lógica de recomendação."""
    rec = Recommender(projects)
    result = rec.recommend(desc)
    if result:
        pretty_print_project(result)
    else:
        print("Nenhuma recomendação encontrada com similaridade suficiente.")

def handle_start(projects: list, desc: str = None):
    """Lida com o comando start."""
    if not desc:
        try:
            print("degite a descrição do projeto:")
            desc = input("> ").strip()
        except KeyboardInterrupt:
            print("\nOperação cancelada.")
            sys.exit(0)
    handle_recommendation(projects, desc)

def handle_list(projects: list):
    """Lida com o comando list."""
    print("projeto no banco de ideias:")
    for i, p in enumerate(projects, 1):
        print(f"{i}. {p['title']} - tags: {', '.join(p['tags'])}")

def handle_add(repo: Repository, args):
    """Lida com o comando add."""
    repo.add(args.title, args.tags, args.stack, args.steps)
    print(f"Projeto '{args.title}' adicionado com sucesso!")

def handle_show(repo: Repository, project_id: int):
    """Lida com o comando show."""
    project = repo.get_by_id(project_id)
    if project:
        pretty_print_project(project)
    else:
        print(f"Projeto com ID {project_id} não encontrado.")

def handle_update(repo: Repository, args):
    """Lida com o comando update."""
    repo.update(
        args.project_id,
        title=args.title,
        tags=args.tags,
        stack=args.stack,
        steps=args.steps
    )
    print(f"Projeto com ID {args.project_id} atualizado com sucesso!")

def handle_delete(repo: Repository, project_id: int):
    """Lida com o comando delete."""
    repo.delete(project_id)
    print(f"Projeto com ID {project_id} removido com sucesso!")

def handle_init_db(repo: Repository):
    """Lida com o comando init-db."""
    print("Recriando o banco de dados...")
    init_db()
    print("Banco de dados recriado.")

    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'projects.json'))
    print(f"DEBUG: Lendo arquivo JSON de: {json_path}")
    print(f"DEBUG: Arquivo existe? {os.path.exists(json_path)}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"DEBUG: Total de projetos no JSON: {len(data)}")
    
    imported_count = 0
    for i, p in enumerate(data, 1):
        try:
            repo.add(
                p["title"],
                ",".join(p["tags"]),
                ",".join(p["stack"]),
                "\n".join(p["steps"])
            )
            imported_count += 1
            if i % 10 == 0:
                print(f"DEBUG: Importados {i} projetos até agora...")
        except Exception as e:
            print(f"ERRO ao importar projeto {i} ('{p.get('title', 'UNKNOWN')}'): {e}")
    
    print(f"Importação completa! Total importado: {imported_count}/{len(data)} projetos")
