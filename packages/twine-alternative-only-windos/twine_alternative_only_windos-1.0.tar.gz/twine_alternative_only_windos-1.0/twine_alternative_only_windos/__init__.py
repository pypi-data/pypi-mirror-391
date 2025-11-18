print('Понимаю. Я подтверждаю, что я не имел никакого соучастия с создания официального twine, но при этом этот проект был сделан из-за того, что фичи оригинального twine просто не работали у меня на одиннадцатый Windows.')
import os
class twine ():
    def __init__(self, token, path):
        self.token = token
        self.path = path
    def apdate(self):
        with open('install.cmd', 'w', encoding='UTF-8') as f:
            f.write(f'python3 -m pip install --upgrade build\npython3 -m build\npython3 -m pip install --upgrade twine')
        os.system('install.cmd')
        os.remove('install.cmd')
        with open('twine.cmd', 'w', encoding='UTF-8') as fa:
            fa.write(f'cd {self.path}\nsetx TWINE_USERNAME __token__\nsetx TWINE_PASSWORD {self.token}\npython setup.py sdist\npython -m twine upload dist/*')
        os.system('twine.cmd')
        os.remove('twine.cmd')