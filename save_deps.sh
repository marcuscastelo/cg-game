# Script to update requirements.txt

# List dependencies, remove -e and split by newline
installed_packages=$(pip freeze | grep -v '^\-e')
# installed_packages=$(pip freeze | grep -v '^\-e' | cut -d = -f 1)

rm -f requirements.txt
for i in $installed_packages; do
    echo $i >> requirements.txt
done