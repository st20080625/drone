import subprocess
import os

def run_script(script_name, x, y):
    """指定されたPythonスクリプトをサブプロセスで実行し、ウィンドウ位置を設定"""
    return subprocess.Popen(
        ["python", script_name],
        env={**os.environ, "SDL_VIDEO_WINDOW_POS": f"{x},{y}"}
    )

if __name__ == "__main__":
    # スクリプトをサブプロセスで実行し、ウィンドウ位置を設定
    process1 = run_script("3d.quaternion.py", 100, 100)  # 左側のウィンドウ位置
    process2 = run_script("3d.euler.py", 800, 100)      # 右側のウィンドウ位置

    try:
        # メインプロセスを待機状態にする
        process1.wait()
        process2.wait()
    except KeyboardInterrupt:
        # Ctrl+C で終了した場合、サブプロセスを終了
        process1.terminate()
        process2.terminate()