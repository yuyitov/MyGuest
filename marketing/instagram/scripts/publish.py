#!/usr/bin/env python3
"""
Publish scheduled Instagram posts via Meta Graph API.

Requirements:
  pip install requests

Environment variables (set in GitHub Secrets or locally):
  INSTAGRAM_TOKEN   - Page Access Token with instagram_content_publish permission
  IG_USER_ID        - Instagram Business Account ID
  BASE_URL          - Public base URL where PNGs are served (no trailing slash)
                      e.g. https://myguestguide.com/instagram

Usage:
  python publish.py              # publishes posts due today or earlier
  python publish.py --dry-run    # shows what would be published without calling API
"""

import json
import os
import sys
import time
import requests
from datetime import date
from pathlib import Path

POSTS_JSON = Path(__file__).parents[1] / "posts.json"
EXPORTS_DIR = Path(__file__).parents[1] / "exports"

GRAPH_API = "https://graph.facebook.com/v25.0"

POST_ID_TO_EXPORT = {}
for f in EXPORTS_DIR.glob("*.png"):
    # filename format: 01-post-001.png → post-001
    parts = f.stem.split("-", 1)
    if len(parts) == 2:
        post_id = parts[1]
        POST_ID_TO_EXPORT[post_id] = f.name


def get_config():
    token = os.environ.get("INSTAGRAM_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    base_url = os.environ.get("BASE_URL", "https://myguestguide.com/instagram")
    if not token or not ig_user_id:
        print("ERROR: INSTAGRAM_TOKEN and IG_USER_ID must be set.")
        sys.exit(1)
    return token, ig_user_id, base_url.rstrip("/")


def create_media_container(ig_user_id, token, image_url, caption):
    resp = requests.post(
        f"{GRAPH_API}/{ig_user_id}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def publish_container(ig_user_id, token, creation_id):
    resp = requests.post(
        f"{GRAPH_API}/{ig_user_id}/media_publish",
        params={
            "creation_id": creation_id,
            "access_token": token,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def build_caption(post):
    parts = [post.get("caption", "")]
    hashtags = post.get("hashtags", "")
    if hashtags:
        parts.append(hashtags)
    return "\n\n".join(p for p in parts if p)


def main():
    dry_run = "--dry-run" in sys.argv
    token, ig_user_id, base_url = get_config()

    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    today = date.today().isoformat()

    to_publish = [
        p for p in posts
        if p.get("status") == "ready"
        and p.get("publish_date", "") <= today
    ]

    if not to_publish:
        print(f"No posts scheduled for today ({today}).")
        return

    published_ids = set()

    for post in to_publish:
        post_id = post["id"]
        filename = POST_ID_TO_EXPORT.get(post_id)

        if not filename:
            print(f"SKIP {post_id}: no PNG found in exports/")
            continue

        image_url = f"{base_url}/{filename}"
        caption = build_caption(post)

        print(f"\n→ {post_id} | {post.get('publish_date')} | {image_url}")

        if dry_run:
            print("  [dry-run] would publish this post")
            continue

        try:
            container_id = create_media_container(ig_user_id, token, image_url, caption)
            print(f"  container created: {container_id}")
            time.sleep(10)
            published_post_id = publish_container(ig_user_id, token, container_id)
            print(f"  published! post id: {published_post_id}")
            published_ids.add(post_id)
        except requests.HTTPError as e:
            print(f"  ERROR: {e.response.status_code} {e.response.text}")

    if published_ids:
        for post in posts:
            if post["id"] in published_ids:
                post["status"] = "published"
        POSTS_JSON.write_text(
            json.dumps(posts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n✓ Updated posts.json — {len(published_ids)} post(s) marked as published.")


if __name__ == "__main__":
    main()
