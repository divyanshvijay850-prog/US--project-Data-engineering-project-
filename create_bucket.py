# ============================================================
# FILE: create_bucket.py
# PURPOSE: User se bucket ka naam lo, AWS S3 pe banao,
#          aur ek file upload karo
# ============================================================

import os        
import boto3
from botocore.exceptions import ClientError
 

# AWS region
REGION = "us-east-1"

# ---------------------------------------------------------------
# FUNCTION: create_bucket
# ---------------------------------------------------------------
def create_bucket(bucket_name):

    print(f"\n[INFO] '{bucket_name}' bucket banayi ja rahi hai...")

    s3_client = boto3.client("s3", region_name=REGION)

    try:
        if REGION == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": REGION
                }
            )

        print(f"[SUCCESS] '{bucket_name}' bucket ban gayi!")
        return True

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        if error_code == "BucketAlreadyExists":
            print(f"[ERROR] '{bucket_name}' bucket pehle se exist karti hai!")
        elif error_code == "BucketAlreadyOwnedByYou":
            print(f"[INFO] '{bucket_name}' bucket pehle se tumhari hai!")
        elif error_code == "InvalidBucketName":
            print(f"[ERROR] Bucket naam galat hai!")
            print(f"        Sirf small letters, numbers aur hyphen use karo!")
        else:
            print(f"[ERROR] Bucket nahi bani: {error}")

        return False


# ---------------------------------------------------------------
# FUNCTION: upload_file
# WHAT IT DOES: Local file ko S3 bucket mein upload karta hai
# PARAMETERS:
#   local_file_path  (str) - tumhare computer pe file ka path
#   bucket_name      (str) - jis bucket mein dalni hai
#   s3_file_name     (str) - S3 pe file ka naam (optional)
#                            agar None diya toh local naam use hoga
# RETURNS: True agar upload hua, False agar nahi
# ---------------------------------------------------------------
def upload_file(local_file_path, bucket_name, s3_file_name=None):

    # Agar S3 pe alag naam nahi diya toh local file ka naam use karo
    if s3_file_name is None:
        s3_file_name = local_file_path.split("/")[-1]  # sirf filename, path nahi

    print(f"\n[INFO] File upload ho rahi hai...")
    print(f"       Local  : {local_file_path}")
    print(f"       Bucket : {bucket_name}")
    print(f"       S3 Key : {s3_file_name}")

    s3_client = boto3.client("s3", region_name=REGION)

    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
        print(f"[ SUCCESS] File upload ho gayi!")
        print(f"[LINK]   s3://{bucket_name}/{s3_file_name}")
        return True

    except FileNotFoundError:
        print(f"[ERROR] File nahi mili: '{local_file_path}'")
        print(f"        Check karo path sahi hai ya nahi!")
        return False

    except ClientError as error:
        print(f"[ERROR] Upload fail hua: {error}")
        return False


# ---------------------------------------------------------------
# FUNCTION: get_bucket_name_from_user
# ---------------------------------------------------------------
def get_bucket_name_from_user():

    print("\n" + "="*50)
    print("      AWS S3 BUCKET CREATOR")
    print("="*50)
    print("\n Bucket Naam Rules:")
    print("    Sirf small letters  → abc")
    print("    Numbers             → 123")
    print("    Hyphen              → -")
    print("    Capital letters     → ABC")
    print("    Underscore          → _")
    print("    Space")
    print("-"*50)

    while True:

        bucket_name = input("\n Create bucket name : ").strip()

        if not bucket_name:
            print("[ERROR] Naam empty hai! Dobara likho.")
            continue

        if bucket_name != bucket_name.lower():
            print("[ERROR] Capital letters use mat karo! Sirf small letters.")
            continue

        if "_" in bucket_name:
            print("[ERROR] Underscore ( _ ) allowed nahi! Hyphen ( - ) use karo.")
            continue

        if " " in bucket_name:
            print("[ERROR] Space allowed nahi!")
            continue

        if len(bucket_name) < 3 or len(bucket_name) > 63:
            print("[ERROR] Naam 3 se 63 characters ke beech hona chahiye!")
            continue

        return bucket_name


# ----- ENTRY POINT -----
if __name__ == "__main__":

    # Step 1: User se bucket naam lo
    bucket_name = get_bucket_name_from_user()

    # Step 2: Bucket banao
    bucket_ready = create_bucket(bucket_name)

    # Step 3: Agar bucket ban gayi toh sabhi 6 files upload karo
    if bucket_ready:

        # Auto path generate hoga — manually likhne ki zaroorat nahi
        files_to_upload = []
        for year in [2021, 2022]:
            for month in range(1, 4):   # 1, 2, 3
                local_path = (
                    f"./downloaded_files/"
                    f"On_Time_Reporting_Carrier_On_Time_Performance_"
                    f"1987_present_{year}_{month}.csv"
                )
                s3_name = s3_name = f"flights/year={year}/month={month:02d}/data.csv"
                files_to_upload.append((local_path, s3_name))

        # Counter
        success_count = 0
        fail_count    = 0

        for local_path, s3_name in files_to_upload:

            #  Check 1: Local file exist karti hai?
            if not os.path.exists(local_path):
                print(f"\n[ STOP] File nahi mili: {local_path}")
                print(f"         Aage upload band — pehle download karo!")
                break   # poora loop band — koi aur file upload nahi hogi

            #  Check 2: S3 pe pehle se exist toh nahi?
            s3_client = boto3.client("s3", region_name=REGION)
            try:
                s3_client.head_object(Bucket=bucket_name, Key=s3_name)
                print(f"\n[INFO] Already S3 pe hai: {s3_name} (skipping)")
                success_count += 1
                continue   # yeh file skip, agli pe jao

            except ClientError:
                pass   # S3 pe nahi hai — theek hai, upload karo

            # Upload karo
            result = upload_file(local_path, bucket_name, s3_name)

            if result:
                success_count += 1
            else:
                print(f"[ STOP] Upload fail hua: {s3_name}")
                print(f"         Aage upload band!")
                break   # agar koi bhi fail ho toh poora band

        # Final summary
        print(f"\n{'='*50}")
        print(f"  UPLOAD SUMMARY")
        print(f"{'='*50}")
        print(f"   Successful : {success_count}/{len(files_to_upload)}")
        print(f"   Failed     : {fail_count}/{len(files_to_upload)}")
        print(f"{'='*50}")