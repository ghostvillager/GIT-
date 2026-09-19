# update_git.pyw
import sys
import os
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox

def run_git(cmd, cwd):
    result = subprocess.run(
        ["git"] + cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result.returncode == 0, result.stdout + result.stderr

def main():
    if len(sys.argv) < 2:
        return

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        return

    # Gitリポジトリかチェック（ここで弾く）
    ok, _ = run_git(["rev-parse", "--is-inside-work-tree"], folder)
    if not ok:
        # Gitじゃないフォルダでは何も出さない（静かに終了）
        return

    # 変更があるか確認
    ok, status = run_git(["status", "--porcelain"], folder)
    if not status.strip():
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Git更新", "変更がありません")
        return

    root = tk.Tk()
    root.withdraw()

    msg = simpledialog.askstring(
        "Git更新",
        "コミットメッセージを入力してください:\n（空欄の場合は「Update」になります）",
        parent=root
    )

    if msg is None:  # キャンセル
        return
    if not msg.strip():
        msg = "Update"

    try:
        ok, out = run_git(["add", "."], folder)
        if not ok:
            raise Exception(f"git add 失敗:\n{out}")

        ok, out = run_git(["commit", "-m", msg], folder)
        if not ok:
            raise Exception(f"git commit 失敗:\n{out}")

        ok, out = run_git(["push"], folder)
        if not ok:
            raise Exception(f"git push 失敗:\n{out}")

        messagebox.showinfo("完了", "更新が完了しました！")

    except Exception as e:
        messagebox.showerror("エラー", str(e))

if __name__ == "__main__":
    main()