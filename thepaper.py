from pip._vendor import requests
import json
from datetime import date
# token_VK = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


class YaUploader:
    def __init__(self, user_id, token_vk, count, token, ya_folder):
        self.user_id = user_id
        self.token_vk = token_vk
        self.count = count
        self.token = token
        self.ya_folder = ya_folder
        self.get_new_folder()

    def initiate_process(self):
        if 1 <= int(self.count) <= 500:
            self.count = int(self.count)
            print(f'Выгрузка {self.count} фотографий')
            self.get_response()
        else:
            self.count = 5
            print(f'Выгрузка {self.count} фотографий')
            self.get_response()

    def get_requests(self):
        link = "https://api.vk.com/method/photos.get?"
        params = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'access_token': self.token_vk,
            'v': '5.126'
        }
        response = requests.get(link, params=params)
        if response.status_code != 200:
            print('Ошибка: нет связи с сервером')
        else:
            return response.json()

    def get_response(self):
        counts = 0
        if 'error' in self.get_requests():
            print(f'Ошибка: аккаунт {self.user_id} недоступен')
        elif self.get_requests()['response'].get('count', False) == 0:
            print(f'Ошибка: в аккаунте: {self.user_id} отсутствуют фотографии профиля')
        else:
            info = []
            current_date = date.today()
            for i in self.get_requests()['response']['items']:
                if counts < int(self.count):
                    prep_dict = dict([('file_name', str(i['likes']['count']) + '.jpg'), ('size', i['sizes'][-1]['type'])])
                    print('Загрузка:', i['sizes'][-1]['url'])
                    self.get_photo(str(i['likes']['count']) + str(current_date) + '.jpg', i['sizes'][-1]['url'])
                    info.append(prep_dict)
                    counts += 1
            self.write_json(info)

    def get_photo(self, file_name, url):
        file_path = self.ya_folder + '/' + file_name
        self.upload_file(file_path, url)

    def get_new_folder(self):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
        params = {'path': self.ya_folder, 'overwrite': 'true'}
        response = requests.post(upload_url, headers=headers, params=params)
        if response.status_code != 201:
            print(f'Папка с именем: {self.ya_folder} уже существует')
        else:
            print(f'Папка: {self.ya_folder} создана на Яндекс.Диск')

    def upload_file(self, file_path: str, url):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}
        params = {'url': url, 'path': file_path}
        response = requests.post(upload_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print('Файл успешно загружен на Яндекс.Диск')

    def write_json(self, info):
        with open('files_progress.json', 'a') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    user_id = input('Пожалуйста, введите ID пользователя VK: ')
    token_vk = input('Пожалуйста, введите токен VK: ')
    count = input('Пожалуйста, введите количество фото, которое вы хотите выгрузить (5 по умолчанию-Enter): ')
    token = input('Пожалуйста, введите токен Полигона Яндекс.Диска: ')
    ya_folder = input('Пожалуйста, введите имя папки Яндекс.Диска для загрузки фото: ')
    uploader = YaUploader(user_id, token_vk, count, token, ya_folder)
    uploader.initiate_process()


