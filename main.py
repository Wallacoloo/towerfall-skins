#!/usr/bin/python3

import os, shutil, xml.etree.ElementTree

from PIL import Image

#default_atlas_dir = "/home/colin/.local/share/Steam/steamapps/common/TowerFall/Content/Atlas"
#default_atlas_dir = "/home/colin/.local/share/Steam/steamapps/common/TowerFall/DarkWorldContent/Atlas"
default_towerfall_dir = "/home/colin/.local/share/Steam/steamapps/common/TowerFall"

class Atlas(object):
    def __init__(self, towerfall_dir):
        self.atlas_png_path = os.path.join(towerfall_dir, "DarkWorldContent/Atlas/atlas.png")
        self.atlas_xml_path = os.path.join(towerfall_dir, "DarkWorldContent/Atlas/atlas.xml")
        self.sprite_data_path = os.path.join(towerfall_dir, "Content/Atlas/SpriteData/spriteData.xml")
        self.backup()
        self.atlas_png = Image.open(self.atlas_png_path)
        self.atlas_xml = xml.etree.ElementTree.parse(self.atlas_xml_path).getroot()
        self.sprite_data_xml = xml.etree.ElementTree.parse(self.sprite_data_path).getroot()
    def backup(self):
        """Copy all files to local directory before editing them"""
        shutil.copyfile(self.atlas_png_path, "backup/atlas.png")

    def patch_all(self):
        self.patch_sprite("PlayerBody0")
        #for texname in os.listdir("res"):
        #    frames = sorted(os.listdir(os.path.join("res", texname)))
        #    self.patch_one(texname.replace("_", "/"), frames)
    def patch_sprite(self, spriteid):
        sprite = self.sprite_data_xml.findall("./sprite_string[@id='{}']".format(spriteid))[0]
        frame_size = (int(sprite.find("./FrameWidth").text), int(sprite.find("./FrameHeight").text))
        texid = sprite.find("./Texture").text

        tex = self.atlas_xml.find("./SubTexture[@name='{}']".format(texid))
        palette_size_px = (int(tex.get("width")), int(tex.get("height")))
        palette_loc  = (int(tex.get("x")), int(tex.get("y")))

        # Location of frames, on disk.
        frame_paths = sorted(os.listdir(os.path.join("res", texid)))
        for frame_path in frame_paths:
            # Get the basename of the leaf, e.g. 0001 in "0001.png"
            frame_id = int(os.path.splitext(frame_path)[0])
            full_path = os.path.join("res", texid, frame_path)
            img = Image.open(full_path)

            # Get the pixel offset of this frame relative to the subtexture.
            offset = frame_id*frame_size[0]
            offset = divmod(offset, palette_size_px[0])
            offset = (offset[1], offset[0] * palette_size_px[1])

            global_coord = (palette_loc[0] + offset[0], palette_loc[1] + offset[1])
            self.patch_frame(img, global_coord, frame_size)

    def patch_frame(self, frame_img, global_coord, frame_size):
        """Scale the image to the given size, and then insert it into the atlas.png"""
        # Resize to necessary size (default resize uses nearest neighbor)
        frame_img = frame_img.resize(frame_size)
        # Overwrite the image in the atlas
        print("Patching frame at {} size {}".format(global_coord, frame_size))
        self.atlas_png.paste(frame_img, global_coord)

    def write(self):
        """Write changes to disk"""
        print("Writing atlas to", self.atlas_png_path)
        self.atlas_png.save(self.atlas_png_path)


if __name__ == "__main__":
    atlas = Atlas(default_towerfall_dir)
    atlas.patch_all()
    atlas.write()
