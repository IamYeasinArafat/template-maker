import base64
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query, Response
from jinja2 import Template
from playwright.async_api import async_playwright
from pydantic import BaseModel
import httpx

from core.config import Settings

router: APIRouter = APIRouter(prefix="/v2", tags=["v2"])

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

def get_base64_image_from_url(url: str) -> str:
    """Fetches an image from a URL and converts it to a Base64 string."""
    if not url:
        return ""
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"Error fetching profile image from URL: {e}")
        return ""

@router.post("/generate-profile")
async def generate_profile(params: Annotated[QueryParams, Query()]):
    settings = Settings()
    template_dir = settings.TEMPLATE_PATH / params.version
    assets_dir = settings.ASSETS_PATH / "persist"
    
    # 1. Prepare Assets (Persistent files)
    bg_b64 = get_base64_image(assets_dir / "cmu-tartan-wave-red-crop-01.png")
    seal_b64 = get_base64_image(assets_dir / "cmu-seal-w.png")
    profile_image_data = get_base64_image_from_url(params.profile_image_url) or get_base64_image(assets_dir / "profile-placeholder.png")

    print("Background image loaded, size (chars): ", len(bg_b64))
    print("Seal image loaded, size (chars): ", len(seal_b64))
    print("Profile image loaded, size (chars): ", len(profile_image_data))

    with open(settings.PROJECT_ROOT / "debug.txt", "w") as debug_file:
        print(profile_image_data, file=debug_file)
    

    # 2. Render Template
    with open(template_dir / "template.html", "r") as f:
        template = Template(f.read())

    html_content = template.render(
        **params.model_dump(), # Spreads name, major, location, handle automatically
        bg_image_data=bg_b64,
        seal_image_data=seal_b64,
        profile_image_data=profile_image_data
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