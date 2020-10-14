import pandas as pd
import boto3
import json, time
from decimal import Decimal


def read_banner_csv(table_name, time_quarter):
    df = pd.read_csv(filepath_or_buffer=f"/Users/olivier/Downloads/banners/{time_quarter}/{table_name}_{time_quarter}.csv")
    df['time_quarter'] = int(time_quarter)
    return df


def insert_into_dynamo(pandas_table, dynamo_table):
    record_list = json.loads(pandas_table.to_json(orient="records"))

    with dynamo_table.batch_writer() as batch:
        for idx, record in enumerate(record_list):
            record["ban_id"] = Decimal(str(record["ban_id"]))
            record["cam_id"] = Decimal(str(record["cam_id"]))
            record["tq"] = Decimal(str(record["tq"]))
            record["con_id"] = Decimal(str(record["con_id"]))
            # print(record)
            batch.put_item(Item=record)
            if idx % 1000 == 0:
                print(str(idx)+"/179000")
                print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
pd.set_option('display.expand_frame_repr', False)
dynamodb = boto3.resource('dynamodb')

clicks_1 = read_banner_csv("clicks", "1")
clicks_2 = read_banner_csv("clicks", "2")
clicks_3 = read_banner_csv("clicks", "3")
clicks_4 = read_banner_csv("clicks", "4")
conversions_1 = read_banner_csv("conversions", "1")
conversions_2 = read_banner_csv("conversions", "2")
conversions_3 = read_banner_csv("conversions", "3")
conversions_4 = read_banner_csv("conversions", "4")

clicks = clicks_1.append(clicks_2).append(clicks_3).append(clicks_4)
clean_clicks = clicks.drop_duplicates().reset_index(drop=True)
conversions = conversions_1.append(conversions_2).append(conversions_3).append(conversions_4)
clean_conversions = conversions.drop_duplicates().reset_index(drop=True)

mother_df = clean_clicks.merge(clean_conversions, on="click_id", how="left", validate="one_to_one")
mother_df = mother_df.fillna(0)
mother_df["rev_clk"] = mother_df["revenue"].astype(str) + "_" + mother_df["click_id"].astype(str) # Artificial sort key

# Drop redundant columns & rename columns for DynamoDB to save costs
mother_df = mother_df.drop(columns=["time_quarter_y", "revenue", "click_id"])
mother_df = mother_df.rename(columns={'time_quarter_x':'time_quarter'})
mother_df.columns = ["ban_id", "cam_id", "tq", "con_id", "rev_clk"]
print(mother_df)

# Check for duplicate composite primary keys
dup_primary_keys = mother_df[mother_df.duplicated(subset=["cam_id", "rev_clk"])]
print(dup_primary_keys)
if dup_primary_keys.shape[0] == 0:
    insert_into_dynamo(mother_df, dynamodb.Table('datachef_banners'))
else:
    print("Something went wrong: duplicate composite primary keys were found!")

print("--- %s seconds ---" % (time.time() - start_time))

