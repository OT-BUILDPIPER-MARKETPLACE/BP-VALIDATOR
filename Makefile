build:
	docker build -t opstree/tagvalidator:0.1 .

run:
	docker run -it --rm --name tagvalidator -v ~/.aws:/root/.aws -v ${data_dir}:/opt/  opstree/tagvalidator:0.1

run-debug:
	docker run -it --rm --name tagvalidator -v ~/.aws:/root/.aws/ -v ${data_dir}:/opt/ --entrypoint sh opstree/tagvalidator:0.1