# Mapperino

Small tool to slice an image in smaller squares and upload each square to an online service such as imgur or Amazon S3.

The main objective of this tool is to provide a way for users to create big images in Minecraft while using the [Image2Map](https://github.com/TheEssem/Image2Map) mod for Fabric.

## Setup and Usage

```
usage: main.py [-h] [-c COUNT] [-t TILESIZE] [-o OUTPUT]
               [--no-upload]
               {imgur,s3,cloudinary} image

Split an image, upload it to imgur and automatically write the
commands in game to create maps

positional arguments:
  {imgur,s3}            Service to use to upload images
  image                 The image to split

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Number of splits
  -t TILESIZE, --tilesize TILESIZE
                        Size of the tiles in px
  -o OUTPUT, --output OUTPUT
                        Output the commands on the file instead of
                        stdout
  --no-upload           Prevents upload of images, for testing
```

The tool allows to specify either the number of horizontal splits or the size of the split. The splits will all be squares, which means that the vertical split cannot be specified indipendently.

The user must either create an [imgur](https://imgur.com/) or an [Amazon AWS](https://aws.amazon.com) account.

### Imgur

For imgur, the client ID should be assigned to a `IMGUR_CLIENT_ID` environment variable.

Then, use the command with `imgur` as a service, for example:

```
python main.py imgur my_image.png -c 3
```

### S3

For Amazon AWS S3, you should install the AWS CLI tool and run `aws configure` (if you haven't previously done so).

Afterwards, just run the command with `s3` as a service, for example:

```
python main.py s3 my_image.png -c 3
```

### Cloudinary

For Cloudinary, make sure you have the CLOUDINARY_URL environment variable set, it should look like this: 
`CLOUDINARY_URL=cloudinary://API-Key:API-Secret@Cloud-name`

Then you can run the command with `cloudinary` as a service, for example:

```
python main.py cloudinary my_image.png -c 3
```
