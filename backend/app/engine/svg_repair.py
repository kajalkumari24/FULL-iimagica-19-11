import re
from typing import Dict, Any, List
import defusedxml.ElementTree as ET

# Disallowed tags that could lead to script execution or data exfiltration
BANNED_TAGS = {
    "script",
    "foreignobject",
    "object",
    "embed",
    "iframe",
    "meta",
    "link",
    "applet",
    "form",
    "input",
    "button",
}

# Dangerous protocols in attributes like href, xlink:href, src, etc.
DANGEROUS_PROTOCOLS = re.compile(r"^\s*(javascript|vbscript|data:(?!image/(png|jpeg|jpg|webp|svg\+xml))):", re.IGNORECASE)

# Event handler attributes (e.g., onload, onclick, onerror)
EVENT_HANDLER_ATTR = re.compile(r"^on[a-z]+$", re.IGNORECASE)

# Valid CSS color patterns (hex, rgb, rgba, hsl, hsla, none, currentColor, standard named colors)
VALID_COLOR_PATTERN = re.compile(
    r"^(#[0-9a-fA-F]{3,8}|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d\.]+\s*\)|hsl\([^)]+\)|hsla\([^)]+\)|url\(#[a-zA-Z0-9_\-]+\)|none|currentColor|[a-zA-Z]+)$"
)

class SVGRepair:
    """
    Sanitizes, validates, and repairs SVG templates.
    Strictly rejects malicious payloads (scripts, event handlers, foreignObjects, external scripts)
    and produces responsive viewBox-based SVGs without destructive distortion.
    """

    @classmethod
    def inspect_and_repair(
        cls,
        svg_content: str,
        target_width: float = 1080.0,
        target_height: float = 160.0,
    ) -> Dict[str, Any]:
        notices: List[str] = []
        was_repaired = False

        if not svg_content or not svg_content.strip():
            return {
                "is_valid": False,
                "was_repaired": False,
                "repaired_svg": "",
                "notices": ["SVG content is empty."],
            }

        raw = svg_content.strip()

        # Step 1: Pre-parse security checks for explicit script and foreignObject injections
        if re.search(r"<\s*(script|foreignobject|object|embed|iframe)", raw, re.IGNORECASE):
            return {
                "is_valid": False,
                "was_repaired": False,
                "repaired_svg": "",
                "notices": ["Security violation: Banned element detected (<script>, <foreignObject>, <object>, or <iframe>)."],
            }

        # Check for event handlers in pre-parse string (e.g. onload=)
        if re.search(r"\son[a-zA-Z]+\s*=", raw, re.IGNORECASE):
            return {
                "is_valid": False,
                "was_repaired": False,
                "repaired_svg": "",
                "notices": ["Security violation: Inline event handler attribute detected (e.g. onload, onclick)."],
            }

        # Step 2: Safe Defused XML parsing
        try:
            # Strip XML declaration if present
            cleaned_svg = re.sub(r"<\?xml.*?\?>", "", raw).strip()
            root = ET.fromstring(cleaned_svg)
        except Exception as e:
            return {
                "is_valid": False,
                "was_repaired": False,
                "repaired_svg": "",
                "notices": [f"Malformed SVG XML structure: {str(e)}"],
            }

        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if tag.lower() != "svg":
            return {
                "is_valid": False,
                "was_repaired": False,
                "repaired_svg": "",
                "notices": [f"Root element is <{tag}>, expected <svg>."],
            }

        # Step 3: Deep AST Element and Attribute Sanitization
        elements_to_check = list(root.iter())
        for elem in elements_to_check:
            elem_tag = elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()
            if elem_tag in BANNED_TAGS:
                return {
                    "is_valid": False,
                    "was_repaired": False,
                    "repaired_svg": "",
                    "notices": [f"Security violation: Banned element <{elem_tag}> found in SVG."],
                }

            # Inspect all attributes
            attrs_to_remove = []
            for attr_name, attr_val in list(elem.attrib.items()):
                clean_attr = attr_name.split("}")[-1].lower() if "}" in attr_name else attr_name.lower()

                # Check for event handlers
                if EVENT_HANDLER_ATTR.match(clean_attr):
                    return {
                        "is_valid": False,
                        "was_repaired": False,
                        "repaired_svg": "",
                        "notices": [f"Security violation: Event handler '{attr_name}' detected."],
                    }

                # Check for dangerous protocols in URIs
                if clean_attr in ["href", "xlink:href", "src"]:
                    if DANGEROUS_PROTOCOLS.search(attr_val.strip()):
                        return {
                            "is_valid": False,
                            "was_repaired": False,
                            "repaired_svg": "",
                            "notices": [f"Security violation: Unsafe protocol in '{attr_name}': {attr_val[:40]}"],
                        }

                # Validate fill and stroke colors
                if clean_attr in ["fill", "stroke"]:
                    val_trimmed = attr_val.strip()
                    if not VALID_COLOR_PATTERN.match(val_trimmed):
                        attrs_to_remove.append(attr_name)
                        notices.append(f"Sanitized suspicious color attribute: '{attr_name}={val_trimmed}'")
                        was_repaired = True

            for a in attrs_to_remove:
                del elem.attrib[a]

        # Step 4: Responsive viewBox and Dimensions
        viewbox = root.attrib.get("viewBox") or root.attrib.get("viewbox")
        width_attr = root.attrib.get("width", "").replace("px", "").strip()
        height_attr = root.attrib.get("height", "").replace("px", "").strip()

        if not viewbox:
            try:
                w_val = float(width_attr) if width_attr else target_width
                h_val = float(height_attr) if height_attr else target_height
                root.attrib["viewBox"] = f"0 0 {w_val} {h_val}"
                notices.append(f"Added viewBox='0 0 {w_val} {h_val}'")
                was_repaired = True
            except ValueError:
                root.attrib["viewBox"] = f"0 0 {target_width} {target_height}"
                notices.append(f"Added fallback viewBox='0 0 {target_width} {target_height}'")
                was_repaired = True

        # Use responsive scaling preserving aspect ratio:
        # DO NOT use preserveAspectRatio="none" universally!
        # For templates, 'xMidYMid meet' preserves design geometry.
        current_par = root.attrib.get("preserveAspectRatio", "")
        if not current_par or current_par == "none":
            root.attrib["preserveAspectRatio"] = "xMidYMid meet"
            notices.append("Preserved design geometry using preserveAspectRatio='xMidYMid meet'")
            was_repaired = True

        root.attrib["width"] = f"{target_width}"
        root.attrib["height"] = f"{target_height}"

        # Serialize safe sanitized XML
        import xml.etree.ElementTree as StandardET
        repaired_string = StandardET.tostring(root, encoding="unicode")

        return {
            "is_valid": True,
            "was_repaired": was_repaired,
            "repaired_svg": repaired_string,
            "notices": notices if notices else ["SVG passed validation with no repairs required."],
        }
