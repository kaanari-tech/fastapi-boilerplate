from datetime import datetime
from typing import Any, Optional

from fastapi import Response, Request
from pydantic import BaseModel, ConfigDict

from backend.common.response.response_code import CustomResponse, CustomResponseCode
from backend.core.conf import settings
from backend.utils.serializers import MsgSpecJSONResponse
from backend.utils.translator import Translator

_ExcludeData = set[int | str] | dict[int | str, Any]

__all__ = ['ResponseModel', 'response_base']


class ResponseModel(BaseModel):
    """
    Unified response model

    E.g. ::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})

        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})

        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    # TODO: json_encoders configuration not working: https://github.com/tiangolo/fastapi/discussions/10252
    model_config = ConfigDict(json_encoders={datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)})

    code: int = CustomResponseCode.HTTP_200.code
    msg: str = CustomResponseCode.HTTP_200.msg
    data: Optional[Any] = None


class ResponseBase:
    """
    Unified response method

    .. tip::

        The methods in this class will return the ResponseModel model, which serves as a coding style convention.

    E.g. ::

        @router.get('/test')
        def test() -> ResponseModel:
            return response_base.success(data={'test': 'test'})
    """

    @staticmethod
    def __response(*, request: Request, res: CustomResponseCode | CustomResponse = None, data: Any | None = None) -> ResponseModel:
        """
        General method for successful request responses

        :param res: Response information
        :param data: Response data
        :return: ResponseModel instance
        """
        translator = Translator(request.state.locale)
        return ResponseModel(code=res.code, msg=translator.t(f'app.{res.msg}'), data=data)

    def success(
        self,
        *,
        request: Request,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel:
        return self.__response(request=request, res=res, data=data)

    def fail(
        self,
        *,
        request: Request,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseModel:
        return self.__response(request=request, res=res, data=data)

    @staticmethod
    def fast_success(
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> Response:
        """
        This method was created to improve response speed. If the return data doesn't require parsing and validation by Pydantic, it is recommended to use this. Otherwise, avoid it.

        .. warning::

            When using this return method, do not specify the response_model parameter in the route, and do not add a return type annotation to the function.

        :param res: Response information
        :param data: Response data
        :return: FastAPI Response object
        """
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()
