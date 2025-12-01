resource "aws_s3_bucket" "stories" {
  bucket = "novelwriter-stories-primary-26-11-2025"
}

resource "aws_s3_bucket_notification" "stories_notification" {
  bucket = aws_s3_bucket.stories.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.entity-miner.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_function.entity-miner]
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.entity-miner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.stories.arn
}