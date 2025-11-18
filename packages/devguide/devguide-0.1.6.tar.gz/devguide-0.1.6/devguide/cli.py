
import argparse
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
from devguide.db.repository import Repository
from devguide.db.database import db_exists
from devguide import core

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="devguide",
        description="devGuide CLI - ajuda para planejar projetos a partir de uma descrição."
    )
    
    sub = parser.add_subparsers(dest="command", required=True)

    # comando start (interativo)
    parser_start = sub.add_parser("start", help="Inicia o assistente interativo")
    parser_start.add_argument("--desc", "-d", type=str, help="Descrição do projeto")
    

    # comando recommend (recomendação) - não interativo
    parser_recommend = sub.add_parser("recommend", help="Recomenda projetos a partir de uma descrição")
    parser_recommend.add_argument("--desc", "-d", type=str, help="Descrição do projeto")
    
    # comando list para listar projetos da base
    parser_list = sub.add_parser("list", help="Lista projetos já no banco de ideias")

    # comando add para adicionar um novo projeto
    parser_add = sub.add_parser("add", help="Adiciona um novo projeto")
    parser_add.add_argument("--title", required=True, help="Título do projeto")
    parser_add.add_argument("--tags", help="Tags separadas por vírgula")
    parser_add.add_argument("--stack", help="Stack separada por vírgula")
    parser_add.add_argument("--steps", help="Passos separados por vírgula")

    # comando show para ver um projeto
    parser_show = sub.add_parser("show", help="Mostra os detalhes de um projeto")
    parser_show.add_argument("project_id", type=int, help="ID do projeto")

    # comando update para atualizar um projeto
    parser_update = sub.add_parser("update", help="Atualiza um projeto existente")
    parser_update.add_argument("project_id", type=int, help="ID do projeto")
    parser_update.add_argument("--title", help="Novo título do projeto")
    parser_update.add_argument("--tags", help="Novas tags separadas por vírgula")
    parser_update.add_argument("--stack", help="Nova stack separada por vírgula")
    parser_update.add_argument("--steps", help="Novos passos separados por vírgula")

    # comando delete para remover um projeto
    parser_delete = sub.add_parser("delete", help="Remove um projeto existente")
    parser_delete.add_argument("project_id", type=int, help="ID do projeto")

    # comando init-db para inicializar o banco de dados
    sub.add_parser("init-db", help="Inicializa o banco de dados com dados de exemplo")

    args = parser.parse_args(argv)

    # Verifica se o banco de dados existe antes de rodar qualquer comando, exceto init-db
    if args.command != "init-db" and not db_exists():
        print("Banco de dados não encontrado.")
        print("Por favor, execute 'devguide init-db' para criar o banco de dados inicial.")
        return

    repo = Repository()

    if args.command in ["start", "recommend", "list"]:
        projects = repo.get_all()
        if args.command == "start":
            core.handle_start(projects, args.desc)
        elif args.command == "recommend":
            core.handle_recommendation(projects, args.desc)
        elif args.command == "list":
            core.handle_list(projects)
    elif args.command == "add":
        core.handle_add(repo, args)
    elif args.command == "show":
        core.handle_show(repo, args.project_id)
    elif args.command == "update":
        core.handle_update(repo, args)
    elif args.command == "delete":
        core.handle_delete(repo, args.project_id)
    elif args.command == "init-db":
        core.handle_init_db(repo)

if __name__ == "__main__":
    main()
    
            