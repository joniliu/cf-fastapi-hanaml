from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from services.hana_service import (
    get_hana_connection,
    test_hana_connection,
    fetch_countries,
    create_country,
    update_country,
    delete_country,
)


# Define request/response models
class CountryCreate(BaseModel):
    NAME: str
    DESCR: str
    CODE: str


class CountryUpdate(BaseModel):
    NAME: Optional[str] = None
    DESCR: Optional[str] = None


api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


@api_router.get("/test_connection")
async def test_connection():
    try:
        result = test_hana_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/hana_version")
async def hana_version():
    try:
        conn = get_hana_connection()
        version = conn.hana_version()
        return {"hana_version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/countries")
async def get_countries(page: int = Query(1, gt=0), per_page: int = Query(100, gt=0)):
    try:
        result = fetch_countries(page=page, per_page=per_page)
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/add/country", status_code=201)
async def add_country(country: CountryCreate):
    try:
        result = create_country(country.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/update/country/{code}")
async def update_country_route(code: str, country: CountryUpdate):
    try:
        result = update_country(code, country.model_dump(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/delete/country/{code}")
async def delete_country_route(code: str):
    try:
        result = delete_country(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
