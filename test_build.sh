mkdir Release
mkdir Release/plugins

cp Engine/* Release
cp Engine/plugins/* Release/plugins

cp Tool/kmake.py Release/plugins
cp Sample/* Release
cd Release/plugins

python kmake.py kicom.lst
python kmake.py kernel.py
python kmake.py kavutil.py
python kmake.py pefile.py
python kmake.py emalware.py
python kmake.py zip.py
python kmake.py ole.py
python kmake.py hwp.py
python kmake.py dummy.py
python kmake.py eicar.py

rm -rf *.pyc
rm -rf kicom.lst

cp kavutil.py ..
cd ..

cp ../Test/* .

