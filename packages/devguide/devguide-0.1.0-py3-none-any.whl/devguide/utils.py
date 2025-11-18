def pretty_print_project(p: dict):
    print("\n✅ Recomendação encontrada:")
    title = p.get("title", "—")
    score = p.get("score", None)
    print(f"Projeto: {title}")
    if score is not None:
        print(f"Similaridade (0..1): {score:.3f}")
    stack = p.get("stack")
    if stack:
        print("\nSugestão de stack:")
        for s in stack:
            print(f" - {s}")
    steps = p.get("steps")
    if steps:
        print("\nPassos iniciais:")
        for i, step in enumerate(steps, 1):
            print(f"{i}. {step}")
    tags = p.get("tags")
    if tags:
        print("\nTags:", ", ".join(tags))
    print()
