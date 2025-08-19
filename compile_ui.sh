for f in qvalhalla/resources/ui/*
do
  file_base=$(basename "$f")
  py_f=${file_base%%.*}
  echo "compiled $py_f"
  pyuic5  $f > qvalhalla/gui/compiled/"${py_f}_ui.py"
done
