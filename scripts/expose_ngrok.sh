#!/bin/bash
# Expose local Odoo (port 8069) via ngrok for team sharing
# Requires: ngrok installed and authenticated (ngrok config add-authtoken <token>)
echo "Exposing Odoo at http://localhost:8069 via ngrok..."
echo "Share the public URL with your team."
ngrok http 8069
