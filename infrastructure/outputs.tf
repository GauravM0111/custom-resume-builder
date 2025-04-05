output "thumbnails_public_access_domain" {
  description = "Public facing domain for cloudfront, used to access thumbnails in S3"
  value = aws_cloudfront_distribution.thumbnails.domain_name
}

output "thumbnails_s3_bucket_domain_name" {
  value = aws_s3_bucket.thumbnails.bucket_domain_name
}