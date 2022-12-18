import pytest
import requests
import datetime
from settings import *


@pytest.fixture(scope="class")
def get_key(request):
    response = requests.post(url=f"{base_url}login", data={"email": valid_email, "pass": valid_password})
    assert response.status_code == 200, 'Запрос выполнен неуспешно'
    assert 'Cookie' in response.request.headers, 'В запросе не передан ключ авторизации'
    print(request.fixturename, "-->", "it`s had return the 'auth_key'")
    return response.request.headers.get('Cookie')


@pytest.fixture(autouse=True)
def request_fixture(request):
    if 'Pets' in request.function.__name__:
        print(f"\nЗапущен тест из сьюта Дом Питомца: {request.function.__name__}")


@pytest.fixture(autouse=True)
def time_delta():
    start_time = datetime.datetime.now()
    yield
    end_time = datetime.datetime.now()
    print(f"\nТест шел: {end_time - start_time}")


def logger(func):
    def wrapper(*args, **kwargs):
        file_content = ('\n<{}>  <{}>\n'.format(func.__name__, args))
        with open('log.txt', 'a', encoding='utf8') as file:
            file_content += str(func(*args, **kwargs))
            file.write(file_content)
        return func(*args, **kwargs)

    return wrapper


@logger
def request_get(headers, params):
    res = requests.get(f'{base_url}api/pets', headers=headers, params=params)
    status = res.status_code
    result = res.json()
    return status, result


class TestClassPets:
    pass

    def test_get_all_pets(self, get_key):
        """" Тестируем GET запрос на получения API-key """
        response = requests.get(url=f"{base_url}api/pets", headers={"Cookie": get_key})

        assert response.status_code == 200, 'Запрос выполнен неуспешно'
        assert response.headers.get('content-type') == 'application/json', 'Не наш контент'
        assert len(response.json().get('pets')) > 0, 'Количество питомцев не соответствует ожиданиям'

    def test_get_my_pets(self, get_key):
        """" Тестируем GET запрос на получения списка своих питомцев """
        response = requests.get(url=f"{base_url}api/pets?filter=my_pets", headers={"Cookie": get_key})

        assert response.status_code == 200, 'Запрос выполнен неуспешно'
        assert response.headers.get('content-type') == 'application/json', 'Не наш контент'
        assert len(response.json().get('pets')) > 0, 'Количество питомцев не соответствует ожиданиям'

    def test_add_pet(self, get_key):
        """" Тестируем POST запрос на добавление нового питомца без фото """
        add_pet = dict(name='Даффи', animal_type='утка', age=0)
        response = requests.post(url=f"{base_url}api/create_pet_simple", headers={"Cookie": get_key}, data=add_pet)

        assert response.status_code == 200, 'Запрос выполнен неуспешно'
        assert response.headers.get('content-type') == 'text/html; charset=utf-8', 'Пет не добавился!'

    def test_add_pet_with_photo(self, get_key):
        """" Тестируем POST запрос на добавление нового питомца с фото """
        add_pet = dict(name='Даффи', animal_type='утка', age=0, pet_photo='image/ducky.jpg')
        response = requests.post(url=f"{base_url}api/pets", headers={"Cookie": get_key}, data=add_pet)

        assert response.status_code == 200, 'Запрос выполнен неуспешно'
        assert response.headers.get('content-type') == 'text/html; charset=utf-8', 'Пет не добавился!'
