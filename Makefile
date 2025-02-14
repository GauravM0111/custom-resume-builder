.PHONY: build
build:
	npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css
	docker compose build --no-cache

.PHONY: run
run:
	npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css
	docker compose down
	docker compose up

.PHONY: tailwind
tailwind:
	npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch
