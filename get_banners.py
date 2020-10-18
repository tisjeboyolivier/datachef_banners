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

    # A click without conversion is equivalent to 0.0 revenue
    with_conv = []
    without_conv = []
    for item in all_banners["Items"]:
        if not item.get("rev_clk").startswith("0.0_"):
            with_conv.append(item.get("ban_id"))
        else:
            without_conv.append(item.get("ban_id"))

    banner_ids = determine_banners(with_conv, len(with_conv), without_conv, len(without_conv))

    return {
        "statusCode": 200,
        "cam_id": cam_id,
        "tq": tq,
        "banner_ids": banner_ids
    }


def determine_banners(with_conv, conv_count, without_conv, without_conv_count):
    if conv_count >= 10:
        return with_conv[:10]
    elif 5 <= conv_count <= 9:
        return with_conv[:conv_count]
    elif 4 <= conv_count <= 1:
        needed_for_five = 5 - conv_count
        return with_conv[:conv_count] + without_conv[:needed_for_five]
    elif conv_count == 0:
        return without_conv[:without_conv_count]
    else:
        print("Something went wrong: negative item count")
        return "Error: negative item count"
