import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    banners_table = dynamodb.Table("datachef_banners")

    cam_id = event.get("cam_id")
    tq = event.get("tq")

    all_banners = banners_table.query(
        KeyConditionExpression=Key("cam_id").eq(cam_id),
        FilterExpression=Attr("tq").eq(tq),
        ProjectionExpression="ban_id,rev_clk",
        ScanIndexForward=False
    )

    # Clicks without conversion is equivalent to 0.0 revenue
    conversion_count = 0
    for item in all_banners["Items"]:
        if not item.get("rev_clk").startswith("0.0_"):
            conversion_count += 1
    all_ban_ids = [d.get("ban_id") for d in all_banners["Items"]]

    banner_ids = determine_banners(all_ban_ids, conversion_count)

    return {
        "statusCode": 200,
        "cam_id": cam_id,
        "tq": tq,
        "banner_ids": banner_ids
    }


def determine_banners(items, item_count):
    if item_count >= 10:
        return items[:10]
    elif 5 <= item_count <= 9:
        return items[:item_count]
    elif 4 <= item_count <= 1:
        return items[:item_count]
    elif item_count == 0:
        return "0 items with revenue"
    else:
        print("Something went wrong: negative item count!")
        return "Error: negative item count"
