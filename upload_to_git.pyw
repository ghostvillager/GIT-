# upload_to_git.pyw
import sys
import os
import shutil
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

    root = tk.Tk()
    root.withdraw()

    url = simpledialog.askstring(
        "Gitリポジトリにアップロード",
        "リモートリポジトリのURLを入力してください:\n(例: https://github.com/user/repo.git)",
        parent=root
    )
    if not url:
        return
    url = url.strip()

    if not messagebox.askyesno("確認", f"以下のフォルダをアップロードしますか？\n\n{folder}\n\n→ {url}"):
        return

    try:
        is_repo, _ = run_git(["rev-parse", "--is-inside-work-tree"], folder)

        if not is_repo:
            ok, out = run_git(["init"], folder)
            if not ok:
                raise Exception(f"git init 失敗:\n{out}")
            run_git(["branch", "-M", "main"], folder)

        # remote を付け直す
        run_git(["remote", "remove", "origin"], folder)
        ok, out = run_git(["remote", "add", "origin", url], folder)
        if not ok:
            raise Exception(f"remote add 失敗:\n{out}")

        ok, out = run_git(["add", "."], folder)
        if not ok:
            raise Exception(f"git add 失敗:\n{out}")

        ok, out = run_git(["status", "--porcelain"], folder)
        if out.strip():
            ok, out = run_git(["commit", "-m", "Initial upload"], folder)
            if not ok:
                raise Exception(f"git commit 失敗:\n{out}")

        ok, out = run_git(["push", "-u", "origin", "main"], folder)
        if not ok:
            ok2, out2 = run_git(["push", "-u", "origin", "master"], folder)
            if not ok2:
                raise Exception(f"git push 失敗:\n{out}\n{out2}")

        # ===== ここから：更新用pywを自動配置 =====
        update_name = "Github更新.pyw"
        dest_path = os.path.join(folder, update_name)

        # 既にある場合はスキップ
        if not os.path.isfile(dest_path):
            # このスクリプトと同じ場所にある更新用を探す
            here = os.path.dirname(os.path.abspath(__file__))
            src_path = os.path.join(here, update_name)

            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
            else:
                # 見つからない場合は埋め込みで作成
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(UPDATE_SCRIPT)

        messagebox.showinfo("完了", "アップロードが完了しました！\n\nこのフォルダに「Github更新.pyw」を配置しました。\n次回からはそれをダブルクリックで更新できます。")

    except Exception as e:
        messagebox.showerror("エラー", str(e))

# 更新用スクリプトの中身（埋め込み）
UPDATE_SCRIPT = r'''# Github更新.pyw
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
    # このpywが置いてあるフォルダを対象にする（日本語パス対応）
    folder = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(folder):
        messagebox.showerror("エラー", f"フォルダが存在しません:\n{folder}")
        return

    ok, _ = run_git(["rev-parse", "--is-inside-work-tree"], folder)
    if not ok:
        messagebox.showerror("エラー", "このフォルダはGitリポジトリではありません")
        return

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
    if msg is None:
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
'''

if __name__ == "__main__":
    main()