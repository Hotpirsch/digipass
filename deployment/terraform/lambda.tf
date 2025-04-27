# # install python requirements for lambda layer
# resource "null_resource" "pip_install" {
#   triggers = {
#     shell_hash = "${sha256(file("${path.root}/../../src/lambda/requirements.txt"))}"
#   }
#   provisioner "local-exec" {
#     command = "python -m pip install -r ${path.root}/../../src/lambda/requirements.txt -t ${path.root}/../../package/layer/python"
#   }
# }
# # create Python requirements layer
# data "archive_file" "lambda_requirements" {
#   type        = "zip"
#   source_dir  = "${path.root}/../../package/layer"
#   output_path = "${path.root}/../../package/layer.zip"
#   depends_on  = [null_resource.pip_install]
# }

# resource "aws_lambda_layer_version" "modules" {
#   layer_name          = "module-layer"
#   filename            = data.archive_file.lambda_requirements.output_path
#   source_code_hash    = data.archive_file.lambda_requirements.output_base64sha256
#   compatible_runtimes = ["python3.12", "python3.11", "python3.10"]
# }


data "archive_file" "python_lambda_package" {  
  type = "zip"  
  source_dir = "${path.module}/../../src/lambda"
  output_path = "${path.module}/../../package/lambda.zip"
}

resource "aws_lambda_function" "rml_member_pass" {
  function_name = "rml-pass-check"
  description = "Lambda function to check membership in RML"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "check-membership.lambda_handler"
  runtime       = "python3.12" // Replace with your runtime
  filename      = data.archive_file.python_lambda_package.output_path
  # layers        = [aws_lambda_layer_version.modules.arn]  
  memory_size   = 128
  timeout       = 30
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
}

resource "aws_lambda_function_url" "rml_member_pass_url" {
  function_name      = aws_lambda_function.rml_member_pass.function_name
  authorization_type = "NONE"
}

output "function_url" {
  value = aws_lambda_function_url.rml_member_pass_url.function_url
  description = "The URL of the Lambda function"
}