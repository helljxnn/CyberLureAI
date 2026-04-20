from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _format_validation_detail(error: dict) -> dict[str, str]:
    location = [str(part) for part in error.get("loc", []) if part != "body"]
    field = ".".join(location) if location else "request"
    return {
        "field": field,
        "message": error.get("msg", "Invalid value."),
    }


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [_format_validation_detail(error) for error in exc.errors()]

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request contains invalid or missing data.",
            "details": details,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
