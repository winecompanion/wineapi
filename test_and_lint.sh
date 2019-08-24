python manage.py test api/tests/
python manage.py test users/


echo -e "\nLinting codebase\n"

if ! flake8 .; then
	echo -e "\nLinter has shown errors!\n"
else
	echo "OK"
fi
