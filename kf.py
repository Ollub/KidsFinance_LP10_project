from app import app, db
from app.models import User, Task, Role, Group

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Task': Task, 'Role': Role, 'Group': Group}

if __name__ == '__main__':
    app.run()