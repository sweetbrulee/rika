import asyncio
from io import BytesIO
import discord
import httpx
from PIL import Image
from bs4 import BeautifulSoup


def create_httpx_client():
    return httpx.AsyncClient(
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        },
    )


async def send_hentai_message(ctx: discord.ApplicationContext, url: str) -> None:
    msg = await ctx.respond(
        content=url,
        # view=HentaiMessageView(ctx, url, image_urls, more_full_urls), disabled because we've already sent the preview image
    )

    async with create_httpx_client() as client:
        response = await client.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}, send url only message as fallback.")
        await ctx.respond(content=url)
        return
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Resolve html content and dom elements, so that we can get the image urls and useful contents that we want
    thumbnail_container = soup.find("div", id="thumbnail-container")
    thumb_links = thumbnail_container.find_all("a", class_="gallerythumb")
    image_urls = []
    for thumb in thumb_links:
        img_tag = thumb.find("img")  # 找到每个 <a> 标签中的 <img> 标签
        img_url = img_tag.get("data-src")  # 提取 data-src 属性中的 URL
        if img_url:
            image_urls.append(img_url)  # 将 URL 添加到列表

    # 提取 more urls（相關本本推薦）
    related_container = soup.find("div", id="related-container")
    gallery_links = related_container.find_all("a", class_="cover")
    more_full_urls = []
    for link in gallery_links:
        href = link.get("href")  # 提取 href 属性
        if href:
            full_url = "https://nhentai.net" + href  # 拼接完整链接
            more_full_urls.append(full_url)  # 添加到列表

    # Create a preview image and edit the original message with the preview image if it is successful
    await msg.edit(
        content=url,
        file=discord.File(
            fp=await create_preview_image(image_urls, 5), filename="preview.jpg"
        ),
    )


async def download_image(url):
    async with create_httpx_client() as client:
        response = await client.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))


async def download_images(image_urls):
    tasks = [download_image(url) for url in image_urls]
    return await asyncio.gather(*tasks)


def select_images(images, k):
    n = len(images)
    if n <= k:
        return images
    step = n // k
    return [images[i * step] for i in range(k)]


def merge_images_horizontally(images):
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)

    merged_image = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for img in images:
        merged_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return merged_image


async def create_preview_image(image_urls: list[str], k: int):
    # Step 1: Download images
    images = await download_images(image_urls)

    # Step 2: Select images based on k
    selected_images = select_images(images, k)

    # Step 3: Merge selected images horizontally
    preview_image = merge_images_horizontally(selected_images)

    # Step 4: Save the merged image to an in-memory BytesIO object and return it
    memory_fp = BytesIO()
    preview_image.save(memory_fp, format="JPEG")
    memory_fp.seek(0)  # Reset file pointer to the beginning for reading
    return memory_fp
