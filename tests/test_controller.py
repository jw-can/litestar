import json
from asyncio import sleep
from typing import Any, List, Optional

import pytest
from pydantic import BaseModel, Field
from pydantic_factories import ModelFactory
from starlette.requests import Request
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from starlite import (
    Controller,
    HttpMethod,
    ImproperlyConfiguredException,
    Router,
    delete,
    get,
    patch,
    post,
    put,
)
from starlite.routing import Inject


class Person(BaseModel):
    id: int
    first_name: str
    last_name: str


class QueryParams(BaseModel):
    first: str
    second: List[str] = Field(min_items=3)
    third: Optional[int]


class PersonFactory(ModelFactory):
    __model__ = Person


class QueryParamsFactory(ModelFactory):
    __model__ = QueryParams


person_instance = PersonFactory.build()


def test_controller_raises_exception_when_base_path_not_set():
    class MyController(Controller):
        pass

    with pytest.raises(ImproperlyConfiguredException):
        MyController(owner=Router(path=""))


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_controller_http_method(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self):
            return person_instance

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code
        assert response.json() == person_instance.dict()


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_path_params(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    class MyController(Controller):
        path = test_path

        @decorator(path="/{person_id:int}")
        def test_method(self, person_id: int):
            assert person_id == person_instance.id
            return None

    with create_test_client(MyController) as client:
        response = client.request(http_method, f"{test_path}/{person_instance.id}")
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_query_params(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    query_params_instance = QueryParamsFactory.build()

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self, first: str, second: List[str], third: Optional[int] = None):
            assert first == query_params_instance.first
            assert second == query_params_instance.second
            assert third == query_params_instance.third
            return None

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path, params=query_params_instance.dict())
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_header_params(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    request_headers = {
        "application-type": "web",
        "site": "www.example.com",
        "user-agent": "some-thing",
        "accept": "*/*",
    }

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self, headers: dict):
            for key, value in request_headers.items():
                assert headers[key] == value

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path, headers=request_headers)
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_request(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self, request: Request):
            assert isinstance(request, Request)

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (get, HttpMethod.GET, HTTP_200_OK),
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_dependency_injection(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    def first_dependency(headers: Any):
        assert headers
        return object()

    async def second_dependency(request: Request):
        assert request
        await sleep(0.1)
        return object()

    class MyController(Controller):
        path = test_path
        dependencies = {"first": Inject(first_dependency), "second": Inject(second_dependency)}

        @decorator()
        def test_method(self, first: object, second: object):
            assert first
            assert second
            assert first != second

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code


def test_defining_data_for_get_handler_raises_exception(create_test_client):
    test_path = "/person"

    class MyController(Controller):
        path = test_path

        @get()
        def test_method(self, data: Person):
            assert data == person_instance

    with create_test_client(MyController) as client:
        response = client.get(test_path)
        assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_data_using_model(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self, data: Person):
            assert data == person_instance

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path, json=person_instance.json())
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "decorator, http_method, expected_status_code",
    [
        (post, HttpMethod.POST, HTTP_201_CREATED),
        (put, HttpMethod.PUT, HTTP_200_OK),
        (patch, HttpMethod.PATCH, HTTP_200_OK),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT),
    ],
)
def test_data_using_list_of_models(decorator, http_method, expected_status_code, create_test_client):
    test_path = "/person"

    people = PersonFactory.batch(size=5)

    class MyController(Controller):
        path = test_path

        @decorator()
        def test_method(self, data: List[Person]):
            assert data == people

    with create_test_client(MyController) as client:
        response = client.request(http_method, test_path, json=json.dumps([p.dict() for p in people]))
        assert response.status_code == expected_status_code