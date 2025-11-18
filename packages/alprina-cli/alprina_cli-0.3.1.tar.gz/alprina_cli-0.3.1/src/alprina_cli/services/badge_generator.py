"""
Badge Generator Service
Generates SVG badges for Alprina security verification.
"""

from datetime import datetime
from typing import Optional, Literal
import xml.etree.ElementTree as ET


class BadgeGenerator:
    """Generates SVG security badges in various styles."""

    # Color schemes
    THEMES = {
        "light": {
            "background": "#ffffff",
            "text": "#1a1a1a",
            "accent": "#3b82f6",
            "border": "#e5e7eb",
            "grade_bg": "#f3f4f6"
        },
        "dark": {
            "background": "#1a1a1a",
            "text": "#ffffff",
            "accent": "#60a5fa",
            "border": "#374151",
            "grade_bg": "#374151"
        }
    }

    # Size configurations
    SIZES = {
        "small": {"width": 160, "height": 50, "font_size": 11},
        "medium": {"width": 200, "height": 60, "font_size": 13},
        "large": {"width": 240, "height": 70, "font_size": 15}
    }

    def generate_svg(
        self,
        style: Literal["standard", "minimal", "detailed"] = "standard",
        theme: Literal["light", "dark"] = "light",
        size: Literal["small", "medium", "large"] = "medium",
        grade: Optional[str] = None,
        last_scan: Optional[datetime] = None,
        custom_text: Optional[str] = None
    ) -> str:
        """Generate SVG badge based on parameters."""

        if style == "minimal":
            return self._generate_minimal_badge(theme, size, grade)
        elif style == "detailed":
            return self._generate_detailed_badge(theme, size, grade, last_scan)
        else:
            return self._generate_standard_badge(theme, size, grade, custom_text)

    def _generate_standard_badge(
        self,
        theme: str,
        size: str,
        grade: Optional[str],
        custom_text: Optional[str]
    ) -> str:
        """Generate standard badge style."""
        colors = self.THEMES[theme]
        dimensions = self.SIZES[size]

        text = custom_text or "Secured by Alprina"
        grade_display = grade if grade and grade != "N/A" else ""

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{dimensions['width']}" height="{dimensions['height']}" viewBox="0 0 {dimensions['width']} {dimensions['height']}">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
        </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="{dimensions['width']}" height="{dimensions['height']}" rx="8" fill="{colors['background']}" stroke="{colors['border']}" stroke-width="1.5"/>

    <!-- Left section with gradient -->
    <rect width="50" height="{dimensions['height']}" rx="8" fill="url(#grad)"/>

    <!-- Shield icon -->
    <g transform="translate(15, {dimensions['height']/2 - 10})">
        <path d="M10 0 L0 4 L0 8 Q0 14 10 18 Q20 14 20 8 L20 4 Z" fill="white" opacity="0.9"/>
        <path d="M10 4 L10 14 M6 9 L10 13 L14 9" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    </g>

    <!-- Main text -->
    <text x="60" y="{dimensions['height']/2 - 5}" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size']}" font-weight="600">
        {text}
    </text>

    <!-- Grade badge (if provided) -->
    {f'<g transform="translate({dimensions["width"] - 40}, {dimensions["height"]/2 - 12})">' if grade_display else ''}
    {f'<rect width="32" height="24" rx="4" fill="{colors["grade_bg"]}" stroke="{colors["border"]}" stroke-width="1"/>' if grade_display else ''}
    {f'<text x="16" y="16" fill="{colors["accent"]}" font-family="Arial, sans-serif" font-size="{dimensions["font_size"] - 1}" font-weight="bold" text-anchor="middle">{grade_display}</text>' if grade_display else ''}
    {f'</g>' if grade_display else ''}

    <!-- Checkmark -->
    <g transform="translate(60, {dimensions['height']/2 + 10})">
        <circle cx="6" cy="6" r="6" fill="#10b981" opacity="0.2"/>
        <path d="M4 6 L6 8 L9 4" stroke="#10b981" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    <text x="74" y="{dimensions['height']/2 + 16}" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size'] - 3}" opacity="0.7">Verified</text>
