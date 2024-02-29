.PHONY: deploy_core

ARN=arn:aws:iam::111111111111:role/lambda_core_basic_execution

#----------------------------------------------
#deploy系
#----------------------------------------------
pip_install:
	pip install -r requirements.txt -t ./

#####################################
# core
#####################################
deploy_core_dev:
	env AWS_PROFILE=default \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=default" \
		--param="account_name=core"

remove_core_dev:
	env AWS_PROFILE=default \
	sls remove --verbose \
		--stage dev \
		--param="profile=default" \
		--param="account_name=core"

deploy_core_prod:
	env AWS_PROFILE=default \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=default" \
		--param="account_name=core"

remove_core_prod:
	env AWS_PROFILE=default \
	sls remove --verbose \
		--stage prod \
		--param="profile=default"\
		--param="account_name=core"


#####################################
# core
#####################################
deploy_orien_dev:
	env AWS_PROFILE=orien_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=orien_dev" \
		--param="account_name=orien"

remove_orien_dev:
	env AWS_PROFILE=orien_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=orien_dev" \
		--param="account_name=orien"

deploy_orien_prod:
	env AWS_PROFILE=orien_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=orien_prod" \
		--param="account_name=orien"

remove_orien_prod:
	env AWS_PROFILE=orien_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=orien_prod"\
		--param="account_name=orien"