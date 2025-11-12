#!/usr/bin/bash
cd /home/kocoadmin/koco_product_sqlmodel
/home/kocoadmin/.local/bin/uv run poe server-gunicorn
