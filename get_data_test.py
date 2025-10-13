from astroquery.sdss import SDSS
from astropy import coordinates as coords
import astropy.units as u
import requests
import pandas as pd
import os
import tqdm
import argparse

SDSS.clear_cache()
query_bands = ["u", "g", "r", "i", "z"]

def download_data(reference_path, parent_dir, LOG_INTERVAL=10):
    CATALOG = pd.read_csv(reference_path)
    sub_folder = reference_path.split("/")[-1][:-4]

    dest_path = os.path.join(parent_dir, sub_folder)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    QUERY_FAIL = []
    IMAGE_FAIL = []
    bar = tqdm.tqdm(range(len(CATALOG[:20])))


    for i in bar:
        ra, dec = CATALOG.iloc[i]["ra"], CATALOG.iloc[i]["dec"]

        pos = coords.SkyCoord(ra, dec, unit="deg", frame="icrs")

        for b in query_bands:
            try:
                imgs = SDSS.get_images(coordinates=pos, radius=20*u.arcsec, band=b, data_release=17)
                imgs[0].writeto(os.path.join(dest_path, f"{b}_{i+1:06}.fits"), overwrite=True)
            except:
                print(f"image not found :{i}", flush=True)
                IMAGE_FAIL += [i]


        #JPEG
        url = f"https://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?ra={ra}&dec={dec}&scale=0.4&width=512&height=512"
        r = requests.get(url)
        open(os.path.join(dest_path, f"{i+1:06}.jpg"), "wb").write(r.content)   
    
        if bar.n % LOG_INTERVAL == 0:
            print(str(bar), flush=True)


    return QUERY_FAIL, IMAGE_FAIL

if __name__=="__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-r","--ref_csv")
    parser.add_argument("-d","--dest_path")
    parser.add_argument("-l","--log_int", default=10)

    args = parser.parse_args()



    download_data(args.ref_csv, args.dest_path, int(args.log_int))