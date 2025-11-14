#!/bin/sh

echo
echo '[VERSION AT src/cochl/sense/__init__.py]'
grep __version__ src/cochl/sense/__init__.py

echo

echo '[VERSION AT pyproject.toml]'
grep version pyproject.toml
echo

echo 'Do versions match? (y/n)'
read -r ANSWER1

# echo "${ANSWER1}"

if [ "${ANSWER1}" = "n" ]; then
  exit
fi

echo
git status
echo 'All changes are pushed? (y/n)'
read -r ANSWER2

# echo "${ANSWER2}"

if [ "${ANSWER2}" = "n" ]; then
  exit
fi

sudo apt install python3.10
sudo apt install python3-pip

# python3.10 -m pip install --upgrade virtualenv
# python3.10 -m virtualenv ./venv
# source ./venv/bin/activate

python3.10 --version
python3.10 -m pip install --upgrade pip
python3.10 -m pip install --upgrade build

rm -rf .github
rm -rf .idea
rm -rf .pytest_cache

rm -rf dist
mkdir dist

rm -rf samples
rm -rf tests
rm -rf .gitignore
rm -rf README_HOME_dot_pypirc.txt

python3.10 -m build
git reset --hard

python3.10 -m pip install --upgrade twine

cp -f ~/.test_pypirc ~/.pypirc
python3.10 -m twine upload dist/* --verbose --repository testpypi
rm -rf ~/.pypirc

# python3.10 -m pip install --index-url https://test.pypi.org/simple/ --no-deps cochl
# python3.10 -c 'import cochl.sense; print(cochl.sense.APIConfig())'
