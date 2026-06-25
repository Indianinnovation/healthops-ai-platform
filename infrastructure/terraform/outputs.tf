output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "data_lake_bucket" {
  value = aws_s3_bucket.data_lake.id
}
