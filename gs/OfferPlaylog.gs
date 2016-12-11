// プレイ履歴を提供してもらうAPI
// 引数
// {
//   friendCode   : string  フレンドコード
//   displayRate  : double  表示レート
//   bestRate     : double  Best値
//   log : [{      
//     musicName  : string  楽曲名
//     levelName  : string  難易度(ex. "expert")
//     score      : int     スコア
//   }]
// }
function offerPlaylog(args) {
  var data = new Array();
  var row = offerPlaylogSheets[0].getLastRow();
  var offerUserId = "anonymous";
  var requestDate = new Date();
  
  if (args.friendCode != undefined) {
    var hash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, args.friendCode);
    offerUserId = bytes_to_hex_string(hash);
  }
  
  data.push(row);
  data.push(offerUserId);
  data.push(requestDate);
  data.push(args.displayRate);
  data.push(args.bestRate);
  
  outputLog([JSON.stringify(args.log), args.log.length]);
  
  var log = args.log;
  for (var i = 0; i < log.length; i++) {
    if (log[i].levelName != "worldsend") {
      data.push(getMusicData(log[i]));
      data.push(log[i].score);
    }
  }
  
  offerPlaylogSheets[0].appendRow(data);
}

function getMusicData(data) {
  if (!musicDataValue || musicDataValue.length == 0) {
    return 0;
  }
  
  var level = levelNameToLevelMap[data.levelName];
  var result = 0;
  for (var i = 0; i < musicDataValue.length; i++) {
    if (musicDataValue[i][1] == data.musicName) {
      result = musicDataValue[i][level+2];
    }
  }
  
  return result;
}