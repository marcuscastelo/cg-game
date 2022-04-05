# If current folder does not contain vendor folder, then exit
if [ ! -d vendor ]; then
    echo "There is no vendor folder in current folder. Exiting..."
    exit 1
fi

cd vendor
for i in *; do
    if [ -d $i ]; then
        cd $i
        pip install -e .
        cd ..
    fi
done