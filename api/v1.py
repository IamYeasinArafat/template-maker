from typing import Annotated
from fastapi import Query, Response, APIRouter
from jinja2 import Template
from playwright.async_api import async_playwright
from core.config import Settings
from pydantic import BaseModel

router : APIRouter = APIRouter(prefix="/v1", tags=["v1"])

class QueryParams(BaseModel):
    name: str
    major: str
    location: str
    handle: str
    version: str = "v1"

@router.post("/generate-profile")
async def generate_profile(params: Annotated[QueryParams, Query()]):
    # 1. Load and Render Template
    template_path = Settings().TEMPLATE_PATH / params.version
    with open(template_path / "template.html", "r") as f:
        print(f"Loaded template from {template_path / 'template.html'}")
        template = Template(f.read())
    
    print(f"Rendering template with: {params.dict()}")

    html_content = template.render(
        name=params.name, 
        major=params.major, 
        location=params.location, 
        handle=params.handle
    )

    # 2. Capture with Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set content and wait for fonts/images to load
        await page.set_content(html_content)
        await page.add_style_tag(path=str(template_path / "style.css"))

        print("USing css file at: ", template_path / "style.css")
        
        # Select the specific card and screenshot it
        element = await page.query_selector(".insta-card")
        image_bytes = await element.screenshot(type="jpeg", quality=90) # type: ignore
        
        await browser.close()
        
    return Response(content=image_bytes, media_type="image/jpeg")