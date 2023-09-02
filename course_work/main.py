import requests
from pprint import pprint
import json
import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


class ImportPhotos:
    def __init__(self, user_id):
        self.user_id = user_id
        self.token_ya = token_ya
        self.photo_w = {}
        self.count_value = {}
        self.result_json = []

    def get_statistic_photo(self):
        with open('vk_token.txt', 'r') as file:
            vk_token = file.read().strip()
        params = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'access_token': vk_token,
            'photo_sizes': 1,
            'extended': 1,
            'v': '5.131'
        }
        vk_photo = requests.get('https://api.vk.com/method/photos.get', params=params)
        size_dict = {'s': 1, 'm': 2, 'x': 3, "o": 4, 'p': 5, 'q': 6, 'r': 7, 'y': 8, 'z': 9, 'w': 10}
        filt_size_dict = {k: v for k, v in sorted(size_dict.items(), key=lambda item: item[1])}

        try:
            while len(self.photo_w) != 5:
                h_size = filt_size_dict.popitem()[0]
                for i in json.loads(vk_photo.text)['response']['items']:
                    for j in i['sizes']:
                        if j['type'] == h_size and len(self.photo_w) != 5:
                            self.photo_w[j['url']] = [j['type']] + [str(i['likes']['count'])] + [str(i['date'])]
                            logging.info(
                                f"in dict photo_w has been added photo {j['url']} with a resolution {j['type']}.")
        except KeyError:
            logging.exception("it looks like you don't have any photos")
        return self.photo_w

    def post_to_ya(self):
        photo_w = self.get_statistic_photo()
        params_folder = {'path': 'Logunov folder'}
        headers_folder = {'Authorization': self.token_ya}
        try:
            response_folder = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                                           headers=headers_folder, params=params_folder)
            logging.info(
                f"The folder {params_folder['path']} has been created with code status {response_folder.status_code}")
        except:
            logging.info('error when creating a folder')

        for key, value in photo_w.items():
            if value[1] not in self.count_value:
                self.count_value[value[1]] = 1
            else:
                self.count_value[value[1]] += 1

        for key, value in photo_w.items():
            try:
                if self.count_value[value[1]] == 1:
                    params = {'path': params_folder['path'] + '/' + value[1] + '.png',
                              'url': key}
                else:
                    params = {'path': params_folder['path'] + '/' + value[1] + '_' + value[2] + '.png',
                              'url': key}
                headers = {'Authorization': self.token_ya}
                response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                         headers=headers, params=params)
                self.result_json.append({'file_name': params['path'].split('/')[-1], 'size': value[0]})
                logging.info(f"photo {key} has been added with code status - {response.status_code}")
            except:
                logging.info(f"error")
        return self.result_json


if __name__ == '__main__':
    id_vk = input('enter the VK user id')
    with open("ya_token.txt", 'r') as file_token_ya:
        token_ya = file_token_ya.read()
    uploader = ImportPhotos(id_vk)
    res = uploader.post_to_ya()
    pprint(res)
