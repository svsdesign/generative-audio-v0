import colorsys
import json

def generate_circular_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors  # Divide the circle into equal parts (0 to 1)
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)  # Full saturation and brightness
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        colors.append(hex_color)
    return colors

# Generate 128 colors
colors = generate_circular_colors(128)

# Create the color mapping JSON
color_mapping = {i: color for i, color in enumerate(colors)}

# Save to a JSON file
with open('static/color_mapping.json', 'w') as f:
    json.dump(color_mapping, f, indent=4)

print("Color mapping saved to color_mapping.json")