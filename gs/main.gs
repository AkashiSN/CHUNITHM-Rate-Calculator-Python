var Version = 16;
function doPost(e) {
  outputLog([e.parameter.data], true);
  var data = JSON.parse(e.parameter.data);
  var result = new Object();
  switch(data.api)
  {
      // 楽曲一覧表に存在しない楽曲を取得するAPI
    case "check_music_data":
      result = checkMusicData(data.args);
      break;
      
      // 楽曲情報を追加するAPI
    case "add_music_data":
      result = addMusicData(data.args);
      break;
      
      // 楽曲情報を変更するAPI
    case "modify_music_data":
      break;
      
      // 楽曲情報を取得するAPI
    case "get_music_data":
      break;
      
      // プレイ履歴を提供してもらうAPI
    case "offer_playlog":
      //      result = offerPlaylog(data.args);
      break;
      
      // プレイヤーデータを管理するAPI
    case "manage_history":
      result = manageHistory(data.args);
      break;
  }
  
  var response = { api:data.api, ver:Version, result:result };
  outputLog([response.api, "result", JSON.stringify(response.result)]);
  return ContentService.createTextOutput(JSON.stringify(response)).setMimeType(ContentService.MimeType.JSON);
}