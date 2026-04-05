output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "glue_database_name" {
  description = "The name of the Glue database"
  value       = aws_glue_catalog_database.analytics_db.name
}

output "athena_workgroup" {
  description = "The name of the Athena workgroup"
  value       = aws_athena_workgroup.analytics_wg.name
}

output "athena_results_location" {
  description = "The S3 location where Athena query results are stored"
  value       = "s3://${aws_s3_bucket.data_lake.bucket}/athena-results/"
}
