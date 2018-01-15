PATH := ./redis-git/src:${PATH}
VERSION=`cat Version`

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean           remove temporary files created by build tools"
	@echo "  cleanmeta       removes all META-* and egg-info/ files created by build tools"
	@echo "  cleancov        remove all files related to coverage reports"
	@echo "  cleanall        all the above + tmp files from development tools"
	@echo "  dist            make a source and wheel distribution"
	@echo " *** CI Commands ***"

clean:
	-rm -f MANIFEST
	-rm -rf dist/
	-rm -rf build/

cleancov:
	-rm -rf htmlcov/
	-coverage combine
	-coverage erase

cleanmeta:
	-rm -rf redis_pubsub_dict.egg-info/

cleanall: clean cleancov cleanmeta
	-find . -type f -name "*~" -exec rm -f "{}" \;
	-find . -type f -name "*.orig" -exec rm -f "{}" \;
	-find . -type f -name "*.rej" -exec rm -f "{}" \;
	-find . -type f -name "*.pyc" -exec rm -f "{}" \;
	-find . -type f -name "*.parse-index" -exec rm -f "{}" \;

dist: cleanmeta
	-pandoc --from=markdown --to=rst --output=README.rst README.md
	-python setup.py sdist bdist_wheel

package: dist
	-twine upload dist/redis_pubsub_dict-$(VERSION).tar.gz

version:
	-echo "$(VERSION)"

travis-run:
	python setup.py test
