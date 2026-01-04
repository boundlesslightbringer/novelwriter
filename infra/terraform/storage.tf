resource "aws_s3_bucket" "stories" {
  bucket = "novelwriter-stories-primary-26-11-2025"
}

resource "aws_s3_bucket_notification" "stories_notification" {
  bucket = aws_s3_bucket.stories.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.entity-miner.arn
    events              = ["s3:ObjectCreated:Put", "s3:ObjectCreated:Post"]
  }

  depends_on = [aws_lambda_function.entity-miner]
}

resource "aws_s3_bucket" "otel-data" {
  bucket = "novelwriter-otel-data-primary-30-12-2025"
}