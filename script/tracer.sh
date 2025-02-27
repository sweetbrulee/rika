# viztracer 是用來追蹤 Python 程式的工具，可以用來分析程式每個函數的執行效能。

# if no .viztracer folder, create one
if [ ! -d ".viztracer" ]; then
  mkdir .viztracer
fi

viztracer -o .viztracer/result.json -- src/main.py;