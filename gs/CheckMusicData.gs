// 楽曲一覧表に存在しない楽曲を取得するAPI
// 引数
// {
//   id  : int[]  楽曲ID
// ]

function checkMusicData(args) {
  if (!musicDataValue || musicDataValue.length == 0) {
    return args;
  }
  
  var result = new Array();
  var id = args.id;
  var list = musicDataValue.map(function (m) { return m[0]; });
  for (var i = 0; i < id.length; i++) {
    if (!underscoreGS._contains(list, id[i])) {
      result.push(id[i]);
    }
  }
  
  return result;
}
