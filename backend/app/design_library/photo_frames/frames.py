class PhotoFrames:
    @staticmethod
    def get_frame_svg(frame_type: str, x: float, y: float, size: float, image_url: str, border_color: str = "#ffffff", border_width: float = 3.0) -> str:
        frame_type = (frame_type or "circle").lower()
        frame_id = f"frame_{abs(hash(image_url)) % 100000}"

        if frame_type == "circle":
            r = size / 2.0
            cx = x + r
            cy = y + r
            return f'''
            <defs>
              <clipPath id="{frame_id}">
                <circle cx="{cx}" cy="{cy}" r="{r - border_width}" />
              </clipPath>
            </defs>
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="{border_color}" />
            <image href="{image_url}" x="{x + border_width}" y="{y + border_width}" width="{size - border_width*2}" height="{size - border_width*2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{frame_id})" />
            '''
        elif frame_type == "rounded":
            rx = size * 0.2
            return f'''
            <defs>
              <clipPath id="{frame_id}">
                <rect x="{x + border_width}" y="{y + border_width}" width="{size - border_width*2}" height="{size - border_width*2}" rx="{rx}" />
              </clipPath>
            </defs>
            <rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx + border_width}" fill="{border_color}" />
            <image href="{image_url}" x="{x + border_width}" y="{y + border_width}" width="{size - border_width*2}" height="{size - border_width*2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{frame_id})" />
            '''
        elif frame_type == "arch":
            r = size * 0.35
            return f'''
            <defs>
              <clipPath id="{frame_id}">
                <path d="M {x+border_width},{y+r} A {r} {r} 0 0 1 {x+size-border_width},{y+r} L {x+size-border_width},{y+size-border_width} L {x+border_width},{y+size-border_width} Z" />
              </clipPath>
            </defs>
            <path d="M {x},{y+r} A {r} {r} 0 0 1 {x+size},{y+r} L {x+size},{y+size} L {x},{y+size} Z" fill="{border_color}" />
            <image href="{image_url}" x="{x+border_width}" y="{y+border_width}" width="{size-border_width*2}" height="{size-border_width*2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{frame_id})" />
            '''
        else: # Square
            return f'''
            <rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{border_color}" />
            <image href="{image_url}" x="{x + border_width}" y="{y + border_width}" width="{size - border_width*2}" height="{size - border_width*2}" preserveAspectRatio="xMidYMid slice" />
            '''
