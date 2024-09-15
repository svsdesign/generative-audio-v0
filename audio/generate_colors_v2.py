import colorsys
import json

def generate_circular_colors(hue_segments, brightness_levels):
    colors = {}
    
    for j in range(brightness_levels):
        for i in range(hue_segments):
            hue = i / hue_segments
            brightness = 100 - (j / (brightness_levels - 1)) * 100
            
            if brightness == 0:
                # Handle the special case where brightness is zero
                gray_value = int((255 / hue_segments) * i)
                hex_color = '#{:02x}{:02x}{:02x}'.format(gray_value, gray_value, gray_value)
                
                if i == 0:
                    hex_color = '#000000'  # Ensure the first segment is pure black
                
            else:
                # Normal color generation with full saturation and varying brightness
                rgb = colorsys.hsv_to_rgb(hue, 1, brightness / 100)
                hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            colors[j * hue_segments + i] = hex_color
    
    return colors

# Parameters
hue_segments = 16
brightness_levels = 8

# Generate colors
colors = generate_circular_colors(hue_segments, brightness_levels)

# Create the color mapping JSON
color_mapping = colors

# Save to a JSON file
with open('static/color_mapping.json', 'w') as f:
    json.dump(color_mapping, f, indent=4)

print("Color mapping saved to color_mapping.json")
