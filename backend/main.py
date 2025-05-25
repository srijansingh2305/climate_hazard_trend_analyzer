from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conlist, Field
from climate_logic import analyze_heatwaves
from db import cache_result, get_cached_result
import traceback

from fastapi.responses import FileResponse
from report_utils import generate_csv, generate_pdf

from climate_logic import analyze_heatwaves, analyze_rainfall, analyze_drought, analyze_flood, get_heatwave_threshold


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YearRange(BaseModel):
    start: int
    end: int

class ClimateRequest(BaseModel):
    bounds: conlist(float, min_length=4, max_length=4)
    range: dict
    threshold: float = Field(default=33.8)
    hazard: str = Field(default="heatwave", description="Type of hazard: heatwave, rainfall, drought, flood")


class HeatwaveRequest(BaseModel):
    bounds: conlist(float, min_length=4, max_length=4)
    range: dict
    threshold: float = Field(default=33.8)

class ThresholdRequest(BaseModel):
    bounds: conlist(float, min_length=4, max_length=4)
    start_year: int
    end_year: int
    percentile: int = 95

@app.post("/api/hazards")
async def get_hazard_data(req: ClimateRequest):
    try:
      
        cached = await get_cached_result(req.bounds, req.range, req.threshold, req.hazard)
        if cached:
            return {"trends": cached["trends"], "summary": cached["summary"]}

       
        if req.hazard == "heatwave":
            trends, summary = await analyze_heatwaves(req.bounds, req.range, req.threshold)
        elif req.hazard == "rainfall":
            trends, summary = await analyze_rainfall(req.bounds, req.range, req.threshold)
        elif req.hazard == "drought":
            trends, summary = await analyze_drought(req.bounds, req.range, req.threshold)
        elif req.hazard == "flood":
            trends, summary = await analyze_flood(req.bounds, req.range, req.threshold)
        else:
            raise HTTPException(status_code=400, detail="Invalid hazard type.")

        await cache_result(req.bounds, req.range, req.threshold, trends, summary, req.hazard)
        return {"trends": trends, "summary": summary}

    except Exception as e:
        print("Error in /api/hazards:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/api/thresholds/heatwave")
async def heatwave_threshold(
    req: ThresholdRequest,
    start_year: int = Query(..., ge=1900, le=2100),
    end_year: int = Query(..., ge=1900, le=2100),
    percentile: int = Query(95, ge=0, le=100),
):
    
    try:
        year_range = {"start": start_year, "end": end_year}
        result = await get_heatwave_threshold(req.bounds, year_range, percentile)
        return result
    except Exception as e:
        print("Error in /api/thresholds/heatwave:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/api/hazards/export")
async def export_hazard_data(req: ClimateRequest):
    if req.hazard == "heatwave":
        trends, summary = await analyze_heatwaves(req.bounds, req.range, req.threshold)
    elif req.hazard == "rainfall":
        trends, summary = await analyze_rainfall(req.bounds, req.range, req.threshold)
    elif req.hazard == "drought":
        trends, summary = await analyze_drought(req.bounds, req.range, req.threshold)
    elif req.hazard == "flood":
        trends, summary = await analyze_flood(req.bounds, req.range, req.threshold)
    else:
        raise HTTPException(status_code=400, detail="Invalid hazard type.")

    csv_path = f"trend_{req.hazard}.csv"
    pdf_path = f"trend_{req.hazard}.pdf"

    generate_csv(trends, csv_path)
    generate_pdf(trends, req.hazard, summary, pdf_path)

    return {
        "csv_url": f"/download/{csv_path}",
        "pdf_url": f"/download/{pdf_path}"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(path=filename, filename=filename, media_type='application/octet-stream')

@app.get("/")
async def root():
    return {"message": "Hello World"}