import sys
from PIL import Image


def convert_image_to_mono_bytes(image):
    # Convert the image to black and white (1-bit pixels) using dithering
    bw_image = image.convert('1')

    # Convert the image to a byte array
    byte_array = bytearray(bw_image.tobytes())

    # Since we're using MONO_HLSB, we need to invert the bits
    # because in the PIL library, 0 is black and 1 is white, which is the opposite in framebuf
    inverted_byte_array = bytearray(len(byte_array))
    for i, byte in enumerate(byte_array):
        # Invert bits
        inverted_byte_array[i] = ~byte & 0xFF

    return inverted_byte_array


def generate_micropython_code(byte_array, width, height):
    # Generate the MicroPython code to create a FrameBuffer object
    # Format the bytearray as a string of escaped hex values
    byte_string = ''.join('\\x{:02x}'.format(b) for b in byte_array)
    fb_code = (f"fb = framebuf.FrameBuffer(bytearray(b'{byte_string}'), "
               f"{width}, {height}, framebuf.MONO_HLSB)")
    return fb_code


def process_image(image_path):
    # Open the image
    with Image.open(image_path) as img:
        # Check if the image has an alpha channel
        if img.mode in ('RGBA', 'LA') or ('transparency' in img.info):
            # Convert the image to RGBA if it's not already in that mode
            rgba_image = img.convert('RGBA')

            # Create a new image with a white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(rgba_image, mask=rgba_image.split()[3])  # 3 is the alpha channel
            img = background.convert('1')

        # Convert to monochrome (1-bit) byte array suitable for FrameBuffer
        byte_array = convert_image_to_mono_bytes(img)

    # Generate MicroPython code
    return generate_micropython_code(byte_array, img.width, img.height)


def main():
    if len(sys.argv) != 2:
        print("Usage: python png_to_framebuffer.py <path_to_png_file>")
        sys.exit(1)

    png_file = sys.argv[1]
    try:
        code = process_image(png_file)
        print(code)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
