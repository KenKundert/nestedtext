def pytest_ignore_collect(path):
    components = str(path).split('/')
    name = components[-1]
    if name.startswith('deploy_') and name.endswith('.py'):
        return True
