import base64
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Query, Response, UploadFile
from jinja2 import Template
from playwright.async_api import async_playwright
from pydantic import BaseModel
import httpx

from core.config import Settings

router: APIRouter = APIRouter(prefix="/v3", tags=["v3"])

class QueryParams(BaseModel):
    name: str
    major: str
    location: str
    handle: str
    profile_image_url: str = "" 
    version: str = "v1"

def get_base64_image(image_path: Path) -> str:
    """Helper to convert local assets to Base64 strings for the browser."""
    if not image_path.exists():
        print(f"Warning: Asset not found at {image_path}")
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def adjust_handle(handle: str) -> str:
    """Ensures the handle starts with '@' for consistent display."""
    return handle if handle.startswith("@") else f"@{handle}"


def adjust_params(params: QueryParams) -> QueryParams:
    """Applies necessary adjustments to the input parameters."""
    params.handle = adjust_handle(params.handle)
    return params

@router.post("/generate-profile")
async def generate_profile(
    # Use Depends to pull in the text fields as query params
    params: Annotated[QueryParams, Query()],
    # Use UploadFile to accept the image
    profile_file: UploadFile = File(...)
):
    settings = Settings()
    params = adjust_params(params)
    template_dir = settings.TEMPLATE_PATH / params.version
    assets_dir = settings.ASSETS_PATH / "persist"
    
    # 1. Prepare Base Assets
    bg_b64 = get_base64_image(assets_dir / "cmu-tartan-wave-red-crop-01.png")
    seal_b64 = get_base64_image(assets_dir / "cmu-seal-w.png")

    # 2. Process the Uploaded File
    try:
        file_content = await profile_file.read()
        profile_image_b64 = base64.b64encode(file_content).decode("utf-8")
    except Exception as e:
        print(f"File upload failed, using placeholder: {e}")
        profile_image_b64 = get_base64_image(assets_dir / "profile-placeholder.png")
    

    # 2. Render Template
    with open(template_dir / "template.html", "r") as f:
        template = Template(f.read())

    html_content = template.render(
        **params.model_dump(), # Spreads name, major, location, handle automatically
        bg_image_data=bg_b64,
        seal_image_data=seal_b64,
        profile_image_data=profile_image_b64
    )

    # 3. Playwright Rendering
    async with async_playwright() as p:
        # Launching with --no-sandbox is often required for Docker environments
        browser = await p.chromium.launch(args=["--no-sandbox"])
        try:
            page = await browser.new_page()
            
            # Set the HTML and inject CSS
            await page.set_content(html_content)
            await page.add_style_tag(path=str(template_dir / "style.css"))
            
            # Wait for any external resources (like Google Fonts) to finish loading
            await page.wait_for_load_state("networkidle")
            
            element = await page.query_selector(".insta-card")
            if not element:
                return Response(content="Layout element '.insta-card' not found", status_code=500)
            
            # Capture the screenshot
            image_bytes = await element.screenshot(
                type="jpeg", 
                quality=95,
                animations="disabled" # Ensures no motion blur if CSS has transitions
            )
            
            return Response(content=image_bytes, media_type="image/jpeg")
            
        finally:
            # Always close the browser to prevent memory leaks
            await browser.close()