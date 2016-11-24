start-docker:
	docker run -d -p 27017:27017 -p 28017:28017 -e MONGODB_USER="fdtest" -e MONGODB_DATABASE="foodie_test" -e MONGODB_PASS="fdtest" tutum/mongodb
