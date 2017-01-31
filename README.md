# CHUNITHM-Rate-Calculator-Python

## 概要
CHUNITHM[©SEGA]のレート解析ツールCHUNITHM-Rate-CalculatorのPython版です。

## 注意
**非公式です。**

**あくまで自己責任で使用してください。このツールを使用したことで起こったトラブルに制作者は責任を持ちません**


## 使い方

```javascript
javascript:(function(){
    if (!location.href.match(/^https:\/\/chunithm-net.com/)) {
        alert("CHUNITHM NETを開いた状態でしてください");
        throw Error();
    }
    window.name = 'CHUNITHM ■ CHUNITHM-NET';
    var html = '<form method="post" action="https://chunical.net/chunithm.api" id="postjump" target=_brunk style="display: none;"><input type="hidden" name="userid" value="' + document.cookie + '" ></form>';
    $("body").append(html);
    $('#postjump').submit();
    $('#postjump').remove();
})(document);
```

- このコードをブックマークレットに登録
- チュウニズムネットにログインした状態でブックマークレットを実行する

詳しくは [https://chunical.net/](https://chunical.net/)


## インストール

```bash
$ apt install python3-dev python3-pip
$ pip3 install Flask
$ apt install apache2
$ apt install libapache2-mod-wsgi-py3
$ cd /var/www/
$ git clone https://github.com/AkashiSN/CHUNITHM-Rate-Calculator-Python.git
$ chown -R www-data:www-data /var/www/CHUNITHM-Rate-Calculator-Python/
$ cd CHUNITHM-Rate-Calculator-Python
$ mv flask.conf /etc/apache2/sites-available/
$ ln -s /etc/apache2/sites-available/flask.conf /etc/apache2/sites-enabled/flask.conf
$ rm /etc/apache2/sites-enabled/000-default.conf 
$ apachectl restart
```

## ライセンス
This software is released under the MIT License, see LICENSE.txt.
