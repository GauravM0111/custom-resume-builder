# S3 bucket to store all thumbnails
resource "aws_s3_bucket" "thumbnails" {
  bucket_prefix = "thumbnails-resume-builder"
}

resource "aws_s3_bucket_policy" "grant_read_permissions_to_cloudfront" {
  bucket = aws_s3_bucket.thumbnails.id
  policy = data.aws_iam_policy_document.grant_read_permissions_to_cloudfront.json
}

data "aws_iam_policy_document" "grant_read_permissions_to_cloudfront" {
  statement {
    principals {
      type = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.thumbnails.arn,
      "${aws_s3_bucket.thumbnails.arn}/*",
    ]

    condition {
      test = "StringEquals"
      variable = "aws:SourceArn"
      values = [aws_cloudfront_distribution.thumbnails.arn]
    }
  }
}

# CDN for caching and serving thumbnails
resource "aws_cloudfront_distribution" "thumbnails" {
  enabled = var.enable_thumbnails_distribution

  origin {
    domain_name = aws_s3_bucket.thumbnails.bucket_domain_name
    origin_id = aws_s3_bucket.thumbnails.id
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_origin_access_control.id
  }

  default_cache_behavior {
    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods = ["GET", "HEAD"]
    cache_policy_id = aws_cloudfront_cache_policy.thumbnails.id
    viewer_protocol_policy = "https-only"
    target_origin_id = aws_s3_bucket.thumbnails.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations = []
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

resource "aws_cloudfront_cache_policy" "thumbnails" {
  name = "thumbnails-cache-policy"
  min_ttl = 10
  max_ttl = 86400
  default_ttl = 300

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"]
      }
    }

    query_strings_config {
      query_string_behavior = "none"
    }

    enable_accept_encoding_gzip = true
    enable_accept_encoding_brotli = true
  }
}

resource "aws_cloudfront_origin_access_control" "s3_origin_access_control" {
  name = "thumbnails-s3-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior = "always"
  signing_protocol = "sigv4"
}