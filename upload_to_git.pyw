# upload_to_git.pyw
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
        messagebox.showerror("エラー", "フォルダパスが渡されていません")
        return

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        messagebox.showerror("エラー", f"フォルダが存在しません:\n{folder}")
        return

    # URL入力
    root = tk.Tk()
    root.withdraw()  # メインウィンドウ非表示

    url = simpledialog.askstring(
        "Gitリポジトリにアップロード",
        "リモートリポジトリのURLを入力してください:\n(例: https://github.com/user/repo.git)",
        parent=root
    )

    if not url:
        return

    url = url.strip()

    # 確認
    if not messagebox.askyesno("確認", f"以下のフォルダをアップロードしますか？\n\n{folder}\n\n→ {url}"):
        return

    try:
        # すでにgitリポジトリか確認
        is_repo, _ = run_git(["rev-parse", "--is-inside-work-tree"], folder)

        if not is_repo:
            ok, out = run_git(["init"], folder)
            if not ok:
                raise Exception(f"git init 失敗:\n{out}")

            ok, out = run_git(["branch", "-M", "main"], folder)

        # remote追加（既にある場合は上書き）
        run_git(["remote", "remove", "origin"], folder)  # 既存があれば削除
        ok, out = run_git(["remote", "add", "origin", url], folder)
        if not ok:
            raise Exception(f"remote add 失敗:\n{out}")

        # 全部追加
        ok, out = run_git(["add", "."], folder)
        if not ok:
            raise Exception(f"git add 失敗:\n{out}")

        # コミット（変更がない場合はスキップ）
        ok, out = run_git(["status", "--porcelain"], folder)
        if out.strip():
            ok, out = run_git(["commit", "-m", "Initial upload"], folder)
            if not ok:
                raise Exception(f"git commit 失敗:\n{out}")

        # push
        ok, out = run_git(["push", "-u", "origin", "main"], folder)
        if not ok:
            # mainで失敗したらmasterを試す
            ok2, out2 = run_git(["push", "-u", "origin", "master"], folder)
            if not ok2:
                raise Exception(f"git push 失敗:\n{out}\n{out2}")

        messagebox.showinfo("完了", "アップロードが完了しました！")

    except Exception as e:
        messagebox.showerror("エラー", str(e))

if __name__ == "__main__":
    main()