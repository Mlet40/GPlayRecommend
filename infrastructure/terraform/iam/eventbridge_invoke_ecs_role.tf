data "aws_iam_policy_document" "eventbridge_invoke_ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eventbridge_invoke_ecs" {
  name               = "eventbridge_invoke_ecs"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_invoke_ecs_assume.json
}

data "aws_iam_policy_document" "eventbridge_invoke_ecs_policy" {
  statement {
    actions = [
      "ecs:RunTask",
      "iam:PassRole"
    ]
    resources = [
      aws_ecs_task_definition.featstore_task.arn,
      aws_iam_role.ecs_task_role.arn,
      aws_iam_role.ecs_execution_role.arn,
      aws_ecs_cluster.this.arn
    ]
  }
}

resource "aws_iam_role_policy" "eventbridge_invoke_ecs_policy_attach" {
  name   = "eventbridge_invoke_ecs_policy"
  role   = aws_iam_role.eventbridge_invoke_ecs.id
  policy = data.aws_iam_policy_document.eventbridge_invoke_ecs_policy.json
}
