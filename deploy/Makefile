Service=wordpress-server-construction-with-kusanagi
ProfileName = default
#################################
# codepipelineの設定
#################################
CodePipelineTemplate=make_codepipeline.yml
BuildSpecFileName=buildspec.ymls
BuilderImage=aws/codebuild/amazonlinux2-x86_64-standard:3.0
ArtifactBucket=codepipeline-ap-northeast-1-124898023392

RepositoryName=core-fargate
BranchName=${service}-docker

CodePipelineServiceRoleArn=arn:aws:iam::88888888888:role/service-role/AWSCodePipelineServiceRole-ap-northeast-1-e2e-codeceptjs-docker
CodeBuildServiceRoleArn=arn:aws:iam::88888888888:role/codebuild-wordpress-with-kusanagi-service-role

CfnPipelineStackName=${service}-pipeline
PipelineName=${service}-pipeline


# #####################################
# fargateのテンプレート
#######################################
FargateTemplate=make_fargate.yml
ECSTaskExecutionRole=arn:aws:iam::88888888888:role/ecsTaskExecutionRole
ECSClusterName=cluster
ECSTaskName=task
ECSTaskCPUUnit=512
ECSTaskMemory=1024
ECSTaskDesiredCount=1
LogGroup="/ecs"
ECRDomain=88888888888.dkr.ecr.ap-northeast-1.amazonaws.com

ProjectName=${service}
CfnFargateStackName=${service}-fargate
ECSContainerName1=${service}
ECSImageName1="$(ECRDomain)/${service}:latest"

deploy_codepipeline:
	aws --profile ${ProfileName} \
			cloudformation deploy \
			--stack-name ${CfnPipelineStackName} \
			--template-file ${CodePipelineTemplate} \
			--parameter-overrides \
				RepositoryName=$(RepositoryName)  \
				BranchName=$(BranchName) \
				PipelineName=$(PipelineName) \
				ArtifactBucket=$(ArtifactBucket) \
				BuildSpecFileName=$(BuildSpecFileName) \
				BuilderImage=$(BuilderImage) \
				CodePipelineServiceRoleArn=$(CodePipelineServiceRoleArn) \
				CodeBuildServiceRoleArn=$(CodeBuildServiceRoleArn)

remove_codepipeline:
	aws  --profile ${ProfileName} \
		  cloudformation delete-stack \
			--stack-name ${CfnPipelineStackName}

deploy_fargate:
	aws --profile ${ProfileName} \
		cloudformation deploy \
			--stack-name ${CfnFargateStackName} \
			--template-file ${FargateTemplate} \
			--parameter-overrides \
				ProjectName=$(ProjectName) \
				ECSClusterName=$(ECSClusterName) \
				ECSTaskName=$(ECSTaskName) \
				ECSTaskCPUUnit=$(ECSTaskCPUUnit) \
				ECSTaskMemory=$(ECSTaskMemory) \
				ECSContainerName1=$(ECSContainerName1) \
				ECSImageName1=$(ECSImageName1) \
				ECSTaskDesiredCount=$(ECSTaskDesiredCount) \
				ECSTaskExecutionRole=$(ECSTaskExecutionRole) \
				LogGroup=$(LogGroup)

remove_fargate:
	aws  --profile ${ProfileName} \
		cloudformation delete-stack \
			--stack-name ${CfnFargateStackName}