</svg>'''
        return svg

    def _generate_minimal_badge(
        self,
        theme: str,
        size: str,
        grade: Optional[str]
    ) -> str:
        """Generate minimal badge style."""
        colors = self.THEMES[theme]
        dimensions = self.SIZES[size]

        grade_display = grade if grade and grade != "N/A" else ""

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{dimensions['width']}" height="{dimensions['height'] - 10}" viewBox="0 0 {dimensions['width']} {dimensions['height'] - 10}">
    <!-- Background -->
    <rect width="{dimensions['width']}" height="{dimensions['height'] - 10}" rx="6" fill="{colors['background']}" stroke="{colors['border']}" stroke-width="1"/>

    <!-- Shield icon -->
    <g transform="translate(10, {(dimensions['height'] - 10)/2 - 8})">
        <path d="M8 0 L0 3 L0 6 Q0 10 8 13 Q16 10 16 6 L16 3 Z" fill="{colors['accent']}" opacity="0.9"/>
        <path d="M8 3 L8 10 M5 7 L8 10 L11 7" stroke="white" stroke-width="1.2" fill="none" stroke-linecap="round"/>
    </g>

    <!-- Text -->
    <text x="35" y="{(dimensions['height'] - 10)/2 + 5}" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size'] - 1}" font-weight="600">
        Alprina
    </text>

    <!-- Grade (if provided) -->
    {f'<text x="{dimensions["width"] - 35}" y="{(dimensions["height"] - 10)/2 + 5}" fill="{colors["accent"]}" font-family="Arial, sans-serif" font-size="{dimensions["font_size"]}" font-weight="bold">{grade_display}</text>' if grade_display else ''}
</svg>'''
        return svg

    def _generate_detailed_badge(
        self,
        theme: str,
        size: str,
        grade: Optional[str],
        last_scan: Optional[datetime]
    ) -> str:
        """Generate detailed badge style with scan date."""
        colors = self.THEMES[theme]
        dimensions = self.SIZES[size]

        grade_display = grade if grade and grade != "N/A" else "N/A"
        date_text = ""
        if last_scan:
            date_text = f"Scanned: {last_scan.strftime('%b %d, %Y')}"
        else:
            date_text = "No recent scan"

        # Increase height for detailed view
        height = dimensions['height'] + 20

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{dimensions['width']}" height="{height}" viewBox="0 0 {dimensions['width']} {height}">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.1" />
            <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:0.1" />
        </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="{dimensions['width']}" height="{height}" rx="10" fill="{colors['background']}" stroke="{colors['border']}" stroke-width="1.5"/>
    <rect width="{dimensions['width']}" height="{height}" rx="10" fill="url(#grad)"/>

    <!-- Header section -->
    <rect width="{dimensions['width']}" height="30" rx="10" fill="{colors['accent']}" opacity="0.1"/>

    <!-- Shield icon -->
    <g transform="translate({dimensions['width']/2 - 12}, 8)">
        <path d="M12 0 L0 4 L0 8 Q0 14 12 20 Q24 14 24 8 L24 4 Z" fill="{colors['accent']}"/>
        <path d="M12 5 L12 16 M8 11 L12 15 L16 11" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
    </g>

    <!-- Title -->
    <text x="{dimensions['width']/2}" y="45" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size']}" font-weight="bold" text-anchor="middle">
        Secured by Alprina
    </text>

    <!-- Grade section -->
    <g transform="translate({dimensions['width']/2 - 30}, 55)">
        <rect width="60" height="30" rx="6" fill="{colors['grade_bg']}" stroke="{colors['border']}" stroke-width="1"/>
        <text x="30" y="20" fill="{colors['accent']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size'] + 4}" font-weight="bold" text-anchor="middle">{grade_display}</text>
    </g>

    <!-- Status indicators -->
    <g transform="translate(15, {height - 20})">
        <circle cx="4" cy="4" r="4" fill="#10b981"/>
        <text x="12" y="7" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size'] - 4}" opacity="0.7">Verified</text>
    </g>

    <!-- Last scan date -->
    <text x="{dimensions['width']/2}" y="{height - 10}" fill="{colors['text']}" font-family="Arial, sans-serif" font-size="{dimensions['font_size'] - 5}" opacity="0.6" text-anchor="middle">
        {date_text}
    </text>
</svg>'''
        return svg

    def generate_static_url(
        self,
        user_id: str,
        base_url: str = "https://alprina.com"
    ) -> str:
        """Generate static badge URL."""
        return f"{base_url}/api/v1/badge/{user_id}/svg"

    def generate_verification_url(
        self,
        user_id: str,
        base_url: str = "https://alprina.com"
    ) -> str:
        """Generate verification page URL."""
        return f"{base_url}/verify/{user_id}"
