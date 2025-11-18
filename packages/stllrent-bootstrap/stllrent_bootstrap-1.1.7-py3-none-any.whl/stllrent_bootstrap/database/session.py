import contextlib

@contextlib.contextmanager
def get_db_session():
    """
    Fornece uma sessão de banco de dados a partir do DatabaseManager central.
    Este método é agnóstico de contexto:
    1. Tenta obter o db_manager do contexto da aplicação Flask (para requisições web e testes).
    2. Se não houver um contexto Flask, recorre à instância global do db_manager (para workers Celery).
    """
    try:
        # Abordagem para o contexto Flask
        from flask import current_app
        db_manager = current_app.extensions["db_manager"]
    except RuntimeError:
        # Fallback para o contexto não-Flask (ex: Celery)
        # Importa a instância global apenas quando necessário.
        from stllrent_bootstrap.database.manager import db_manager

    with db_manager.get_session() as session:
        yield session