"""Nếu trong máy có 2 tài khoản git online là x và local là y

Nếu push lên x thì x sẽ denied y

vì vậy phải xoá 1 thằng local y đi. Cách xoá: vào credential manager -> window credential manager -> xóa credential của y đi
# Sau đó push lên x thì sẽ yêu cầu nhập lại tài khoản và mật khẩu của x

nếu đã add và commit bằng y rồi thì phải xóa cache của y đi bằng lệnh sau:
git credential-cache exit

hoặc git pull --rebase origin main

sau đó push lại bình thường
"""