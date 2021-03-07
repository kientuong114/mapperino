import argparse
import itertools
import os
import tempfile
from PIL import Image

IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID', None)
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'mapperino')
transfer = None

parser = argparse.ArgumentParser(description='Split an image, upload it to imgur and automatically write the commands in game to create maps')
parser.add_argument('service', choices=['imgur', 's3', 'cloudinary'], help='Service to use to upload images')
parser.add_argument('image', help='The image to split')
parser.add_argument('-c', '--count', help='Number of splits', type=int)
parser.add_argument('-t', '--tilesize', help='Size of the tiles in px', type=int)
parser.add_argument('-o', '--output', help='Output the commands on the file instead of stdout')
parser.add_argument('--no-upload', help='Prevents upload of images, for testing', action='store_true')

def split_image(img_name: str, h_splits: int):
    img = Image.open(img_name)
    w, h = img.size
    tile_size = w // h_splits
    grid = list(itertools.product(range(0, w, tile_size), range(0, h, tile_size)))
    imgs = []
    for i, j in grid:
        box = (i, j, i+tile_size, j+tile_size)
        imgs.append(img.crop(box))
    return imgs

def split_image_by_tile_size(img_name: str, tile_size):
    img = Image.open(img_name)
    w, h = img.size
    grid = list(itertools.product(range(0, w, tile_size), range(0, h, tile_size)))
    imgs = []
    print(len(grid))
    for i, j in grid:
        box = (i, j, i+tile_size, j+tile_size)
        imgs.append(img.crop(box))
    return imgs

def upload_image(client, file, filename, folder_name):
    global transfer
    if args.service == 'imgur':
        uploaded = client.upload_image(file, title=filename)
        return uploaded.link
    elif args.service == 's3':
        if not transfer:
            transfer = S3Transfer(client)
        transfer.upload_file(file, S3_BUCKET_NAME, filename, extra_args={'ACL': 'public-read'})
        return f'{client.meta.endpoint_url}/{S3_BUCKET_NAME}/{filename}'
    elif args.service == 'cloudinary':
        uploaded = upload(file, folder=folder_name, public_id=filename)
        return uploaded['secure_url']


if __name__ == "__main__":
    args = parser.parse_args()
    if not (args.count or args.tilesize):
        parser.error('You must specify either the tile count or the tile size')
    if args.count and args.tilesize:
        parser.error('You must specify only one between tile count and tile size')
    if args.count:
        imgs = split_image(args.image, args.count)
    elif args.tilesize:
        imgs = split_image_by_tile_size(args.image, args.tilesize)

    if args.service == 'imgur':
        import pyimgur
        client = pyimgur.Imgur(IMGUR_CLIENT_ID)
    elif args.service == 's3':
        import boto3
        from boto3.s3.transfer import S3Transfer
        client = boto3.client('s3', region_name='eu-central-1')
    elif args.service == 'cloudinary':
        from cloudinary.uploader import upload
        client = None

    image_name = args.image.replace(' ', '_')
    folder_name = os.path.splitext(image_name)[0]

    if not args.no_upload:
        commands = []

        with tempfile.TemporaryDirectory() as tempdir:
            for i, img in enumerate(imgs):
                filename = os.path.join(tempdir, str(i) + '_' + image_name)
                img.save(filename)
                uploaded = upload_image(client, filename, 'MapperinoTool_' + str(i) + '_' + image_name, folder_name)
                commands.append(f'/mapcreate {uploaded}')

        if args.output:
            with open(args.output) as f:
                f.write('\n'.join(commands))
        else:
            print('\n'.join(commands))
