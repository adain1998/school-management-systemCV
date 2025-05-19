# Makefile pour gérer les templates HTML avec blueprint dynamique

.PHONY: update restore

update:
	python update_templates.py

restore:
	python update_templates.py restore
