
data "aws_ssm_parameter" "ecs_amazon_linux_2" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"
}

locals {
  ecs_optimized_ami  = jsondecode(data.aws_ssm_parameter.ecs_amazon_linux_2.value)["image_id"]
  frontend_image_uri = "${aws_ecr_repository.primary.repository_url}:${var.frontend_image_tag}"
  backend_image_uri  = "${aws_ecr_repository.primary.repository_url}:${var.backend_image_tag}"
}

# entity mining VM
data "archive_file" "entity_miner_zip" {
  type        = "zip"
  source_file = "${path.module}/../../backend/lambda/entity_miner.py"
  output_path = "${path.module}/../../backend/lambda/entity_miner.zip"
}

resource "aws_lambda_function" "entity-miner" {
  function_name    = "entity-miner"
  role             = aws_iam_role.entity_miner_lambda_role.arn
  handler          = "entity_miner.lambda_handler"
  runtime          = "python3.9"
  filename         = data.archive_file.entity_miner_zip.output_path
  source_code_hash = data.archive_file.entity_miner_zip.output_base64sha256

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.backend.id]
  }
}

# ECS Cluster and Capacity
resource "aws_ecs_cluster" "novelwriter" {
  name = "novelwriter-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

resource "aws_launch_template" "ecs" {
  name_prefix   = "novelwriter-ecs-"
  image_id      = local.ecs_optimized_ami
  instance_type = "t3.small"

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  vpc_security_group_ids = [aws_security_group.ecs_instances.id]

  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo ECS_CLUSTER=${aws_ecs_cluster.novelwriter.name} >> /etc/ecs/ecs.config
  EOF
  )

  monitoring {
    enabled = false
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "novelwriter-ecs-host"
    }
  }
}

resource "aws_autoscaling_group" "ecs" {
  name                      = "novelwriter-ecs-asg"
  desired_capacity          = 1
  max_size                  = 2
  min_size                  = 1
  vpc_zone_identifier       = [aws_subnet.private.id]
  health_check_grace_period = 300
  health_check_type         = "EC2"
  capacity_rebalance        = true

  launch_template {
    id      = aws_launch_template.ecs.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "novelwriter-ecs-host"
    propagate_at_launch = true
  }

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}

resource "aws_ecs_capacity_provider" "novelwriter" {
  name = "novelwriter-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.ecs.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
      minimum_scaling_step_size = 0
      maximum_scaling_step_size = 2
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "novelwriter" {
  cluster_name       = aws_ecs_cluster.novelwriter.name
  capacity_providers = [aws_ecs_capacity_provider.novelwriter.name]

  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.novelwriter.name
    weight            = 1
    base              = 0
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "frontend" {
  family                   = "novelwriter-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.frontend_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = local.frontend_image_uri
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "novelwriter-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.backend_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = local.backend_image_uri
      essential = true
      portMappings = [
        {
          containerPort = 7000
          hostPort      = 7000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "CHROMA_HOST"
          value = aws_instance.chroma_server.private_ip
        },
        {
          name  = "CHROMA_PORT"
          value = "8000"
        }
      ]
    }
  ])
}

# ECS Service

resource "aws_ecs_service" "frontend" {
  name                               = "novelwriter-frontend-service"
  cluster                            = aws_ecs_cluster.novelwriter.id
  task_definition                    = aws_ecs_task_definition.frontend.arn
  desired_count                      = 2
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 80
  }

  network_configuration {
    subnets          = [aws_subnet.private.id]
    security_groups  = [aws_security_group.frontend.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_lb_listener.main,
    aws_ecs_cluster_capacity_providers.novelwriter
  ]
}

resource "aws_ecs_service" "backend" {
  name                               = "novelwriter-backend-service"
  cluster                            = aws_ecs_cluster.novelwriter.id
  task_definition                    = aws_ecs_task_definition.backend.arn
  desired_count                      = 2
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 7000
  }

  network_configuration {
    subnets          = [aws_subnet.private.id]
    security_groups  = [aws_security_group.backend.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_lb_listener_rule.backend,
    aws_ecs_cluster_capacity_providers.novelwriter
  ]
}

# Auto Scaling Policies 

resource "aws_appautoscaling_target" "frontend" {
  max_capacity       = 2
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.novelwriter.name}/${aws_ecs_service.frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.frontend]
}

resource "aws_appautoscaling_policy" "frontend_cpu" {
  name               = "novelwriter-frontend-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "frontend_requests" {
  name               = "novelwriter-frontend-requests"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.webapp.arn_suffix}/${aws_lb_target_group.frontend.arn_suffix}"
    }
    target_value       = 2000
    scale_in_cooldown  = 120
    scale_out_cooldown = 120
  }
}

resource "aws_appautoscaling_target" "backend" {
  max_capacity       = 2
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.novelwriter.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.backend]
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "novelwriter-backend-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 60
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "backend_requests" {
  name               = "novelwriter-backend-requests"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.webapp.arn_suffix}/${aws_lb_target_group.backend.arn_suffix}"
    }
    target_value       = 1000
    scale_in_cooldown  = 120
    scale_out_cooldown = 120
  }
}

