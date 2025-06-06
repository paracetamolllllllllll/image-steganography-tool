from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import base64

# AES encryption
def encrypt_message(message, password):
    key = password.encode('utf-8').ljust(32, b'0')[:32]
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct).decode('utf-8')

def decrypt_message(encrypted_message, password):
    try:
        encrypted = base64.b64decode(encrypted_message)
        iv = encrypted[:16]
        ct = encrypted[16:]
        key = password.encode('utf-8').ljust(32, b'0')[:32]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except Exception:
        raise ValueError("Decryption failed. Possibly incorrect password or invalid data.")

# LSB encoding
def encode_message(image_path, message):
    img = Image.open(image_path)
    encoded = img.copy()
    message += '|||END|||'
    binary = ''.join([format(ord(char), '08b') for char in message])
    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(encoded.getpixel((x, y)))
            for i in range(3):
                if data_index < len(binary):
                    pixel[i] = pixel[i] & ~1 | int(binary[data_index])
                    data_index += 1
            encoded.putpixel((x, y), tuple(pixel))
            if data_index >= len(binary):
                return encoded
    raise ValueError("Image is too small to hold the message.")

# LSB decoding
def decode_message(image_path):
    img = Image.open(image_path)
    binary = ''
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            for i in range(3):
                binary += str(pixel[i] & 1)
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    chars = [chr(int(b, 2)) for b in bytes_list]
    decoded = ''.join(chars)
    return decoded.split('|||END|||')[0]
