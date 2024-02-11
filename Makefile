.PHONY: deploy_core

ARN=arn:aws:iam::707536174080:role/service-role/lambda_core_basic_execution

#----------------------------------------------
#deploy系
#----------------------------------------------

targets_dev=deploy_core_dev deploy_milight_dev deploy_imc_dev deploy_chocolat_dev deploy_acloud_dev deploy_reignite_dev

targets_prod=deploy_core_prod deploy_milight_prod deploy_imc_prod deploy_chocolat_prod deploy_acloud_prod deploy_reignite_prod

targets_dev_rm=remove_core_dev remove_milight_dev remove_imc_dev remove_chocolat_dev remove_acloud_dev remove_reignite_dev

targets_prod_rm=remove_core_prod remove_milight_prod remove_imc_prod remove_chocolat_prod remove_acloud_prod remove_reignite_prod


#####################################
# 全体
#####################################
deploy_all_dev: $(targets_dev)
	echo "Deploy all dev"

deploy_all_prod: $(targets_prod)
	echo "Deploy all prod"

remove_all_dev: $(targets_dev_rm)
	echo "Remove all dev"

remove_all_prod: $(targets_prod_rm)
	echo "Remove all prod"


pip_install:
	pip install -r requirements.txt -t ./

#####################################
# coretech
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
# Mi-light
#####################################
deploy_milight_dev:
	env AWS_PROFILE=milight_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=milight_dev" \
		--param="account_name=mil"

remove_milight_dev:
	env AWS_PROFILE=milight_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=milight_dev" \
		--param="account_name=mil"

deploy_milight_prod:
	env AWS_PROFILE=milight_prod \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage prod \
		--param="profile=milight_prod" \
		--param="account_name=mil"

remove_milight_prod:
	env AWS_PROFILE=milight_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=milight_prod" \
		--param="account_name=mil"

#####################################
# chocolat
#####################################
deploy_chocolat_dev:
	env AWS_PROFILE=chocolat_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=chocolat_dev" \
		--param="account_name=chocolat"

remove_chocolat_dev:
	env AWS_PROFILE=chocolat_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=chocolat_dev" \
		--param="account_name=chocolat"

deploy_chocolat_prod:
	env AWS_PROFILE=chocolat_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=chocolat_prod" \
		--param="account_name=chocolat"

remove_chocolat_prod:
	env AWS_PROFILE=chocolat_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=chocolat_prod" \
		--param="account_name=chocolat"

#####################################
# imc
#####################################
deploy_imc_dev:
	env AWS_PROFILE=imc_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=imc_dev" \
		--param="account_name=imc"

remove_imc_dev:
	env AWS_PROFILE=imc_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=imc_dev" \
		--param="account_name=imc"

deploy_imc_prod:
	env AWS_PROFILE=imc_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=imc_prod" \
		--param="account_name=imc"

remove_imc_prod:
	env AWS_PROFILE=imc_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=imc_prod" \
		--param="account_name=imc"

#####################################
# acloud
#####################################
deploy_acloud_dev:
	env AWS_PROFILE=acloud_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=acloud_dev" \
		--param="account_name=acl"

remove_acloud_dev:
	env AWS_PROFILE=acloud_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=acloud_dev" \
		--param="account_name=acl"

deploy_acloud_prod:
	env AWS_PROFILE=acloud_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=acloud_prod" \
		--param="account_name=acl"


remove_acloud_prod:
	env AWS_PROFILE=acloud_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=acloud_prod" \
		--param="account_name=acl"

#####################################
# reignite
#####################################
deploy_reignite_dev:
	env AWS_PROFILE=reignite_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=reignite_dev" \
		--param="account_name=reignite"

remove_reignite_dev:
	env AWS_PROFILE=reignite_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=reignite_dev" \
		--param="account_name=reignite"

deploy_reignite_prod:
	env AWS_PROFILE=reignite_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=reignite_prod" \
		--param="account_name=reignite"

remove_reignite_prod:
	env AWS_PROFILE=reignite_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=reignite_prod" \
		--param="account_name=reignite"

#####################################
# fanne
#####################################
deploy_fanne_dev:
	env AWS_PROFILE=fanne_dev \
	sls deploy --verbose \
		--param="check_alarm=NO" \
		--stage dev \
		--param="profile=fanne_dev" \
		--param="account_name=fanne"

remove_fanne_dev:
	env AWS_PROFILE=fanne_dev \
	sls remove --verbose \
		--stage dev \
		--param="profile=fanne_dev" \
		--param="account_name=fanne"

deploy_fanne_prod:
	env AWS_PROFILE=fanne_prod \
	sls deploy --verbose \
		--param="check_alarm=YES" \
		--stage prod \
		--param="profile=fanne_prod" \
		--param="account_name=fanne"

remove_fanne_prod:
	env AWS_PROFILE=fanne_prod \
	sls remove --verbose \
		--stage prod \
		--param="profile=fanne_prod" \
		--param="account_name=fanne"

