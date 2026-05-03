for f in valhalla/resources/ui/*
do
  file_base=$(basename "$f")
  py_f=${file_base%%.*}
  echo "compiled $py_f"
  pyuic6  $f > valhalla/gui/compiled/"${py_f}_ui.py"
done
