# datachef_banners
Project for the Datachef Banners assignment.

## Prerequisites
Before starting, make sure to:
1. Create a python 3.8 venv
2. Activate the venv `source venv/bin/activate`
3. Run `pip install -r requirements.txt`

## Flow
S3 <--> API Gateway <--> Lambda <--> DynamoDB

The banner serving website is hosted in an S3 bucket at http://datachef-banners.s3-website.eu-central-1.amazonaws.com.
To load banners for a certain campaign ID, add the campaign ID to the end of the URL as a query string, like so: `/?cam-id=<id>`, e.g.
http://datachef-banners.s3-website.eu-central-1.amazonaws.com/?cam-id=10.

The campaign ID and the current time quarter based (1, 2, 3, or 4) on the browser time are passed onto the `get-banners POST`
method of the datachef_banners REST API in API Gateway. The `get_banners POST` triggers the `get_banners` Lambda with
the campaign ID and time quarter as request body.

The `get_banners` Lambda uses the campaign ID and time quarter to perform a query on the banners DynamoDB table. The
query returns all banners for the campaign ID by revenue. If there are less than 5 results with revenue, the list of 
banners is appended with non-converting (0 revenue) banners. Finally, the list of banners is shuffled and returned.

## Banners table structure
The unique composite primary key of the DynamoDB banners table is as follows:

- Partition key: `cam_id` (campaign ID)
- Sort key: `rev_clk` (artificial combined key of revenue and click ID)

Clicks without conversion are equivalent to clicks without revenue, so for unconverted clicks we set `rev_clk` to `0.0_<click_id>`.

Using this structure, we can return the top revenue banners by simply querying the campaign ID and sorting descendingly.
To get the correct time quarter, we filter on the partition. This is fast enough, since partitioning by campaign ID thins
out the sizes of the partitions plenty.

## Stress test
To achieve 5000 request/min, we need to be able to handle at least 84 request/s. To test this, I've used Locust (https://locust.io). 
The get-banners POST method is called 100+/s for 2 minutes, resulting in 6000+ request/min. Results and the script used can be found in the 
`loadtest_2020_10_19.pdf` in the load_test folder.