import pytest
import taler_python.errors

taler_error_detail = {"code": 5125, "hint": "The requested resource was not found.", "detail": "account unknown"}

class TestErrors:
    def test_status_code(self):
        # detail_error = taler_python.errors.ErrorDetail(taler_error_detail)
        detail_error = taler_python.errors.ErrorDetail.model_validate(taler_error_detail)
        not_found_error = taler_python.errors.NotFoundError(detail_error)
        assert not_found_error.http_status == 404
        
        conflict_error = taler_python.errors.ConflictError(detail_error)
        assert conflict_error.http_status == 409
        
        gone_error = taler_python.errors.GoneError(detail_error)
        assert gone_error.http_status == 410
        
        unauthorized_error = taler_python.errors.UnauthorizedError(detail_error)
        assert unauthorized_error.http_status == 401

        forbidden_error = taler_python.errors.ForbiddenError(detail_error)
        assert forbidden_error.http_status == 403
    
    def test_response_parse(self):
        result = taler_python.errors.ErrorDetail.model_validate(taler_error_detail)
        
        assert result.code == 5125
        assert result.hint == "The requested resource was not found."
        assert result.detail == "account unknown"
        assert result.parameter is None
        assert result.path is None

    def test_verify_str(self):
        detail_error = taler_python.errors.ErrorDetail.model_validate(taler_error_detail)
        e = taler_python.errors.NotFoundError(detail_error)
        assert str(e) == "NotFoundError(404): [5125] The requested resource was not found."