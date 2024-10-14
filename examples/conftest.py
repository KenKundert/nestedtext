def pytest_ignore_collect(collection_path):
    components = collection_path.parts
    name = components[-1]
    if name.startswith('deploy_') and name.endswith('.py'):
        return True
    if name == 'example.py':
        return True
