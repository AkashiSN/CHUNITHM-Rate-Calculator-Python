// 楽曲情報を追加するAPI
// 引数
// {
//   musicData : [{
//     id    : int     楽曲ID
//     name  : string  楽曲名
//     level : [{
//       constant : double  譜面定数
//       checked  : bool    検証済み
//     }]
//     imagePath  : string  画像パス
//   }]
// }

function addMusicData(args) {
  var requestDate = new Date();
  var added = args.musicData
  .filter(function(d) { return !containsMusicData(d.id); })
  .map(function(d) { return convertToRowData(d, requestDate); });
  
  if (!added || added.length == 0) {
    return;
  }
  
  var nextRow = musicDataSheet.getLastRow() + 1;
  var rowLength = added.length;
  var columnLength = 13;
  
  musicDataSheet.getRange(nextRow, 1, rowLength, columnLength).setValues(added);
  musicDataValue = musicDataSheet.getRange(2, 1, rowLength, columnLength).getValues();
}

// 楽曲情報の重複チェック
function containsMusicData(id) {
  if (!musicDataValue || musicDataValue.length == 0) {
    return false;
  }
  
  for (var i = 0; i < musicDataValue.length; i++) {
    if (musicDataValue[i][0] == id) {
      return true;
    }
  }
  
  return false;
}

// データフォーマット
function convertToRowData(data, requestDate) {
  var result = new Array();
  result.push(data.id);
  result.push("=\"" + data.name + "\"");
  result.push(data.level[0].constant);
  result.push(data.level[1].constant);
  result.push(data.level[2].constant);
  result.push(data.level[3].constant);
  result.push(data.level[0].checked ? data.level[0].checked : false);
  result.push(data.level[1].checked ? data.level[1].checked : false);
  result.push(data.level[2].checked ? data.level[2].checked : false);
  result.push(data.level[3].checked ? data.level[3].checked : false);
  result.push(data.imagePath ? data.imagePath : "");
  result.push(requestDate);
  result.push(requestDate);
  return result;
}