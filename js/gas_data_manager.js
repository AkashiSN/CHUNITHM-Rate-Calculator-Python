// CHUNITHM DataManager(仮) API 一覧
// gas_check_music_data : 楽曲情報の更新チェック
// gas_add_music_data   : 楽曲情報の追加
// gas_offer_playlog    : プレイ履歴の提供
// gas_manage_history   : プレイ履歴の管理

var GAS_URL = "https://script.google.com/macros/s/AKfycbwIZBMFc514Ye7WdAx-fwvAHodJelFtF4vZyV67eyqZ6pX9F4o/exec";
// GASのAPIを呼び出す際に使用するメソッド
function gas_request_api(api_name, args, callback, errorback) {
    var req_data = { api: api_name, args: args };

    $.ajax(GAS_URL, {
        type: "post",
        data: "data=" + JSON.stringify(req_data),
        dataType: "json",
        scriptCharset: "UTF-8"
    }).done(function (data) {
        if (!data) return errorback && errorback(id);
        callback && callback(data);
    }).fail(function (id) {
        errorback && errorback(id);
    });
}