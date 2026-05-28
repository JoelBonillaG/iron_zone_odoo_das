import os

def create_svg(filename, icon_path, color="#FF5722"):
    """Crea un SVG minimalista y profesional para el gym."""
    svg_content = f"""<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#2c3e50;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#000000;stop-opacity:1" />
            </linearGradient>
        </defs>
        <circle cx="256" cy="256" r="250" fill="url(#grad)" stroke="{color}" stroke-width="10"/>
        <g fill="white" transform="translate(128, 128) scale(1)">
            {icon_path}
        </g>
        <circle cx="256" cy="256" r="230" fill="none" stroke="white" stroke-width="2" stroke-dasharray="20,10" opacity="0.3"/>
    </svg>"""
    
    with open(filename, "w") as f:
        f.write(svg_content)

# Definición de iconos (Paths de SVG simplificados para que sean portables)
ICONS = {
    "membership_basic.svg": '<path d="M128 0L162.5 106.3H256L180.7 172.5L215.3 278.8L128 212.5L40.7 278.8L75.3 172.5L0 106.3H93.5L128 0Z" transform="translate(0, -10) scale(0.8) translate(32, 40)"/>',
    "membership_trim.svg": '<path d="M128 0L162.5 106.3H256L180.7 172.5L215.3 278.8L128 212.5L40.7 278.8L75.3 172.5L0 106.3H93.5L128 0Z" fill="#C0C0C0" transform="translate(-40, 0) scale(0.7)"/><path d="M128 0L162.5 106.3H256L180.7 172.5L215.3 278.8L128 212.5L40.7 278.8L75.3 172.5L0 106.3H93.5L128 0Z" fill="#E0E0E0" transform="translate(40, 0) scale(0.7)"/>',
    "membership_gold.svg": '<path d="M128 0L150 50L200 60L160 100L170 150L128 125L86 150L96 100L56 60L106 50L128 0Z" fill="#FFD700" transform="scale(1.2) translate(-20, -10)"/>',
    "spinning.svg": '<circle cx="64" cy="192" r="48" fill="none" stroke="white" stroke-width="16"/><circle cx="192" cy="192" r="48" fill="none" stroke="white" stroke-width="16"/><path d="M64 192L128 64L192 192M100 100H156" fill="none" stroke="white" stroke-width="16"/>',
    "crossfit.svg": '<rect x="32" y="96" width="192" height="64" rx="10" fill="white"/><rect x="0" y="112" width="32" height="32" rx="5" fill="#FF5722"/><rect x="224" y="112" width="32" height="32" rx="5" fill="#FF5722"/>',
    "personal_trainer.svg": '<circle cx="128" cy="64" r="48"/><path d="M32 224C32 160 64 128 128 128C192 128 224 160 224 224H32Z"/>',
    "gloves.svg": '<path d="M64 64C64 32 96 0 144 0C192 0 224 32 224 96V192C224 224 192 256 144 256H112C80 256 64 240 64 208V64Z"/><rect x="48" y="160" width="192" height="32" fill="#FF5722" rx="5"/>',
    "protein.svg": '<path d="M64 64H192V256H64V64ZM80 32H176V64H80V32Z"/><path d="M96 128H160" stroke="#FF5722" stroke-width="16"/>',
    "rope.svg": '<path d="M32 64C32 64 64 256 128 256C192 256 224 64 224 64" fill="none" stroke="white" stroke-width="16"/><rect x="16" y="32" width="32" height="64" rx="5"/><rect x="208" y="32" width="32" height="64" rx="5"/>',
    "water.svg": '<path d="M128 32L96 96V256H160V96L128 32Z"/><rect x="96" y="128" width="64" height="16" fill="#03A9F4"/>',
    "combo_plan.svg": '<path d="M128 224L110 206C44 146 0 106 0 58C0 18 30 0 66 0C86 0 106 10 128 25C150 10 170 0 190 0C226 0 256 18 256 58C256 106 212 146 146 206L128 224Z" fill="#FF5722"/>'
}

output_dir = "seeds/images/products"
os.makedirs(output_dir, exist_ok=True)

print(f"Generando {len(ICONS)} iconos profesionales en {output_dir}...")

for filename, path in ICONS.items():
    create_svg(os.path.join(output_dir, filename), path)
    print(f"  [OK] {filename}")

print("\nListo. Los iconos tienen un estilo moderno (Dark Mode + Accent Color).")
