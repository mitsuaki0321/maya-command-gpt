# maya-command-gpt ( WIP )

GPTs から Maya へコマンドを送信するための簡単なテスト。


## 概要

GPTs から Maya へコマンドを送信します。  
あくまでテストのためセキュリティなどの部分は考えていません。

テスト内容としては、ローカルでサーバーを起動しそれを ngrok などのサービスで外部公開し GPTs の Actions からコマンドを Maya へ送信します。


## 更新予定

* 現在ローカルのサーバーでない場合使用できない設計なので、効果がありそうだったらネットワーク上のサーバーでも機能するように修正する。
* 使用してみて、コマンド以外もやり取りできるかどうかのテストによる部分。


## インストール方法

リポジトリをクローンし、Maya のから参照できるパス ( PYTHONPATH ) にリポジトリの親ディレクトリを追加してください。

クローンしたリポジトリをカレントディレクトリにして、venv など仮想環境を構築し、以下のコマンドで必要ライブラリをインストールしてください。

```shell
pip install -r requirements.txt 
```

## 使用方法

### config.ini を設定する

まず、`/ config.ini` を設定します。  
値はそれぞれ以下のような意味があります。

`url`  
GPTs と通信するための URL です。

`maya_port`  
Maya と通信するためのポート番号です。  
デフォルトは、7001 番を設定しています。

`python`  
コマンドを Maya へ送信した際、そのコマンドが保存されます。  
その保存先になります。

`result`  
コマンドの戻り値を保存します。  
その保存先になります。

### コマンドを送信する

Maya を起動しでコマンドを受信するポートを開きます。  
Maya の ScriptEditor 上でコマンドを実行してポートを開いてください。

```python

# ポートを開く
import [PackageName].maya.maya_settings
[PackageName].maya.maya_settings.open_port()

# 閉じる場合は、以下のコマンドを実行
import [PackageName].maya.maya_settings
[PackageName].maya.maya_settings.close_port()

```

ローカルのサーバーを起動します。  
クローンしたリポジトリをカレントディレクトリにして以下のコマンドを実行してください。  
[ ポート番号 ] は、Maya で使用した番号以外を使用してください。

```shell

uvicorn [PackageName].main:app --reload --port [ポート番号]

```

この状態で、/maya/sendCommand パスに POST でリクエストすると Maya にコマンドを送信します。


### 送信するコマンドの仕様

送信するコマンドは、main 関数が存在する必要があります。  
戻り値は、記述すればそれをレスポンスとして受け取れます。

```python
# リクエスト例

import json
import request

url = '[URL]/maya/sendCommand'
command = """
import maya.cmds as cmds

def main():
    return cmds.createNode('joint')

"""
data = {'command': command, file_name='foo'}
res = request.post(url, data=json.dumps(data))

if res.status_code == 200:
    print(res.json())    
```

### GPTs からのリクエスト

GPTs でリクエストを送るためには、ngrok などのサービスを使用しローカルで起動しているサーバーを外部に公開する必要があります。  
GPTs 側の Actions の設定には、`/ shema.json` を使用します。
