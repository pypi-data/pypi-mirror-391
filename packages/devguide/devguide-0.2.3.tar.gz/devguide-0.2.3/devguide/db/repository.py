from .database import get_conn

class Repository:
    def get_all(self):
        """Retorna todos os projetos do banco de dados."""
        with get_conn() as conn:
            cursor = conn.execute("SELECT id, title, tags, stack, steps FROM projects")
            projects = []
            for row in cursor:
                projects.append({
                    "id": row[0],
                    "title": row[1],
                    "tags": row[2].split(",") if row[2] else [],
                    "stack": row[3].split(",") if row[3] else [],
                    "steps": row[4].split("\n") if row[4] else []
                })
            return projects

    def get_by_id(self, project_id: int):
        """Busca um projeto pelo seu ID."""
        with get_conn() as conn:
            cursor = conn.execute("SELECT id, title, tags, stack, steps FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "tags": row[2].split(",") if row[2] else [],
                    "stack": row[3].split(",") if row[3] else [],
                    "steps": row[4].split("\n") if row[4] else []
                }
            return None

    def add(self, title: str, tags: str, stack: str, steps: str):
        """Adiciona um novo projeto ao banco de dados."""
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO projects (title, tags, stack, steps) VALUES (?, ?, ?, ?)",
                (title, tags, stack, steps)
            )
            conn.commit()

    def update(self, project_id: int, title: str = None, tags: str = None, stack: str = None, steps: str = None):
        """Atualiza um projeto existente."""
        fields_to_update = []
        params = []

        if title is not None:
            fields_to_update.append("title = ?")
            params.append(title)
        if tags is not None:
            fields_to_update.append("tags = ?")
            params.append(tags)
        if stack is not None:
            fields_to_update.append("stack = ?")
            params.append(stack)
        if steps is not None:
            fields_to_update.append("steps = ?")
            params.append(steps)

        if not fields_to_update:
            return

        params.append(project_id)
        
        with get_conn() as conn:
            conn.execute(
                f"UPDATE projects SET {', '.join(fields_to_update)} WHERE id = ?",
                tuple(params)
            )
            conn.commit()

    def delete(self, project_id: int):
        """Deleta um projeto do banco de dados."""
        with get_conn() as conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
