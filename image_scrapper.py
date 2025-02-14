import json
import os
from dotenv import load_dotenv
from PIL import Image
import requests

load_dotenv()

JSON_PATH = os.getenv("JSON_PATH")


def get_number_of_json_files():
    return len([name for name in os.listdir('.') if name.endswith('.json') and name.startswith('test_batch')])


def load_from_json_batch(batch_number):
    filename = JSON_PATH.format(batch_num=batch_number*100)

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Batch {batch_number} file not found")
        return {}


def convert_to_webp(image_path):
    im = Image.open(image_path)
    im.save(image_path.replace(".png", ".webp"), "WEBP")


def main():
    os.makedirs('images', exist_ok=True)
    data_base_lenght = get_number_of_json_files()
    print(f"Found {data_base_lenght} batches")

    data = load_from_json_batch(1)
    print(f"Loading {len(data)} coins...")

    for coin_name, image_url in data.items():
        print(f"Downloading {coin_name}...")

        try:
            response = requests.get(image_url)
            response.raise_for_status()

            safe_filename = "".join(
                c if c.isalnum() or c == '_' else '_'
                for c in coin_name
            ).rstrip('_')
            png_filepath = os.path.join('images', f"{safe_filename}.png")

            with open(png_filepath, "wb") as f:
                f.write(response.content)

            convert_to_webp(png_filepath)
            print(f"Successfully saved {coin_name}")
            os.remove(png_filepath)
            print(f"Deleted {coin_name}.png")

        except requests.RequestException as e:
            print(f"Failed to download {coin_name}: {str(e)}")
        except IOError as e:
            print(f"Failed to save {coin_name}: {str(e)}")


if __name__ == "__main__":
    main()
